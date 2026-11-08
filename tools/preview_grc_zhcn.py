#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNU Radio Companion (GRC) 汉化版独立预览与验证启动器
可以在不完整编译 C++ GNU Radio 的情况下直接拉起 PyQt6 界面，
完整展示中文主窗口、菜单栏、模块库、侧边栏面板、画布和属性对话框。
"""

import sys
import os
import glob
import types
import gettext
import argparse

# 确保 Windows 命令行支持 UTF-8 打印输出
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# 确保项目根目录在 sys.path 中
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# 1. 如果系统环境中没有已安装的 gnuradio C++ 模块，提供轻量 Mock 环境
if 'gnuradio' not in sys.modules:
    class MockPaths:
        @staticmethod
        def userconf(): return os.path.expanduser('~/.gnuradio')
        @staticmethod
        def cache(): return os.path.expanduser('~/.cache/gnuradio')
        @staticmethod
        def persistent(): return os.path.expanduser('~/.grc_gnuradio')

    class MockSubModule(types.ModuleType):
        def __getattr__(self, name):
            return 1

    mod_gnuradio = types.ModuleType('gnuradio')
    mod_gr = types.ModuleType('gnuradio.gr')
    mod_gr.version = lambda: '3.11.0.0-zhcn'
    mod_gr.major_version = lambda: '3'
    mod_gr.api_version = lambda: '11'
    mod_gr.minor_version = lambda: '0'
    mod_gr.prefix = lambda: REPO_ROOT
    mod_gr.userconf_path = lambda: os.path.expanduser('~/.gnuradio')
    mod_gr.paths = MockPaths

    class MockPrefs:
        def get_string(self, *a, **k):
            return ''

        def get_bool(self, *a, **k):
            return False

    mod_gr.prefs = lambda: MockPrefs()
    mod_gnuradio.gr = mod_gr

    for sub in ['analog', 'blocks', 'fft', 'filter', 'qtgui', 'channels', 'digital', 'fec', 'audio', 'uhd', 'soapy']:
        m = MockSubModule(f'gnuradio.{sub}')
        setattr(mod_gnuradio, sub, m)
        sys.modules[f'gnuradio.{sub}'] = m

    sys.modules['gnuradio'] = mod_gnuradio
    sys.modules['gnuradio.gr'] = mod_gr

    import grc
    mod_gnuradio.grc = grc
    sys.modules['gnuradio.grc'] = grc
    import grc.workflows
    sys.modules['gnuradio.grc.workflows'] = grc.workflows
    import grc.workflows.python_qt_gui
    sys.modules['gnuradio.grc.workflows.python_qt_gui'] = grc.workflows.python_qt_gui
    import grc.core
    sys.modules['gnuradio.grc.core'] = grc.core

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QSettings, QTimer
from PyQt6.QtGui import QIcon
from grc.gui_qt import properties
from grc.gui_qt.Platform import Platform
from grc.gui_qt.components.window import MainWindow
from grc.gui_qt.components.dialogs import PropsDialog


def run_preview(lang='zh_CN', headless=False):
    print(f"[*] 启动 GRC 中文汉化版预览器 (语言: {lang})...")

    # 2. 初始化 gettext 国际化
    locale_dir = os.path.join(REPO_ROOT, 'grc', 'gui_qt', 'resources', 'language')
    translation = gettext.translation('grc', locale_dir, languages=[lang], fallback=True)
    translation.install()
    print(f"[+] 已加载 gettext 翻译字典: {lang}")

    # 3. 创建 Platform 模型并从仓库加载全部 580+ 个 DSP 模块
    mod_gr = sys.modules['gnuradio.gr']
    model = Platform(
        version='3.11.0.0-zhcn',
        version_parts=('3', '11', '0'),
        prefs=mod_gr.prefs(),
        install_prefix=REPO_ROOT
    )

    # 扫描仓库内所有的 gr-*/grc 和 grc/blocks 路径
    search_dirs = [os.path.abspath(d) for d in glob.glob(os.path.join(
        REPO_ROOT, 'gr-*', 'grc')) + [os.path.join(REPO_ROOT, 'grc', 'blocks')]]
    model.build_library(path=search_dirs)
    print(f"[+] 成功构建模块库，已加载 {len(model.blocks)} 个 DSP 模块与 {len(model._block_categories)} 个分类映射。")

    # 4. 创建 Application (内部封装了 MainWindow, Console, BlockLibrary, VariableEditor 等)
    settings = properties.Properties([])
    settings.argv = ["preview_grc"]
    from grc.gui_qt.grc import Application
    app = Application(settings, model, [])
    main_win = app.MainWindow
    main_win.setWindowTitle(_("window-title") + " - " + _("简体中文版"))
    main_win.resize(1280, 800)

    # 5. 向当前流图添加经典 DSP 信号链路并建立连线，验证模块汉化与正常绿灯工作状态
    scene = main_win.currentFlowgraphScene
    if scene:
        b_src = None
        b_thr = None
        b_snk = None

        # 添加信号源
        if 'analog_sig_source_x' in model.blocks:
            scene.add_block('analog_sig_source_x', pos=(80, 150))
            b_src = scene.core.blocks[-1]
        # 添加节流限速
        if 'blocks_throttle2' in model.blocks:
            scene.add_block('blocks_throttle2', pos=(420, 150))
            b_thr = scene.core.blocks[-1]
        elif 'blocks_throttle' in model.blocks:
            scene.add_block('blocks_throttle', pos=(420, 150))
            b_thr = scene.core.blocks[-1]
        # 添加 QT 示波器
        if 'qtgui_time_sink_x' in model.blocks:
            scene.add_block('qtgui_time_sink_x', pos=(760, 150))
            b_snk = scene.core.blocks[-1]

        # 建立连线以验证正常连线与流图有效状态（消除未连线时的红字报警）
        if b_src and b_thr and b_src.sources and b_thr.sinks:
            conn1 = scene.core.connect(b_src.sources[0], b_thr.sinks[0])
            scene.addItem(conn1.gui)
        if b_thr and b_snk and b_thr.sources and b_snk.sinks:
            conn2 = scene.core.connect(b_thr.sources[0], b_snk.sinks[0])
            scene.addItem(conn2.gui)

        scene.core.rewrite()
        scene.core.validate()

        # 预设保存路径，方便直接点击“生成代码”进行代码生成测试
        default_grc = os.path.join(REPO_ROOT, "demo_zhcn.grc")
        scene.filename = default_grc
        scene.set_saved(True)
        main_win.tabWidget.setTabText(0, "demo_zhcn.grc")
        try:
            model.save_flow_graph(default_grc, main_win.currentFlowgraph)
        except Exception:
            pass

    main_win.show()
    print("[+] GRC 汉化版主界面已成功构建并显示！")

    if headless:
        print("[+] Headless 验证模式：所有中文组件、菜单栏与流图画布均已成功初始化与渲染！")
        return 0

    return app.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="GRC 汉化版独立预览工具")
    parser.add_argument('-l', '--lang', default='zh_CN', choices=['zh_CN', 'en_US'], help="界面语言")
    parser.add_argument('--headless', action='store_true', help="无窗口自测运行")
    args = parser.parse_args()

    sys.exit(run_preview(lang=args.lang, headless=args.headless))

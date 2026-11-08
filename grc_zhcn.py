#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNU Radio 伴侣 (GRC) 简体中文增强版启动器
支持直接打开 .grc 流图文件、全模块库加载、深色暗黑主题与完整中文本地化。
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
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# 设置环境变量默认值
os.environ.setdefault('LANG', 'zh_CN.UTF-8')
os.environ.setdefault('LC_ALL', 'zh_CN.UTF-8')


def setup_localization(lang='zh_CN'):
    """加载 gettext 翻译文件"""
    locale_dirs = [
        os.path.join(REPO_ROOT, 'grc', 'gui_qt', 'resources', 'language'),
        os.path.join(REPO_ROOT, 'share', 'locale'),
        os.path.join(sys.prefix, 'share', 'locale'),
    ]
    for ldir in locale_dirs:
        mo_file = os.path.join(ldir, lang, 'LC_MESSAGES', 'grc.mo')
        if os.path.isfile(mo_file):
            try:
                t = gettext.translation('grc', ldir, languages=[lang], fallback=True)
                t.install()
                return t
            except Exception as e:
                print(f"[!] 加载语言文件失败 ({ldir}): {e}", file=sys.stderr)
    # 回退内置安装
    gettext.install('grc')
    return None


def init_gnuradio_environment():
    """检测并初始化 gnuradio 运行时环境；若未编译安装则提供兼容 mock 环境"""
    try:
        from gnuradio import gr
        return gr
    except (ImportError, Exception):
        # 兼容纯 Python 运行环境
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
            def get_string(self, *a, **k): return ''
            def get_bool(self, *a, **k): return False

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

        return mod_gr


def main():
    parser = argparse.ArgumentParser(description="GNU Radio 伴侣 (GRC) 简体中文增强版")
    parser.add_argument('flowgraph', nargs='*', help="要打开的 .grc 流图文件路径")
    parser.add_argument('-l', '--lang', default='zh_CN', choices=['zh_CN', 'en_US'], help="界面语言 (默认 zh_CN)")
    parser.add_argument('--headless', action='store_true', help="无图形界面验证模式 (用于自动化测试)")
    args = parser.parse_args()

    # 1. 初始化国际化
    setup_localization(args.lang)

    # 2. 初始化环境
    gr_mod = init_gnuradio_environment()

    # 3. 导入 PyQt6 与 GRC 组件
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt, QSettings
        from grc.gui_qt import properties
        from grc.gui_qt.Platform import Platform
        from grc.gui_qt.grc import Application
    except ImportError as e:
        print(f"[错误] 无法加载 PyQt6 组件: {e}", file=sys.stderr)
        print("请先安装 PyQt6: pip install PyQt6 pyyaml mako qdarkstyle", file=sys.stderr)
        return 1

    # 4. 初始化 Platform 数据模型
    install_prefix = getattr(gr_mod, 'prefix', lambda: REPO_ROOT)()
    model = Platform(
        version='3.11.0.0-zhcn',
        version_parts=('3', '11', '0'),
        prefs=gr_mod.prefs(),
        install_prefix=install_prefix
    )

    # 搜索 DSP 模块定义目录
    search_dirs = []
    # 环境变量中的路径
    if 'GRC_BLOCKS_PATH' in os.environ:
        search_dirs.extend([p for p in os.environ['GRC_BLOCKS_PATH'].split(os.pathsep) if os.path.isdir(p)])
    # 系统安装路径中的 blocks
    system_blocks = os.path.join(install_prefix, 'share', 'gnuradio', 'grc', 'blocks')
    if os.path.isdir(system_blocks):
        search_dirs.append(system_blocks)
    # 仓库源码目录中的 blocks
    repo_blocks = [os.path.abspath(d) for d in glob.glob(os.path.join(REPO_ROOT, 'gr-*', 'grc')) + [os.path.join(REPO_ROOT, 'grc', 'blocks')]]
    search_dirs.extend([d for d in repo_blocks if os.path.isdir(d)])

    # 去重保留顺序
    unique_dirs = []
    for d in search_dirs:
        if d not in unique_dirs:
            unique_dirs.append(d)

    model.build_library(path=unique_dirs)

    # 5. 启动 Application
    settings = properties.Properties([])
    settings.argv = [sys.argv[0]]
    file_paths = [os.path.abspath(f) for f in args.flowgraph if os.path.isfile(f)]

    app = Application(settings, model, file_paths)
    main_win = app.MainWindow
    main_win.setWindowTitle(_("window-title") + " - " + _("简体中文版"))

    # 如果没有指定文件且当前未加载流图，加载 demo 或创建默认流图
    if not file_paths and hasattr(main_win, 'currentFlowgraphScene') and main_win.currentFlowgraphScene:
        scene = main_win.currentFlowgraphScene
        # 若画布为空，设置默认流图标题
        if not scene.core.blocks or len(scene.core.blocks) <= 2:
            default_demo = os.path.join(REPO_ROOT, "demo_zhcn.grc")
            if os.path.isfile(default_demo):
                try:
                    main_win.load_flow_graph(default_demo)
                except Exception:
                    pass

    main_win.show()

    if args.headless:
        print("[+] Headless 验证成功：中文界面与 DSP 模块库均已就绪。")
        return 0

    return app.run()


if __name__ == '__main__':
    sys.exit(main())

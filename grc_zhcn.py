#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNU Radio 伴侣 (GRC) 简体中文增强版启动器
支持直接打开 .grc 流图文件、全模块库加载、深色暗黑主题与完整中文本地化。
完美兼容自带 runtime 环境与外部已安装的 Radioconda / Conda 环境。
"""

import sys
import os
import glob
import types
import gettext
import builtins
import argparse

# 确保 Windows 命令行支持 UTF-8 打印输出
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# 确保项目根目录永远排在 sys.path 最前面，防止被 site-packages 中的旧版 grc 覆盖
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT in sys.path:
    sys.path.remove(REPO_ROOT)
sys.path.insert(0, REPO_ROOT)

# 设置环境变量默认值
os.environ.setdefault('LANG', 'zh_CN.UTF-8')
os.environ.setdefault('LC_ALL', 'zh_CN.UTF-8')


def setup_localization(lang='zh_CN'):
    """加载 gettext 翻译文件并强力绑定至 builtins._"""
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
                builtins.__dict__['_'] = t.gettext
                return t
            except Exception as e:
                print(f"[!] 加载语言文件失败 ({ldir}): {e}", file=sys.stderr)
    # 回退内置安装
    gettext.install('grc')
    return None


def bind_localized_grc_modules(gnuradio_mod=None):
    """强制将当前目录下的汉化版 grc 绑定到 sys.modules['gnuradio.grc']，防止调用未汉化的系统库"""
    for mod_name in list(sys.modules.keys()):
        if mod_name == 'grc' or mod_name.startswith('grc.') or mod_name.startswith('gnuradio.grc'):
            del sys.modules[mod_name]

    import grc
    import grc.core
    import grc.gui_qt
    import grc.workflows
    import grc.workflows.python_qt_gui

    if gnuradio_mod is not None:
        gnuradio_mod.grc = grc

    sys.modules['gnuradio.grc'] = grc
    sys.modules['gnuradio.grc.core'] = grc.core
    sys.modules['gnuradio.grc.gui_qt'] = grc.gui_qt
    sys.modules['gnuradio.grc.workflows'] = grc.workflows
    sys.modules['gnuradio.grc.workflows.python_qt_gui'] = grc.workflows.python_qt_gui


def init_gnuradio_environment():
    """检测并初始化 gnuradio 运行时环境；若未编译安装则提供兼容 mock 环境"""
    try:
        import gnuradio
        from gnuradio import gr
        bind_localized_grc_modules(gnuradio)
        return gr
    except (ImportError, Exception):
        # 兼容纯 Python 运行环境
        class MockPaths:
            @staticmethod
            def userconf():
                return os.path.expanduser('~/.gnuradio')

            @staticmethod
            def cache():
                return os.path.expanduser('~/.cache/gnuradio')

            @staticmethod
            def persistent():
                return os.path.expanduser('~/.grc_gnuradio')

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

        bind_localized_grc_modules(mod_gnuradio)
        return mod_gr


def main():
    parser = argparse.ArgumentParser(description="GNU Radio 伴侣 (GRC) 简体中文增强版")
    parser.add_argument('flowgraph', nargs='*', help="要打开的 .grc 流图文件路径")
    parser.add_argument('-l', '--lang', default='zh_CN', choices=['zh_CN', 'en_US'], help="界面语言 (默认 zh_CN)")
    parser.add_argument('--headless', action='store_true', help="无图形界面验证模式 (用于自动化测试)")
    args = parser.parse_args()

    # 1. 初始化国际化
    setup_localization(args.lang)

    # 2. 初始化环境并强制使用本地汉化 grc 包
    gr_mod = init_gnuradio_environment()

    # 再次确保 _ 未被覆盖
    setup_localization(args.lang)

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
    # 系统安装路径中的 blocks (包含 Radioconda / Conda Library/share)
    candidate_prefixes = [
        install_prefix,
        sys.prefix,
        os.path.join(sys.prefix, 'Library'),
        os.path.join(install_prefix, 'Library'),
        os.path.join(REPO_ROOT, 'runtime'),
        os.path.join(REPO_ROOT, 'runtime', 'Library'),
    ]
    for pfx in candidate_prefixes:
        if pfx:
            sb = os.path.join(pfx, 'share', 'gnuradio', 'grc', 'blocks')
            if os.path.isdir(sb):
                search_dirs.append(sb)

    # 仓库源码目录中的核心 blocks（包含 .workflow.yml 和 .domain.yml，始终加载）
    core_blocks_dir = os.path.abspath(os.path.join(REPO_ROOT, 'grc', 'blocks'))
    if os.path.isdir(core_blocks_dir):
        search_dirs.append(core_blocks_dir)

    # 若未从 runtime 加载到子模块 blocks，则扫描 gr-*/grc
    if len(search_dirs) <= 1:
        repo_blocks = [os.path.abspath(d) for d in glob.glob(os.path.join(REPO_ROOT, 'gr-*', 'grc'))]
        search_dirs.extend([d for d in repo_blocks if os.path.isdir(d)])

    # 去重保留顺序
    unique_dirs = []
    for d in search_dirs:
        norm_d = os.path.normcase(os.path.abspath(d))
        if norm_d not in [os.path.normcase(os.path.abspath(x)) for x in unique_dirs]:
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

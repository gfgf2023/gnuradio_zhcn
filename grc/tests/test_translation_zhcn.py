# -*- coding: utf-8 -*-
"""
自动化测试：验证 GRC 简体中文 (zh_CN) 汉化语言包及国际化架构
"""

import os
import sys
import gettext
import re
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS_DIR = os.path.join(REPO_ROOT, 'tools')
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from compile_po import parse_po, compile_po_to_mo


@pytest.fixture(scope="session")
def locale_setup():
    po_path = os.path.join(REPO_ROOT, 'grc', 'gui_qt', 'resources', 'language', 'zh_CN', 'LC_MESSAGES', 'grc.po')
    mo_path = os.path.join(REPO_ROOT, 'grc', 'gui_qt', 'resources', 'language', 'zh_CN', 'LC_MESSAGES', 'grc.mo')

    # 确保编译最新 mo 文件
    assert os.path.exists(po_path), f"PO 文件不存在: {po_path}"
    compile_po_to_mo(po_path, mo_path)
    assert os.path.exists(mo_path), f"MO 文件生成失败: {mo_path}"

    locale_dir = os.path.join(REPO_ROOT, 'grc', 'gui_qt', 'resources', 'language')
    tr = gettext.translation('grc', locale_dir, languages=['zh_CN'], fallback=False)

    translations_dict = parse_po(po_path)
    return {
        'po_path': po_path,
        'mo_path': mo_path,
        'tr': tr,
        'dict': translations_dict
    }


def test_mo_file_compilation(locale_setup):
    """测试 PO -> MO 编译完整度与条目数量"""
    translations = locale_setup['dict']
    assert len(translations) >= 900, f"翻译条目过少 ({len(translations)} 项)，预期至少 900 项"


def test_gettext_loads_zh_cn(locale_setup):
    """测试 Python gettext 能正确载入 zh_CN 语言环境"""
    tr = locale_setup['tr']
    assert type(tr) != gettext.NullTranslations, "gettext 未能正确载入 zh_CN 字典"
    assert tr.gettext('save') != 'save'


def test_menus_and_ui_translated(locale_setup):
    """测试主窗口顶级菜单及关键 UI 标签汉化完整性"""
    tr = locale_setup['tr']
    core_ui_keys = [
        '&File', '&Edit', '&View', '&Build', '&Tools', '&Help', '&Console',
        'window-title', 'save', 'open', 'close', 'undo', 'redo', 'cut', 'copy', 'paste',
        'Block Library', 'Console', 'Variable Editor', 'Errors and Warnings', 'GRC Preferences'
    ]
    for key in core_ui_keys:
        val = tr.gettext(key)
        assert val != key, f"UI 核心项未翻译: {key}"
        assert len(val.strip()) > 0, f"翻译值为空: {key}"


def test_block_categories_translated(locale_setup):
    """测试 DSP 模块分类目录汉化"""
    tr = locale_setup['tr']
    categories = [
        'Core', 'Variables', 'Analog', 'Audio', 'Blocks', 'Channel Models',
        'Digital Television', 'Filters', 'Fourier Analysis', 'Math Operators',
        'Modulators', 'Resamplers', 'Stream Operators', 'Synchronizers',
        'Type Converters', 'UHD', 'Soapy', 'QT'
    ]
    for cat in categories:
        val = tr.gettext(cat)
        assert val != cat, f"分类未汉化: {cat}"


def test_core_dsp_blocks_translated(locale_setup):
    """测试核心 DSP 模块标签汉化 (用户明确要求的模块汉化)"""
    tr = locale_setup['tr']
    blocks = [
        'Options', 'Variable', 'Signal Source', 'Noise Source', 'Constant Source',
        'Throttle', 'Add', 'Multiply', 'Divide', 'Subtract', 'Complex to Float',
        'Float to Complex', 'Low Pass Filter', 'High Pass Filter', 'Band Pass Filter',
        'Root Raised Cosine Filter', 'Rational Resampler', 'Constellation Modulator',
        'Symbol Sync', 'Costas Loop', 'QT GUI Time Sink', 'QT GUI Frequency Sink',
        'QT GUI Waterfall Sink', 'QT GUI Constellation Sink', 'UHD: USRP Source',
        'ATSC Deinterleaver', 'ZMQ PUB Sink', 'TCP Sink', 'IIO Device Source',
        'RFNoC FFT', 'FEC Async Decoder', 'CODEC2 Audio Decoder', 'PDU Filter',
        'Trellis Encoder', 'Polyphase Channelizer', 'GMSK Mod', 'FFT'
    ]
    for blk in blocks:
        val = tr.gettext(blk)
        assert val != blk, f"模块未汉化: {blk}"
        # 验证译文包含中文字符
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in val)
        assert has_chinese, f"模块译文不包含中文字符: {blk} -> {val}"


def test_parameters_and_options_translated(locale_setup):
    """测试常用模块参数与下拉选项汉化"""
    tr = locale_setup['tr']
    params = [
        'Sample Rate', 'Frequency', 'Gain', 'Amplitude', 'Offset',
        'Cutoff Freq', 'Transition Width', 'Decimation', 'Interpolation',
        'Waveform', 'Output Type', 'Input Type'
    ]
    for p in params:
        val = tr.gettext(p)
        assert val != p, f"参数项未汉化: {p}"

    options = [
        'Constant', 'Sine', 'Cosine', 'Square', 'Triangle', 'Saw Tooth',
        'Complex', 'Float', 'Int', 'Short', 'Byte', 'Hamming', 'Hann', 'Blackman'
    ]
    for opt in options:
        val = tr.gettext(opt)
        assert val != opt, f"参数选项未汉化: {opt}"


def test_format_placeholders_consistency(locale_setup):
    """验证翻译文本中的格式化占位符与源文本一致，杜绝运行时报错"""
    translations = locale_setup['dict']

    # 正则提取 {xxx} 命名占位符和 {} 匿名占位符
    brace_re = re.compile(r'\{[a-zA-Z0-9_]*\}')
    # 正则提取 %s, %d 等格式化符
    percent_re = re.compile(r'%[0-9.-]*[sdifxX]')

    for msgid, msgstr in translations.items():
        if not msgstr:
            continue
        id_braces = sorted(brace_re.findall(msgid))
        str_braces = sorted(brace_re.findall(msgstr))
        assert id_braces == str_braces, f"占位符不匹配: msgid '{msgid}' ({id_braces}) vs msgstr '{msgstr}' ({str_braces})"

        id_percents = sorted(percent_re.findall(msgid))
        str_percents = sorted(percent_re.findall(msgstr))
        assert id_percents == str_percents, f"%格式化符不匹配: msgid '{msgid}' vs msgstr '{msgstr}'"


def test_code_generation_module_resolution():
    """测试汉化环境下核心代码生成器模块的解析，确保不崩溃"""
    pytest.importorskip("numpy")
    from grc.core.generator.Generator import Generator
    import grc.workflows.python_qt_gui

    class MockPlatform:
        pass

    class MockFlowGraph:
        parent_platform = MockPlatform()

        def get_option(self, opt):
            if opt == 'generator_module':
                return 'gnuradio.grc.workflows.python_qt_gui'
            if opt == 'generator_class_name':
                return 'PythonQtGuiGenerator'
            if opt == 'id':
                return 'test_flowgraph'
            return ''

    # 测试通过源码前缀回退正确导入生成器类
    gen = Generator(MockFlowGraph(), output_dir='.')
    assert gen.generator_class_name == 'PythonQtGuiGenerator'
    assert gen._generator is not None

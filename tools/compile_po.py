#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pure Python PO to MO compiler.
Converts GNU gettext Portable Object (.po) files to binary Machine Object (.mo) files.
Independent of GNU gettext / msgfmt binary, works on all platforms.
"""

import sys
import os
import struct
import re

MAGIC = 0x950412de


def unescape(s):
    """Unescape standard escape sequences in PO strings."""
    escapes = {
        '\\n': '\n',
        '\\t': '\t',
        '\\r': '\r',
        '\\"': '"',
        '\\\\': '\\',
    }
    # Replace escaped sequences

    def repl(m):
        return escapes.get(m.group(0), m.group(0))
    return re.sub(r'\\[ntr"\\]', repl, s)


def parse_po(file_path):
    """
    Parse a .po file and return a dictionary of {msgid: msgstr}.
    Supports multiline strings and escaped characters.
    """
    translations = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_msgid = None
    current_msgstr = None
    state = None  # 'msgid' or 'msgstr'

    def commit():
        nonlocal current_msgid, current_msgstr
        if current_msgid is not None and current_msgstr is not None:
            translations[current_msgid] = current_msgstr
        current_msgid = None
        current_msgstr = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue

        if line.startswith('msgid '):
            commit()
            val = line[6:].strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            current_msgid = unescape(val)
            state = 'msgid'
        elif line.startswith('msgstr '):
            val = line[7:].strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            current_msgstr = unescape(val)
            state = 'msgstr'
        elif line.startswith('"') and line.endswith('"'):
            val = unescape(line[1:-1])
            if state == 'msgid' and current_msgid is not None:
                current_msgid += val
            elif state == 'msgstr' and current_msgstr is not None:
                current_msgstr += val

    commit()
    return translations


def generate_mo(translations):
    """
    Generate binary MO data from translations dictionary according to GNU gettext MO file specification.
    """
    # Sort keys for predictable output and binary search compatibility
    keys = sorted(translations.keys())

    # Encode strings to UTF-8
    orig_table = []
    trans_table = []

    # String storage begins after header and index tables
    # Header format:
    # 0:  magic (4 bytes)
    # 4:  version (4 bytes, 0)
    # 8:  num_strings (4 bytes)
    # 12: orig_table_offset (4 bytes)
    # 16: trans_table_offset (4 bytes)
    # 20: hash_table_size (4 bytes, 0)
    # 24: hash_table_offset (4 bytes, 0)
    num_strings = len(keys)
    header_size = 28
    index_size = num_strings * 8  # 4 bytes length + 4 bytes offset

    orig_table_offset = header_size
    trans_table_offset = orig_table_offset + index_size
    strings_offset = trans_table_offset + index_size

    encoded_orig = [k.encode('utf-8') + b'\x00' for k in keys]
    encoded_trans = [translations[k].encode('utf-8') + b'\x00' for k in keys]

    # Calculate offsets for string data
    current_offset = strings_offset
    orig_indices = []
    for s in encoded_orig:
        orig_indices.append((len(s) - 1, current_offset))
        current_offset += len(s)

    trans_indices = []
    for s in encoded_trans:
        trans_indices.append((len(s) - 1, current_offset))
        current_offset += len(s)

    # Assemble binary MO
    mo_data = bytearray()
    # Write header
    mo_data.extend(struct.pack('<I', MAGIC))
    mo_data.extend(struct.pack('<I', 0))  # version
    mo_data.extend(struct.pack('<I', num_strings))
    mo_data.extend(struct.pack('<I', orig_table_offset))
    mo_data.extend(struct.pack('<I', trans_table_offset))
    mo_data.extend(struct.pack('<I', 0))  # hash size
    mo_data.extend(struct.pack('<I', 0))  # hash offset

    # Write orig table (length, offset)
    for length, offset in orig_indices:
        mo_data.extend(struct.pack('<II', length, offset))

    # Write trans table (length, offset)
    for length, offset in trans_indices:
        mo_data.extend(struct.pack('<II', length, offset))

    # Write orig strings
    for s in encoded_orig:
        mo_data.extend(s)

    # Write trans strings
    for s in encoded_trans:
        mo_data.extend(s)

    return bytes(mo_data)


def compile_po_to_mo(po_path, mo_path=None):
    if mo_path is None:
        if po_path.endswith('.po'):
            mo_path = po_path[:-3] + '.mo'
        else:
            mo_path = po_path + '.mo'

    os.makedirs(os.path.dirname(os.path.abspath(mo_path)), exist_ok=True)
    translations = parse_po(po_path)
    mo_bytes = generate_mo(translations)

    with open(mo_path, 'wb') as f:
        f.write(mo_bytes)

    print(f"Successfully compiled {po_path} ({len(translations)} entries) -> {mo_path}")
    return len(translations)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # 默认寻找并编译 zh_CN 语言包
        default_po = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'grc', 'gui_qt', 'resources', 'language', 'zh_CN', 'LC_MESSAGES', 'grc.po'
        )
        if os.path.isfile(default_po):
            in_po = default_po
            out_mo = None
        else:
            print("Usage: compile_po.py <input.po> [output.mo]")
            sys.exit(1)
    else:
        in_po = sys.argv[1]
        out_mo = sys.argv[2] if len(sys.argv) > 2 else None

    compile_po_to_mo(in_po, out_mo)

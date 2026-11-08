#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GNU Radio 中文发行包打包与装配工具
支持在本地或 GitHub Actions CI 中自动化打包生成绿色便携发行版与校验码。
"""

import os
import sys
import shutil
import tarfile
import zipfile
import hashlib
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def get_sha256(filepath):
    """计算文件的 SHA256 哈希值"""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192 * 1024):
            h.update(chunk)
    return h.hexdigest()


def compile_mo():
    """编译 PO 到 MO 文件"""
    po_file = REPO_ROOT / 'grc' / 'gui_qt' / 'resources' / 'language' / 'zh_CN' / 'LC_MESSAGES' / 'grc.po'
    mo_file = REPO_ROOT / 'grc' / 'gui_qt' / 'resources' / 'language' / 'zh_CN' / 'LC_MESSAGES' / 'grc.mo'
    compile_script = REPO_ROOT / 'tools' / 'compile_po.py'

    print(f"[*] 正在编译翻译文件: {po_file} -> {mo_file}")
    import subprocess
    ret = subprocess.run([sys.executable, str(compile_script), str(po_file), str(mo_file)], capture_output=True, text=True)
    if ret.returncode != 0:
        print(f"[!] 编译 PO 文件失败: {ret.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"[+] 语言包编译成功: {mo_file.stat().st_size} 字节")


def copy_tree_filtered(src: Path, dst: Path, ignore_patterns=None):
    """复制目录树，并自动过滤缓存与临时文件"""
    if ignore_patterns is None:
        ignore_patterns = shutil.ignore_patterns(
            '__pycache__', '*.pyc', '*.pyo', '*.pyd.manifest',
            '.git*', '*.tmp', 'pkgs', 'tests', 'test', 'idlelib'
        )
    shutil.copytree(src, dst, ignore=ignore_patterns, dirs_exist_ok=True)


def package_release(target_os: str, runtime_path: Path, output_dir: Path, version: str):
    print(f"\n=======================================================")
    print(f"  开始打包 GNU Radio 简体中文增强发行版 (v{version})")
    print(f"  目标操作系统: {target_os}")
    print(f"  运行时路径: {runtime_path}")
    print(f"  输出目录: {output_dir}")
    print(f"=======================================================\n")

    # 1. 编译语言包
    compile_mo()

    # 2. 准备目录结构
    release_name = f"gnuradio-v{version}-{target_os}-x64-portable-zhCN"
    staging_dir = output_dir / release_name
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)

    runtime_dst = staging_dir / 'runtime'

    # 3. 复制 runtime 环境 (若提供)
    if runtime_path and runtime_path.exists():
        print(f"[*] 正在复制并精简运行时环境到 {runtime_dst}...")
        copy_tree_filtered(runtime_path, runtime_dst)
        print("[+] 运行时环境复制完成。")
    else:
        print(f"[!] 警告: 未找到 runtime 目录 ({runtime_path})，打包将仅包含 GRC 中文本地化代码与启动脚本。")

    # 4. 覆盖/部署中文版 grc 模块到 runtime 的 site-packages
    site_packages_candidates = []
    if target_os == 'windows':
        site_packages_candidates.append(runtime_dst / 'Lib' / 'site-packages')
    else:
        site_packages_candidates.extend(list(runtime_dst.glob('lib/python*/site-packages')))

    for sp in site_packages_candidates:
        if sp.exists():
            target_grc = sp / 'gnuradio' / 'grc'
            print(f"[*] 正在将汉化版 GRC 注入 runtime: {target_grc}")
            copy_tree_filtered(REPO_ROOT / 'grc', target_grc)

            # 拷贝 mo 文件至 runtime 的 locale 目录
            locale_dir = runtime_dst / 'share' / 'locale' / 'zh_CN' / 'LC_MESSAGES'
            locale_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(
                REPO_ROOT / 'grc' / 'gui_qt' / 'resources' / 'language' / 'zh_CN' / 'LC_MESSAGES' / 'grc.mo',
                locale_dir / 'grc.mo'
            )

    # 5. 复制根目录启动脚本与资源
    print("[*] 正在装配启动器与中文文档...")
    shutil.copy2(REPO_ROOT / 'grc_zhcn.py', staging_dir / 'grc_zhcn.py')
    shutil.copy2(REPO_ROOT / 'run_grc_zhcn.bat', staging_dir / 'run_grc_zhcn.bat')

    demo_file = REPO_ROOT / 'demo_zhcn.grc'
    if demo_file.exists():
        shutil.copy2(demo_file, staging_dir / 'demo_zhcn.grc')

    # 复制 grc 源码包至便携包根目录
    copy_tree_filtered(REPO_ROOT / 'grc', staging_dir / 'grc')

    if target_os == 'windows':
        win_pkg = REPO_ROOT / 'packaging' / 'windows'
        for f in win_pkg.iterdir():
            if f.is_file():
                shutil.copy2(f, staging_dir / f.name)
    else:
        linux_pkg = REPO_ROOT / 'packaging' / 'linux'
        for f in linux_pkg.iterdir():
            if f.is_file():
                shutil.copy2(f, staging_dir / f.name)

    # 6. 生成归档压缩包
    output_dir.mkdir(parents=True, exist_ok=True)
    if target_os == 'windows':
        archive_name = f"{release_name}.zip"
        archive_path = output_dir / archive_name
        print(f"[*] 正在压缩生成 Windows ZIP 绿色免安装包: {archive_path}")
        # 使用最高效率打包
        shutil.make_archive(str(output_dir / release_name), 'zip', str(staging_dir.parent), str(release_name))
    else:
        archive_name = f"{release_name}.tar.gz"
        archive_path = output_dir / archive_name
        print(f"[*] 正在压缩生成 Linux TAR.GZ 绿色免安装包: {archive_path}")
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(staging_dir, arcname=release_name)

    # 7. 计算 SHA256 校验码
    sha256_val = get_sha256(archive_path)
    sha_file = output_dir / "SHA256SUMS.txt"
    with open(sha_file, 'a', encoding='utf-8') as f:
        f.write(f"{sha256_val}  {archive_name}\n")

    print("\n=======================================================")
    print(f"  打包完成！")
    print(f"  安装包文件: {archive_path}")
    print(f"  文件大小: {archive_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"  SHA256: {sha256_val}")
    print("=======================================================\n")
    return archive_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="GNU Radio 中文便携发行包打包器")
    parser.add_argument('--os', choices=['windows', 'linux'], default='windows' if sys.platform == 'win32' else 'linux')
    parser.add_argument('--runtime', type=str, default='', help="Conda/Micromamba 编译导出的运行时目录路径")
    parser.add_argument('--output', type=str, default='dist', help="安装包输出目录")
    parser.add_argument('--version', type=str, default='3.11.0.0-zhcn', help="版本号 (如 3.11.0.0-zhcn)")
    args = parser.parse_args()

    rt_path = Path(args.runtime).resolve() if args.runtime else None
    out_path = Path(args.output).resolve()
    package_release(args.os, rt_path, out_path, args.version)

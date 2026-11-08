#!/usr/bin/env bash
# GNU Radio 伴侣 (GRC) 简体中文增强版 Linux 终端环境
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME="$SCRIPT_DIR/runtime"

if [ ! -d "$RUNTIME" ]; then
    echo "[错误] 未找到 runtime 运行环境目录！"
    exit 1
fi

export PATH="$RUNTIME/bin:$PATH"
export LD_LIBRARY_PATH="$RUNTIME/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="$SCRIPT_DIR:$RUNTIME/lib/python3.11/site-packages:$PYTHONPATH"
export GRC_BLOCKS_PATH="$RUNTIME/share/gnuradio/grc/blocks:$SCRIPT_DIR/grc/blocks"
export LANG="zh_CN.UTF-8"
export LC_ALL="zh_CN.UTF-8"

if [ -f "$RUNTIME/bin/activate" ]; then
    source "$RUNTIME/bin/activate" "$RUNTIME"
fi

echo "========================================================================="
echo "  GNU Radio 伴侣 (GRC) 简体中文增强版 - Linux SDR 终端环境"
echo "========================================================================="
echo "  已加载 Python, GNU Radio C++, SoapySDR, UHD 工具集"
echo "  启动命令: ./run_grc_zhcn.sh"
echo "========================================================================="
exec bash --norc

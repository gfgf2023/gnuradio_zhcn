================================================================================
GNU Radio 伴侣 (GRC) 简体中文增强发行版 - Linux 使用说明
================================================================================

一、启动方式
1. 打开终端，赋予启动脚本执行权限（若需要）：
   chmod +x run_grc_zhcn.sh sdr_terminal.sh
2. 启动图形化中文界面：
   ./run_grc_zhcn.sh
3. 启动 SDR 命令行工具箱：
   ./sdr_terminal.sh

二、USB 设备权限配置 (udev rules)
在 Linux 下免 root 使用 RTL-SDR / HackRF / PlutoSDR 等设备，建议配置 udev 规则：
sudo cp packaging/linux/99-sdr-devices.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger

三、特性
- 全功能集成 GNU Radio C++ 运行时及 Python 3.11 环境。
- 100% 汉化所有 575+ 个 DSP 模块与参数分类。
- 支持深色暗黑主题与中英双语检索。
================================================================================

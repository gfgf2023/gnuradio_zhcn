@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"

title GNU Radio 中文增强版 - SDR 命令行工具箱

if not exist "%RUNTIME%\python.exe" (
    echo [错误] 未在当前目录下找到 runtime 运行环境！
    pause
    exit /b 1
)

:: 配置独立运行环境变量
set "PATH=%RUNTIME%;%RUNTIME%\Library\bin;%RUNTIME%\Library\usr\bin;%RUNTIME%\Library\mingw-w64\bin;%RUNTIME%\Scripts;%RUNTIME%\bin;%PATH%"
set "PYTHONHOME=%RUNTIME%"
set "PYTHONPATH=%ROOT%;%RUNTIME%\Lib\site-packages"
set "GRC_BLOCKS_PATH=%RUNTIME%\share\gnuradio\grc\blocks;%ROOT%grc\blocks"
set "LANG=zh_CN.UTF-8"
set "LC_ALL=zh_CN.UTF-8"

if exist "%RUNTIME%\condabin\conda.bat" (
    call "%RUNTIME%\condabin\conda.bat" activate "%RUNTIME%" >nul 2>&1
)

echo =========================================================================
echo   GNU Radio 伴侣 (GRC) 简体中文增强版 - SDR 命令行运行环境
echo =========================================================================
echo   已加载组件:
echo     - Python 3.11 及科学计算库 (NumPy, SciPy, Matplotlib)
echo     - GNU Radio C++ 核心 DSP 库与 Qt6 GUI
echo     - SoapySDR 统一硬件驱动 (RTL-SDR, HackRF, PlutoSDR, Airspy)
echo     - UHD (USRP 硬件驱动套件)
echo     - VOLK SIMD 矢量加速指令集
echo.
echo   常用测试命令:
echo     python grc_zhcn.py         : 启动中文版 GRC 界面
echo     SoapySDRUtil --find        : 探测当前连接的所有 SDR 硬件
echo     uhd_find_devices           : 探测连接的 USRP 设备
echo     volk_profile               : 执行本机 CPU SIMD 指令调优
echo =========================================================================
echo.

cmd /k

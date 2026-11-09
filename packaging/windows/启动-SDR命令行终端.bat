@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"
set "LANG=zh_CN.UTF-8"
set "LC_ALL=zh_CN.UTF-8"
set "PYTHONIOENCODING=utf-8"

title GNU Radio 中文增强版 - SDR 命令行工具箱

if not exist "%RUNTIME%\python.exe" goto :NO_RUNTIME

set "PATH=%RUNTIME%;%RUNTIME%\Library\bin;%RUNTIME%\Library\usr\bin;%RUNTIME%\Library\mingw-w64\bin;%RUNTIME%\Scripts;%RUNTIME%\bin;%PATH%"
set "PYTHONHOME=%RUNTIME%"
set "PYTHONPATH=%ROOT%;%RUNTIME%\Lib\site-packages"
set "GRC_BLOCKS_PATH=%RUNTIME%\Library\share\gnuradio\grc\blocks;%RUNTIME%\share\gnuradio\grc\blocks;%ROOT%grc\blocks"

if exist "%RUNTIME%\condabin\conda.bat" call "%RUNTIME%\condabin\conda.bat" activate "%RUNTIME%" >nul 2>&1
goto :SHOW_BANNER

:NO_RUNTIME
set "PYTHONPATH=%ROOT%;%PYTHONPATH%"
set "GRC_BLOCKS_PATH=%ROOT%grc\blocks;%GRC_BLOCKS_PATH%"
echo [提示] 未检测到内置 runtime 目录，当前使用系统 Python / Conda 环境。
echo.

:SHOW_BANNER
echo =========================================================================
echo   GNU Radio 伴侣 (GRC) 简体中文增强版 - SDR 命令行运行环境
echo =========================================================================
echo   常用命令:
echo     python grc_zhcn.py         : 启动中文版 GRC 界面
echo     SoapySDRUtil --find        : 探测当前连接的所有 SDR 硬件
echo     uhd_find_devices           : 探测连接的 USRP 设备
echo     volk_profile               : 执行本机 CPU SIMD 指令调优
echo =========================================================================
echo.

cmd /k

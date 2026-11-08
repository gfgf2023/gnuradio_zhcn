@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"

if not exist "%RUNTIME%\python.exe" (
    echo [错误] 未在当前目录下找到 runtime 运行环境！
    echo 请确认已完整解压软件包，并且 runtime 文件夹存在。
    echo.
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

:: 尝试激活 Conda 动态链接（若存在）
if exist "%RUNTIME%\condabin\conda.bat" (
    call "%RUNTIME%\condabin\conda.bat" activate "%RUNTIME%" >nul 2>&1
)

:: 运行 GRC 简体中文增强版
"%RUNTIME%\python.exe" "%ROOT%grc_zhcn.py" %*

if errorlevel 1 (
    echo.
    echo =====================================================================
    echo [提示] GNU Radio 伴侣异常退出 (退出代码: %errorlevel%)
    echo 若初次使用，请检查是否已连接设备驱动，或查阅【使用说明与硬件驱动配置.txt】。
    echo =====================================================================
    pause
)

@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"
set "LANG=zh_CN.UTF-8"
set "LC_ALL=zh_CN.UTF-8"
set "PYTHONIOENCODING=utf-8"

title GNU Radio Companion (zh_CN) - SDR Terminal

if not exist "%RUNTIME%\python.exe" goto NO_RUNTIME

set "PATH=%RUNTIME%;%RUNTIME%\Library\bin;%RUNTIME%\Library\usr\bin;%RUNTIME%\Library\mingw-w64\bin;%RUNTIME%\Scripts;%RUNTIME%\bin;%PATH%"
set "PYTHONHOME=%RUNTIME%"
set "PYTHONPATH=%ROOT%;%RUNTIME%\Lib\site-packages"
set "GRC_BLOCKS_PATH=%RUNTIME%\Library\share\gnuradio\grc\blocks;%RUNTIME%\share\gnuradio\grc\blocks;%ROOT%grc\blocks"

if exist "%RUNTIME%\condabin\conda.bat" call "%RUNTIME%\condabin\conda.bat" activate "%RUNTIME%" >nul 2>&1
goto SHOW_BANNER

:NO_RUNTIME
set "PYTHONPATH=%ROOT%;%PYTHONPATH%"
set "GRC_BLOCKS_PATH=%ROOT%grc\blocks;%GRC_BLOCKS_PATH%"

:SHOW_BANNER
echo =========================================================================
echo   GNU Radio Companion (GRC) zh_CN - SDR Command Line Environment
echo =========================================================================
echo   Commands:
echo     python grc_zhcn.py         : Launch GRC (Chinese UI)
echo     SoapySDRUtil --find        : Detect connected SDR hardware
echo     uhd_find_devices           : Detect connected USRP devices
echo     volk_profile               : Run VOLK SIMD CPU profiler
echo =========================================================================
echo.

cmd /k

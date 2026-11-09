@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"
set "LANG=zh_CN.UTF-8"
set "LC_ALL=zh_CN.UTF-8"
set "PYTHONIOENCODING=utf-8"

if exist "%RUNTIME%\python.exe" goto :USE_PORTABLE_RUNTIME

:: Fallback to system / Radioconda Python if portable runtime folder is not present
set "PYTHONPATH=%ROOT%;%PYTHONPATH%"
set "GRC_BLOCKS_PATH=%ROOT%grc\blocks;%GRC_BLOCKS_PATH%"

where python >nul 2>&1
if not errorlevel 1 goto :USE_SYSTEM_PYTHON

echo =====================================================================
echo [Error] Portable runtime folder not found and Python is not in PATH.
echo [错误] 未找到内置 runtime 运行环境，且系统中未检测到 Python。
echo 请确认下载并解压了完整的全功能便携包 (约 400MB+)。
echo =====================================================================
pause
exit /b 1

:USE_PORTABLE_RUNTIME
set "PATH=%RUNTIME%;%RUNTIME%\Library\bin;%RUNTIME%\Library\usr\bin;%RUNTIME%\Library\mingw-w64\bin;%RUNTIME%\Scripts;%RUNTIME%\bin;%PATH%"
set "PYTHONHOME=%RUNTIME%"
set "PYTHONPATH=%ROOT%;%RUNTIME%\Lib\site-packages"
set "GRC_BLOCKS_PATH=%RUNTIME%\Library\share\gnuradio\grc\blocks;%RUNTIME%\share\gnuradio\grc\blocks;%ROOT%grc\blocks"

if exist "%RUNTIME%\condabin\conda.bat" call "%RUNTIME%\condabin\conda.bat" activate "%RUNTIME%" >nul 2>&1

"%RUNTIME%\python.exe" "%ROOT%grc_zhcn.py" %*
if errorlevel 1 goto :ON_ERROR
exit /b 0

:USE_SYSTEM_PYTHON
python "%ROOT%grc_zhcn.py" %*
if errorlevel 1 goto :ON_ERROR
exit /b 0

:ON_ERROR
echo.
echo =====================================================================
echo [提示] GNU Radio 伴侣异常退出 (Exit Code: %errorlevel%)
echo 若使用外部 Python 环境，请确保已安装依赖:
echo   pip install PyQt6 pyyaml mako qdarkstyle numpy
echo =====================================================================
pause
exit /b 1

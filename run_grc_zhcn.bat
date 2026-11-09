@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "ROOT=%~dp0"
set "RUNTIME=%ROOT%runtime"
set "LANG=zh_CN.UTF-8"
set "LC_ALL=zh_CN.UTF-8"
set "PYTHONIOENCODING=utf-8"

if exist "%RUNTIME%\python.exe" goto RUN_PORTABLE

set "PYTHONPATH=%ROOT%;%PYTHONPATH%"
set "GRC_BLOCKS_PATH=%ROOT%grc\blocks;%GRC_BLOCKS_PATH%"
python "%ROOT%grc_zhcn.py" %*
if errorlevel 1 goto ERR
exit /b 0

:RUN_PORTABLE
set "PATH=%RUNTIME%;%RUNTIME%\Library\bin;%RUNTIME%\Library\usr\bin;%RUNTIME%\Library\mingw-w64\bin;%RUNTIME%\Scripts;%RUNTIME%\bin;%PATH%"
set "PYTHONHOME=%RUNTIME%"
set "PYTHONPATH=%ROOT%;%RUNTIME%\Lib\site-packages"
set "GRC_BLOCKS_PATH=%RUNTIME%\Library\share\gnuradio\grc\blocks;%RUNTIME%\share\gnuradio\grc\blocks;%ROOT%grc\blocks"
"%RUNTIME%\python.exe" "%ROOT%grc_zhcn.py" %*
if errorlevel 1 goto ERR
exit /b 0

:ERR
echo.
echo [Error] Launch failed. Please check Python and dependencies:
echo   pip install PyQt6 pyyaml mako qdarkstyle numpy
pause
exit /b 1

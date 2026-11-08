@echo off
chcp 65001 >nul
cd /d "%~dp0"
python grc_zhcn.py %*
if errorlevel 1 (
    echo.
    echo [错误] 启动失败，请检查 Python 及依赖是否正常。
    echo 推荐安装依赖: pip install PyQt6 pyyaml mako qdarkstyle
    pause
)

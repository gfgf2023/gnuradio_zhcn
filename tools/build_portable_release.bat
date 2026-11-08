@echo off
chcp 65001 >nul
cd /d "%~dp0\.."

echo =========================================================================
echo   GNU Radio 伴侣 (GRC) 简体中文增强版 - 本地发行包构建器
echo =========================================================================
echo.

:: 1. 编译语言包
python tools\compile_po.py
if errorlevel 1 (
    echo [错误] 编译语言包失败！
    pause
    exit /b 1
)

:: 2. 运行单元测试
python -m pytest grc\tests\test_translation_zhcn.py
if errorlevel 1 (
    echo [错误] 单元测试未通过！
    pause
    exit /b 1
)

:: 3. 打包生成绿色便携版
echo.
echo [*] 正在打包生成发布包至 dist 目录...
python tools\package_release.py --os windows --output dist --version 3.11.0.0-zhcn

if errorlevel 1 (
    echo [错误] 打包失败！
    pause
    exit /b 1
)

echo.
echo [成功] 本地便携版打包完成，已存放在 dist 目录下！
echo 包含文件及 SHA256 校验码请查看 dist\SHA256SUMS.txt
echo.
pause

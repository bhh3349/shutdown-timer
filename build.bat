@echo off
chcp 65001 >nul 2>&1
title 定时关机 - 编译器
color 0a

echo.
echo  ============================================
echo         定时关机程序 - 一键编译
echo  ============================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python！
    echo.
    echo 请先在浏览器打开此链接安装 Python：
    echo https://www.python.org/downloads/
    echo.
    echo 安装时务必勾选 "Add Python to PATH"！！！
    echo.
    pause
    exit /b 1
)

echo [1/3] 检测到 Python 版本：
python --version
echo.

echo [2/3] 安装 PyInstaller...
pip install pyinstaller
echo.

echo [3/3] 正在编译程序...
pyinstaller --onefile --windowed --name "定时关机" shutdown_timer.py --clean --noconfirm
echo.

if exist "dist\定时关机.exe" (
    echo ============================================
echo  编译成功！文件位置：
echo  %~dp0dist\定时关机.exe
echo ============================================
echo.
echo 正在打开文件夹...
start "" "dist"
) else (
    echo [错误] 编译失败，请检查上方错误信息
)

echo.
pause

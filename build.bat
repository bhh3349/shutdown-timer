@echo off
title Shutdown Timer Builder
color 0a

echo.
echo  ============================================
echo       Shutdown Timer - Build Script
echo  ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during install!
    echo.
    pause
    exit /b 1
)

echo [1/3] Python detected:
python --version
echo.

echo [2/3] Installing PyInstaller...
pip install pyinstaller
echo.

echo [3/3] Building executable...
pyinstaller --onefile --windowed --name "ShutdownTimer" shutdown_timer.py --clean --noconfirm
echo.

if exist "dist\ShutdownTimer.exe" (
    echo ============================================
    echo   BUILD SUCCESS!
    echo   File: %~dp0dist\ShutdownTimer.exe
    echo ============================================
    echo.
    echo Opening output folder...
    start "" "dist"
) else (
    echo [ERROR] Build failed. Check errors above.
)

echo.
pause

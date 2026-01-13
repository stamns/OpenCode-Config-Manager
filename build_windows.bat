@echo off
chcp 65001 >nul
echo ========================================
echo   OpenCode Config Manager - Windows Build
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

:: Check PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyInstaller...
    pip install pyinstaller
)

:: Clean previous build
echo [INFO] Cleaning previous build...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec

:: Build
echo [INFO] Building executable...
pyinstaller --onefile ^
    --windowed ^
    --name "OpenCodeConfigManager" ^
    --add-data "README.md;." ^
    --icon "assets/icon.ico" ^
    opencode_config_manager.py

if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build completed successfully!
echo   Output: dist/OpenCodeConfigManager.exe
echo ========================================
pause

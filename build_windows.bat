@echo off
chcp 65001 > nul
REM ============================================================
REM OpenCode Config Manager - Windows Build Script
REM v1.0.4 Fluent (PyQt5 + QFluentWidgets)
REM ============================================================
REM
REM 使用方法:
REM   双击运行或在命令行执行: build_windows.bat
REM
REM 依赖:
REM   - Python 3.8+
REM   - PyQt5, PyQt5-Fluent-Widgets, PyInstaller
REM
REM ============================================================

setlocal enabledelayedexpansion

set VERSION=1.0.4
set MAIN_SCRIPT=opencode_config_manager_fluent.py

echo ========================================
echo   OpenCode Config Manager - Windows Build
echo   v%VERSION% Fluent (PyQt5 + QFluentWidgets)
echo ========================================
echo.

REM ==================== Python 检测 ====================
echo [INFO] Checking Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python version: %PYTHON_VERSION%

REM ==================== 依赖安装 ====================
echo [INFO] Checking dependencies...

REM PyQt5
python -c "import PyQt5" > nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyQt5...
    pip install PyQt5
)

REM QFluentWidgets
python -c "import qfluentwidgets" > nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyQt5-Fluent-Widgets...
    pip install PyQt5-Fluent-Widgets
)

REM PyInstaller
python -c "import PyInstaller" > nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing PyInstaller...
    pip install pyinstaller
)

REM ==================== 清理旧构建 ====================
echo [INFO] Cleaning previous build...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del /q *.spec

REM ==================== 构建 ====================
echo [INFO] Building executable...
echo [INFO] This may take a few minutes...

pyinstaller --onefile ^
    --windowed ^
    --name "OpenCodeConfigManager_v%VERSION%" ^
    --add-data "assets;assets" ^
    --collect-data qfluentwidgets ^
    --collect-submodules qfluentwidgets ^
    --hidden-import qfluentwidgets ^
    --hidden-import qfluentwidgets.components ^
    --hidden-import qfluentwidgets.common ^
    --hidden-import qfluentwidgets.window ^
    --icon "assets/icon.ico" ^
    --exclude-module torch ^
    --exclude-module tensorflow ^
    --exclude-module scipy ^
    --exclude-module matplotlib ^
    --exclude-module pandas ^
    --exclude-module numpy ^
    --exclude-module IPython ^
    --exclude-module jupyter ^
    --exclude-module tkinter ^
    %MAIN_SCRIPT%

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

REM ==================== 构建完成 ====================
echo.
echo ========================================
echo   Build completed successfully!
echo ========================================
echo.
echo   Platform: Windows
echo   Output:   dist\OpenCodeConfigManager_v%VERSION%.exe
echo.

REM 显示文件大小
for %%A in (dist\OpenCodeConfigManager_v%VERSION%.exe) do (
    set SIZE=%%~zA
    set /a SIZE_MB=!SIZE!/1048576
    echo   Size:     !SIZE_MB! MB
)

echo.
echo ========================================
echo.
pause

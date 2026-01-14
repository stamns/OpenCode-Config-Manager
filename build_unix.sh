#!/bin/bash
set -e

echo "========================================"
echo "  OpenCode Config Manager - Unix Build"
echo "  v1.0.2 Fluent (PyQt5 + QFluentWidgets)"
echo "========================================"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     PLATFORM=linux;;
    Darwin*)    PLATFORM=macos;;
    *)          PLATFORM=unknown;;
esac

echo "[INFO] Detected platform: ${PLATFORM}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[INFO] Python version: ${PYTHON_VERSION}"

# Check dependencies
echo "[INFO] Checking dependencies..."

if ! python3 -c "import PyQt5" &> /dev/null; then
    echo "[INFO] Installing PyQt5..."
    pip3 install PyQt5
fi

if ! python3 -c "import qfluentwidgets" &> /dev/null; then
    echo "[INFO] Installing PyQt5-Fluent-Widgets..."
    pip3 install PyQt5-Fluent-Widgets
fi

if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "[INFO] Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Clean previous build
echo "[INFO] Cleaning previous build..."
rm -rf dist build

# Collect qfluentwidgets data
echo "[INFO] Collecting qfluentwidgets resources..."

# Build
echo "[INFO] Building executable..."

VERSION="1.0.2"
MAIN_SCRIPT="opencode_config_manager_fluent_v1.0.0.py"

if [ "${PLATFORM}" = "macos" ]; then
    # macOS: Create .app bundle
    pyinstaller --onefile \
        --windowed \
        --name "OpenCodeConfigManager_v${VERSION}" \
        --osx-bundle-identifier "com.opencode.configmanager" \
        --add-data "assets:assets" \
        --collect-data qfluentwidgets \
        --collect-submodules qfluentwidgets \
        --hidden-import qfluentwidgets \
        --hidden-import qfluentwidgets.components \
        --hidden-import qfluentwidgets.common \
        --hidden-import qfluentwidgets.window \
        --icon "assets/icon.png" \
        --exclude-module torch \
        --exclude-module tensorflow \
        --exclude-module scipy \
        --exclude-module matplotlib \
        --exclude-module pandas \
        --exclude-module numpy \
        --exclude-module IPython \
        --exclude-module jupyter \
        --exclude-module tkinter \
        "${MAIN_SCRIPT}"

    # Create DMG (optional)
    if command -v create-dmg &> /dev/null; then
        echo "[INFO] Creating DMG..."
        create-dmg \
            --volname "OpenCode Config Manager" \
            --window-pos 200 120 \
            --window-size 600 400 \
            --icon-size 100 \
            --app-drop-link 450 185 \
            "dist/OpenCodeConfigManager_v${VERSION}.dmg" \
            "dist/OpenCodeConfigManager_v${VERSION}.app"
    fi
else
    # Linux
    pyinstaller --onefile \
        --windowed \
        --name "OpenCodeConfigManager_v${VERSION}" \
        --add-data "assets:assets" \
        --collect-data qfluentwidgets \
        --collect-submodules qfluentwidgets \
        --hidden-import qfluentwidgets \
        --hidden-import qfluentwidgets.components \
        --hidden-import qfluentwidgets.common \
        --hidden-import qfluentwidgets.window \
        --exclude-module torch \
        --exclude-module tensorflow \
        --exclude-module scipy \
        --exclude-module matplotlib \
        --exclude-module pandas \
        --exclude-module numpy \
        --exclude-module IPython \
        --exclude-module jupyter \
        --exclude-module tkinter \
        "${MAIN_SCRIPT}"
fi

echo ""
echo "========================================"
echo "  Build completed successfully!"
if [ "${PLATFORM}" = "macos" ]; then
    echo "  Output: dist/OpenCodeConfigManager_v${VERSION}.app"
else
    echo "  Output: dist/OpenCodeConfigManager_v${VERSION}"
fi
echo "========================================"

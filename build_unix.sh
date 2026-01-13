#!/bin/bash
set -e

echo "========================================"
echo "  OpenCode Config Manager - Unix Build"
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

# Check PyInstaller
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "[INFO] Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Clean previous build
echo "[INFO] Cleaning previous build..."
rm -rf dist build *.spec

# Build
echo "[INFO] Building executable..."

if [ "${PLATFORM}" = "macos" ]; then
    # macOS: Create .app bundle
    pyinstaller --onefile \
        --windowed \
        --name "OpenCodeConfigManager" \
        --osx-bundle-identifier "com.opencode.configmanager" \
        opencode_config_manager.py

    # Create DMG (optional)
    if command -v create-dmg &> /dev/null; then
        echo "[INFO] Creating DMG..."
        create-dmg \
            --volname "OpenCode Config Manager" \
            --window-pos 200 120 \
            --window-size 600 400 \
            --icon-size 100 \
            --app-drop-link 450 185 \
            "dist/OpenCodeConfigManager.dmg" \
            "dist/OpenCodeConfigManager.app"
    fi
else
    # Linux
    pyinstaller --onefile \
        --windowed \
        --name "OpenCodeConfigManager" \
        opencode_config_manager.py
fi

echo ""
echo "========================================"
echo "  Build completed successfully!"
if [ "${PLATFORM}" = "macos" ]; then
    echo "  Output: dist/OpenCodeConfigManager.app"
else
    echo "  Output: dist/OpenCodeConfigManager"
fi
echo "========================================"

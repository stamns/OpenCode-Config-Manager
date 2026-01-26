#!/bin/bash
# OCCM 自动更新安装脚本

set -e

APP_NAME="OCCM.app"
INSTALL_DIR="/Applications"
OLD_APP="$INSTALL_DIR/$APP_NAME"

echo "=========================================="
echo "OCCM 安装/更新工具"
echo "=========================================="

# 查找OCCM.app的位置（支持多种目录结构）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
NEW_APP=""

# 尝试多个可能的位置
if [ -d "$SCRIPT_DIR/$APP_NAME" ]; then
    NEW_APP="$SCRIPT_DIR/$APP_NAME"
elif [ -d "$SCRIPT_DIR/../$APP_NAME" ]; then
    NEW_APP="$SCRIPT_DIR/../$APP_NAME"
elif [ -d "/Volumes/OCCM/$APP_NAME" ]; then
    NEW_APP="/Volumes/OCCM/$APP_NAME"
elif [ -d "/Volumes/OpenCode Config Manager/$APP_NAME" ]; then
    NEW_APP="/Volumes/OpenCode Config Manager/$APP_NAME"
else
    # 在当前目录及父目录搜索
    FOUND=$(find "$SCRIPT_DIR" "$SCRIPT_DIR/.." -maxdepth 2 -name "$APP_NAME" -type d 2>/dev/null | head -1)
    if [ -n "$FOUND" ]; then
        NEW_APP="$FOUND"
    fi
fi

# 检查是否找到应用
if [ -z "$NEW_APP" ] || [ ! -d "$NEW_APP" ]; then
    echo "❌ 错误: 找不到 $APP_NAME"
    echo ""
    echo "请尝试以下方法："
    echo "  1. 直接将 OCCM.app 拖入 /Applications 文件夹"
    echo "  2. 确保此脚本与 OCCM.app 在同一目录"
    echo "  3. 从 DMG 挂载点运行此脚本"
    echo ""
    echo "当前搜索路径："
    echo "  - $SCRIPT_DIR"
    echo "  - /Volumes/OCCM"
    echo "  - /Volumes/OpenCode Config Manager"
    exit 1
fi

echo "✓ 找到应用: $NEW_APP"

# 检查是否有旧版本
if [ -d "$OLD_APP" ]; then
    echo "检测到已安装的版本"
    
    # 获取版本号
    OLD_VERSION=$(defaults read "$OLD_APP/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null || echo "未知")
    NEW_VERSION=$(defaults read "$NEW_APP/Contents/Info.plist" CFBundleShortVersionString 2>/dev/null || echo "未知")
    
    echo "当前版本: $OLD_VERSION"
    echo "新版本: $NEW_VERSION"
    echo ""
    
    # 询问是否替换
    read -p "是否替换旧版本? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "正在备份旧版本..."
        BACKUP_NAME="$OLD_APP.backup.$(date +%Y%m%d_%H%M%S)"
        mv "$OLD_APP" "$BACKUP_NAME"
        echo "✓ 旧版本已备份到: $BACKUP_NAME"
    else
        echo "取消安装"
        exit 0
    fi
else
    echo "首次安装 OCCM"
fi

# 复制新版本
echo "正在安装新版本..."
cp -R "$NEW_APP" "$INSTALL_DIR/"

# 移除隔离属性
echo "正在移除隔离属性..."
xattr -dr com.apple.quarantine "$OLD_APP" 2>/dev/null || true

# 验证安装
if [ -d "$OLD_APP" ]; then
    echo ""
    echo "✓ 安装完成!"
    echo ""
    echo "您现在可以从以下位置启动 OCCM:"
    echo "  - 启动台 (Launchpad)"
    echo "  - 应用程序文件夹"
    echo "  - Spotlight 搜索"
    echo ""
    echo "如果遇到\"应用已损坏\"错误,请运行:"
    echo "  xattr -cr /Applications/OCCM.app"
    echo "=========================================="
else
    echo ""
    echo "❌ 安装失败"
    echo "请手动将 OCCM.app 拖入应用程序文件夹"
    exit 1
fi

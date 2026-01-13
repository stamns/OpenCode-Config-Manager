# -*- mode: python ; coding: utf-8 -*-
# OpenCode Config Manager 构建配置
# 图标已嵌入 exe，无需外部 assets 目录
# 使用方法: pyinstaller OpenCodeConfigManager.spec --noconfirm
# 构建后手动重命名为带版本号的文件名

VERSION = '0.7.0'

a = Analysis(
    ['opencode_config_manager.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/icon.ico', 'assets'), ('assets/icon.png', 'assets')],  # 嵌入图标资源
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=f'OpenCodeConfigManager_v{VERSION}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon.ico'],
)

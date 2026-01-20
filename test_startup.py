#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试程序是否能正常导入和初始化"""

import sys
import os

# 设置输出编码为 UTF-8
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

print("=" * 60)
print("OpenCode Config Manager - 启动测试")
print("=" * 60)

# 测试 1: 导入模块
print("\n[1/4] 测试模块导入...")
try:
    import opencode_config_manager_fluent as app

    print("✓ 模块导入成功")
except Exception as e:
    print(f"✗ 模块导入失败: {e}")
    sys.exit(1)

# 测试 2: 检查 tr 函数
print("\n[2/4] 测试翻译函数...")
try:
    result = app.tr("common.save")
    print(f"✓ tr() 函数正常工作")
    print(f"  示例: tr('common.save') = '{result}'")
except Exception as e:
    print(f"✗ tr() 函数测试失败: {e}")
    sys.exit(1)

# 测试 3: 检查语言管理器
print("\n[3/4] 测试语言管理器...")
try:
    lang_mgr = app.LanguageManager()
    current_lang = lang_mgr._current_language
    available_langs = list(lang_mgr._translations.keys())
    print(f"✓ 语言管理器初始化成功")
    print(f"  当前语言: {current_lang}")
    print(f"  可用语言: {', '.join(available_langs)}")
except Exception as e:
    print(f"✗ 语言管理器测试失败: {e}")
    sys.exit(1)

# 测试 4: 检查翻译文件
print("\n[4/4] 测试翻译文件...")
try:
    zh_keys = len(lang_mgr._translations.get("zh_CN", {}))
    en_keys = len(lang_mgr._translations.get("en_US", {}))
    print(f"✓ 翻译文件加载成功")
    print(f"  zh_CN: {zh_keys} 个键")
    print(f"  en_US: {en_keys} 个键")
except Exception as e:
    print(f"✗ 翻译文件测试失败: {e}")
    sys.exit(1)

# 测试 5: 测试一些关键翻译
print("\n[5/5] 测试关键翻译...")
test_keys = [
    "home.title",
    "provider.title",
    "model.title",
    "mcp.title",
    "cli_export.title",
    "monitor.title",
]

all_ok = True
for key in test_keys:
    try:
        result = app.tr(key)
        print(f"  ✓ {key} = '{result}'")
    except Exception as e:
        print(f"  ✗ {key} 失败: {e}")
        all_ok = False

if not all_ok:
    print("\n✗ 部分翻译键测试失败")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ 所有测试通过！程序可以正常启动。")
print("=" * 60)

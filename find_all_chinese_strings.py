#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查找所有对话框、InfoBar、MessageBox 中的中文字符串"""

import re

# 读取文件
with open("opencode_config_manager_fluent.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 查找中文字符串的模式
chinese_pattern = re.compile(r'["\']([^"\']*[\u4e00-\u9fa5]+[^"\']*)["\']')

# 需要关注的关键词（对话框、提示相关）
keywords = [
    "InfoBar",
    "MessageBox",
    "setPlaceholderText",
    "setToolTip",
    "setText",
    "setTitle",
    "setWindowTitle",
    "Dialog",
    "show_error",
    "show_warning",
    "show_success",
    "show_info",
]

found_strings = []

for i, line in enumerate(lines):
    line_num = i + 1

    # 跳过已经使用 tr() 的行
    if "tr(" in line:
        continue

    # 跳过注释和 docstring
    stripped = line.strip()
    if (
        stripped.startswith("#")
        or stripped.startswith('"""')
        or stripped.startswith("'''")
    ):
        continue

    # 检查是否包含关键词
    has_keyword = any(keyword in line for keyword in keywords)

    if has_keyword:
        # 查找中文字符串
        matches = chinese_pattern.findall(line)
        for match in matches:
            found_strings.append((line_num, match, line.strip(), has_keyword))

# 输出结果到文件
with open("all_chinese_strings_in_dialogs.txt", "w", encoding="utf-8") as out:
    out.write(f"找到 {len(found_strings)} 个对话框/提示中的未翻译中文字符串:\n\n")

    for line_num, text, full_line, has_keyword in found_strings:
        out.write(f"行 {line_num}: {text}\n")
        out.write(f"  完整行: {full_line}\n\n")

print(
    f"结果已保存到 all_chinese_strings_in_dialogs.txt，共找到 {len(found_strings)} 个未翻译的中文字符串"
)

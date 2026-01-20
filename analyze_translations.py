#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""整理并分类所有需要翻译的字符串"""

import re
import json

# 读取文件
with open("opencode_config_manager_fluent.py", "r", encoding="utf-8") as f:
    content = f.read()
    lines = content.split("\n")

# 常见的提示词分类
common_messages = {
    # 通用提示
    "提示": "common.hint",
    "警告": "common.warning",
    "错误": "common.error",
    "成功": "common.success",
    "确认": "common.confirm",
    "信息": "common.info",
    # 通用操作结果
    "已添加": "common.added",
    "已删除": "common.deleted",
    "已保存": "common.saved",
    "已更新": "common.updated",
    "已启用": "common.enabled",
    "已禁用": "common.disabled",
    # 通用错误
    "请选择": "common.please_select",
    "请输入": "common.please_input",
    "不能为空": "common.cannot_be_empty",
    "格式错误": "common.format_error",
    # 通用确认
    "确定要删除": "common.confirm_delete",
    "确认删除": "common.confirm_delete_title",
    "吗？": "",  # 这个通常是问句的一部分
}

# 查找所有 InfoBar 和 MessageBox 调用
infobar_pattern = re.compile(
    r'InfoBar\.(warning|error|success|info)\(["\']([^"\']+)["\'],\s*["\']([^"\']+)["\']'
)
messagebox_pattern = re.compile(
    r'FluentMessageBox\(["\']([^"\']+)["\'],\s*["\']([^"\']+)["\']'
)
placeholder_pattern = re.compile(r'setPlaceholderText\(["\']([^"\']+)["\']')
tooltip_pattern = re.compile(r'setToolTip\(["\']([^"\']+)["\']')

# 收集所有需要翻译的字符串
translations_needed = {
    "infobar": [],
    "messagebox": [],
    "placeholder": [],
    "tooltip": [],
}

for i, line in enumerate(lines):
    line_num = i + 1

    # 跳过已翻译的行
    if "tr(" in line:
        continue

    # InfoBar
    for match in infobar_pattern.finditer(line):
        level, title, message = match.groups()
        if any("\u4e00" <= c <= "\u9fa5" for c in title + message):
            translations_needed["infobar"].append(
                {
                    "line": line_num,
                    "level": level,
                    "title": title,
                    "message": message,
                    "full_line": line.strip(),
                }
            )

    # MessageBox
    for match in messagebox_pattern.finditer(line):
        title, message = match.groups()
        if any("\u4e00" <= c <= "\u9fa5" for c in title + message):
            translations_needed["messagebox"].append(
                {
                    "line": line_num,
                    "title": title,
                    "message": message,
                    "full_line": line.strip(),
                }
            )

    # Placeholder
    for match in placeholder_pattern.finditer(line):
        text = match.group(1)
        if any("\u4e00" <= c <= "\u9fa5" for c in text):
            translations_needed["placeholder"].append(
                {"line": line_num, "text": text, "full_line": line.strip()}
            )

    # Tooltip
    for match in tooltip_pattern.finditer(line):
        text = match.group(1)
        if any("\u4e00" <= c <= "\u9fa5" for c in text):
            translations_needed["tooltip"].append(
                {"line": line_num, "text": text, "full_line": line.strip()}
            )

# 输出统计
with open("translation_analysis.txt", "w", encoding="utf-8") as f:
    f.write("=" * 80 + "\n")
    f.write("翻译需求分析报告\n")
    f.write("=" * 80 + "\n\n")

    f.write(f"InfoBar 调用: {len(translations_needed['infobar'])} 处\n")
    f.write(f"MessageBox 调用: {len(translations_needed['messagebox'])} 处\n")
    f.write(f"Placeholder 文本: {len(translations_needed['placeholder'])} 处\n")
    f.write(f"Tooltip 文本: {len(translations_needed['tooltip'])} 处\n")
    f.write(f"总计: {sum(len(v) for v in translations_needed.values())} 处\n\n")

    f.write("=" * 80 + "\n")
    f.write("详细列表\n")
    f.write("=" * 80 + "\n\n")

    # InfoBar
    f.write("\n### InfoBar 调用 ###\n\n")
    for item in translations_needed["infobar"][:20]:  # 只显示前20个
        f.write(
            f"行 {item['line']}: [{item['level']}] {item['title']} - {item['message']}\n"
        )

    # MessageBox
    f.write("\n### MessageBox 调用 ###\n\n")
    for item in translations_needed["messagebox"][:20]:
        f.write(f"行 {item['line']}: {item['title']} - {item['message']}\n")

    # Placeholder
    f.write("\n### Placeholder 文本 ###\n\n")
    for item in translations_needed["placeholder"][:20]:
        f.write(f"行 {item['line']}: {item['text']}\n")

    # Tooltip
    f.write("\n### Tooltip 文本 ###\n\n")
    for item in translations_needed["tooltip"][:20]:
        f.write(f"行 {item['line']}: {item['text']}\n")

# 保存完整数据为 JSON
with open("translation_data.json", "w", encoding="utf-8") as f:
    json.dump(translations_needed, f, ensure_ascii=False, indent=2)

print(f"分析完成！")
print(f"  InfoBar: {len(translations_needed['infobar'])} 处")
print(f"  MessageBox: {len(translations_needed['messagebox'])} 处")
print(f"  Placeholder: {len(translations_needed['placeholder'])} 处")
print(f"  Tooltip: {len(translations_needed['tooltip'])} 处")
print(f"  总计: {sum(len(v) for v in translations_needed.values())} 处")
print(f"\n详细报告已保存到 translation_analysis.txt")
print(f"完整数据已保存到 translation_data.json")

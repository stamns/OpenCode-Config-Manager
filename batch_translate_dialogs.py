#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量翻译剩余的对话框和提示文本
处理 InfoBar、MessageBox、Placeholder、Tooltip 中的中文字符串
"""

import json

# 读取分析数据
with open("translation_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 准备翻译键和替换规则
translations_zh = {}
translations_en = {}
replacements = []

# 处理 InfoBar 调用
for item in data["infobar"]:
    title = item["title"]
    message = item["message"]
    line = item["line"]
    full_line = item["full_line"]

    # 为每个唯一的消息创建翻译键
    # 标题通常是通用的
    if title == "提示":
        title_key = "common.hint"
    elif title == "警告":
        title_key = "common.warning"
    elif title == "错误":
        title_key = "common.error"
    elif title == "成功":
        title_key = "common.success"
    else:
        # 其他标题，创建新键
        title_key = f"dialog.{title.lower()}"
        translations_zh[title_key] = title
        translations_en[title_key] = title  # 临时使用中文，稍后手动翻译

    # 消息内容
    msg_key = None
    msg_en = None

    if message == "请选择至少一个模型":
        msg_key = "dialog.select_at_least_one_model"
        msg_en = "Please select at least one model"
    elif message == "已禁用所有 Oh My MCP 服务器":
        msg_key = "dialog.disabled_all_ohmymcp"
        msg_en = "All Oh My MCP servers disabled"
    elif message == "预设数据不可用":
        msg_key = "dialog.preset_data_unavailable"
        msg_en = "Preset data unavailable"
    elif message == "当前预设类型与对话框类型不一致":
        msg_key = "dialog.preset_type_mismatch"
        msg_en = "Preset type does not match dialog type"
    elif message == "请选择至少一个 Agent":
        msg_key = "dialog.select_at_least_one_agent"
        msg_en = "Please select at least one Agent"
    elif message == "请输入工具名称":
        msg_key = "dialog.enter_tool_name"
        msg_en = "Please enter tool name"
    elif message == "请输入 Category 名称":
        msg_key = "dialog.enter_category_name"
        msg_en = "Please enter Category name"
    elif message == "请选择一个预设 Category":
        msg_key = "dialog.select_preset_category"
        msg_en = "Please select a preset Category"
    elif message == "备份失败":
        msg_key = "dialog.backup_failed"
        msg_en = "Backup failed"
    elif message == "请先选择一个备份":
        msg_key = "dialog.select_backup_first"
        msg_en = "Please select a backup first"
    elif message == "备份文件不存在":
        msg_key = "dialog.backup_file_not_exist"
        msg_en = "Backup file does not exist"
    elif message == "备份已恢复":
        msg_key = "dialog.backup_restored"
        msg_en = "Backup restored"
    elif message == "恢复失败":
        msg_key = "dialog.restore_failed"
        msg_en = "Restore failed"
    elif message == "备份已删除":
        msg_key = "dialog.backup_deleted"
        msg_en = "Backup deleted"
    elif message == "删除失败":
        msg_key = "dialog.delete_failed"
        msg_en = "Delete failed"
    else:
        # 其他消息
        msg_key = f"dialog.msg_{len(translations_zh)}"
        msg_en = message

    translations_zh[msg_key] = message
    translations_en[msg_key] = msg_en

    # 创建替换规则
    old_pattern = f'InfoBar.{item["level"]}("{title}", "{message}"'
    new_pattern = f'InfoBar.{item["level"]}(tr("{title_key}"), tr("{msg_key}")'
    replacements.append((old_pattern, new_pattern))

# 处理 MessageBox 调用
for item in data["messagebox"]:
    title = item["title"]
    message = item["message"]

    if title == "配置格式检查":
        title_key = "dialog.config_format_check"
        title_en = "Configuration Format Check"
    elif title == "确认删除":
        title_key = "common.confirm_delete_title"
        title_en = "Confirm Delete"
    else:
        title_key = f"dialog.{title.lower().replace(' ', '_')}"
        title_en = title

    if message == "确定要删除此备份吗？":
        msg_key = "dialog.confirm_delete_backup"
        msg_en = "Are you sure you want to delete this backup?"
    else:
        msg_key = f"dialog.msg_{len(translations_zh)}"
        msg_en = message

    translations_zh[title_key] = title
    translations_en[title_key] = title_en
    translations_zh[msg_key] = message
    translations_en[msg_key] = msg_en

    old_pattern = f'FluentMessageBox("{title}", "{message}"'
    new_pattern = f'FluentMessageBox(tr("{title_key}"), tr("{msg_key}")'
    replacements.append((old_pattern, new_pattern))

# 处理 Placeholder 文本
placeholder_translations = {
    "如: 提供网页抓取能力的 MCP 服务器": (
        "dialog.placeholder_mcp_desc",
        "e.g., MCP server providing web scraping capabilities",
    ),
    "如: stdio, web, search": (
        "dialog.placeholder_mcp_tags",
        "e.g., stdio, web, search",
    ),
    "Agent 功能描述": ("dialog.placeholder_agent_desc", "Agent function description"),
    "自定义系统提示词...": (
        "dialog.placeholder_custom_prompt",
        "Custom system prompt...",
    ),
    "如: Bash, Read, mcp_*": (
        "dialog.placeholder_tool_names",
        "e.g., Bash, Read, mcp_*",
    ),
    "描述 Agent 的功能和适用场景": (
        "dialog.placeholder_agent_desc_detail",
        "Describe the Agent's function and applicable scenarios",
    ),
    "如: visual, business-logic": (
        "dialog.placeholder_category_tags",
        "e.g., visual, business-logic",
    ),
    "描述该分类的用途和适用场景": (
        "dialog.placeholder_category_desc",
        "Describe the purpose and applicable scenarios of this category",
    ),
    "选择 Skill 后显示内容": (
        "dialog.placeholder_skill_select",
        "Content displayed after selecting Skill",
    ),
    "描述 Skill 的功能 (1-1024 字符)": (
        "dialog.placeholder_skill_desc",
        "Describe the Skill's function (1-1024 characters)",
    ),
    "如: MIT, Apache-2.0 (可选)": (
        "dialog.placeholder_license",
        "e.g., MIT, Apache-2.0 (optional)",
    ),
    "如: opencode, claude (可选)": (
        "dialog.placeholder_tags",
        "e.g., opencode, claude (optional)",
    ),
    "如: *, internal-*, my-skill": (
        "dialog.placeholder_allow_pattern",
        "e.g., *, internal-*, my-skill",
    ),
    "如: documents-*, internal-*": (
        "dialog.placeholder_deny_pattern",
        "e.g., documents-*, internal-*",
    ),
}

for text, (key, en_text) in placeholder_translations.items():
    translations_zh[key] = text
    translations_en[key] = en_text
    old_pattern = f'setPlaceholderText("{text}")'
    new_pattern = f'setPlaceholderText(tr("{key}"))'
    replacements.append((old_pattern, new_pattern))

# 处理 Tooltip 文本
tooltip_translations = {
    "点击标题切换展开/收起": (
        "dialog.tooltip_toggle_expand",
        "Click title to toggle expand/collapse",
    ),
    "启动对话延迟自动检测": (
        "dialog.tooltip_auto_detect",
        "Start automatic latency detection",
    ),
}

for text, (key, en_text) in tooltip_translations.items():
    translations_zh[key] = text
    translations_en[key] = en_text
    old_pattern = f'setToolTip("{text}")'
    new_pattern = f'setToolTip(tr("{key}"))'
    replacements.append((old_pattern, new_pattern))

# 读取现有语言文件
with open("locales/zh_CN.json", "r", encoding="utf-8") as f:
    zh_data = json.load(f)

with open("locales/en_US.json", "r", encoding="utf-8") as f:
    en_data = json.load(f)

# 添加新翻译
if "dialog" not in zh_data:
    zh_data["dialog"] = {}
if "dialog" not in en_data:
    en_data["dialog"] = {}

for key, value in translations_zh.items():
    if key.startswith("dialog."):
        zh_data["dialog"][key.replace("dialog.", "")] = value
    elif key.startswith("common."):
        if "common" not in zh_data:
            zh_data["common"] = {}
        zh_data["common"][key.replace("common.", "")] = value

for key, value in translations_en.items():
    if key.startswith("dialog."):
        en_data["dialog"][key.replace("dialog.", "")] = value
    elif key.startswith("common."):
        if "common" not in en_data:
            en_data["common"] = {}
        en_data["common"][key.replace("common.", "")] = value

# 保存语言文件
with open("locales/zh_CN.json", "w", encoding="utf-8") as f:
    json.dump(zh_data, f, ensure_ascii=False, indent=2)

with open("locales/en_US.json", "w", encoding="utf-8") as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)

# 执行替换
with open("opencode_config_manager_fluent.py", "r", encoding="utf-8") as f:
    content = f.read()

replaced_count = 0
not_found = []

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        replaced_count += 1
    else:
        not_found.append(old[:100])

# 保存文件
with open("opencode_config_manager_fluent.py", "w", encoding="utf-8") as f:
    f.write(content)

# 输出结果
with open("dialog_translation_result.txt", "w", encoding="utf-8") as f:
    f.write(f"对话框和提示翻译完成\n")
    f.write(f"成功替换: {replaced_count} 处\n")
    f.write(f"总规则数: {len(replacements)}\n")
    f.write(f"新增翻译键: {len(translations_zh)} 个\n\n")

    if not_found:
        f.write(f"未找到的字符串 ({len(not_found)} 个):\n")
        for item in not_found:
            f.write(f"  - {item}\n")

print(f"完成！成功替换 {replaced_count}/{len(replacements)} 处")
print(f"新增翻译键: {len(translations_zh)} 个")

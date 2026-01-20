#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""处理剩余的 MessageBox 和其他中文字符串"""

import json

# 读取文件
with open("opencode_config_manager_fluent.py", "r", encoding="utf-8") as f:
    content = f.read()

# 定义替换规则
replacements = [
    # MessageBox - 确认删除 Agent
    (
        'FluentMessageBox("确认删除", f\'确定要删除 Agent "{name}" 吗？\', self)',
        'FluentMessageBox(tr("common.confirm_delete_title"), tr("dialog.confirm_delete_agent", name=name), self)',
    ),
    # MessageBox - 确认删除 Category
    (
        'FluentMessageBox("确认删除", f\'确定要删除 Category "{name}" 吗？\', self)',
        'FluentMessageBox(tr("common.confirm_delete_title"), tr("dialog.confirm_delete_category", name=name), self)',
    ),
    # MessageBox - 配置文件已变更
    (
        'FluentMessageBox("配置文件已变更", msg, self)',
        'FluentMessageBox(tr("dialog.config_file_changed"), msg, self)',
    ),
    # MessageBox - 配置文件冲突
    (
        'FluentMessageBox(f"{config_name} 配置文件冲突", msg, self)',
        'FluentMessageBox(tr("dialog.config_file_conflict", config_name=config_name), msg, self)',
    ),
    # show_success/error/warning 中的中文
    (
        'self.show_success("成功", f\'Agent "{name}" 已删除\')',
        'self.show_success(tr("common.success"), tr("dialog.agent_deleted", name=name))',
    ),
    (
        'self.show_success("成功", f\'Agent "{name}" 已删除\')',
        'self.show_success(tr("common.success"), tr("dialog.agent_deleted", name=name))',
    ),
    (
        'self.show_success("成功", f\'Category "{name}" 已删除\')',
        'self.show_success(tr("common.success"), tr("dialog.category_deleted", name=name))',
    ),
    # InfoBar - 已添加模型/Agent
    (
        'InfoBar.success("成功", f"已添加 {added} 个模型", parent=self)',
        'InfoBar.success(tr("common.success"), tr("dialog.models_added", count=added), parent=self)',
    ),
    (
        'InfoBar.success("成功", f"已添加 {added} 个 Agent", parent=self)',
        'InfoBar.success(tr("common.success"), tr("dialog.agents_added", count=added), parent=self)',
    ),
    # InfoBar - 已启用/禁用
    (
        'InfoBar.success("成功", f\'已启用 "{mcp_name}"\', parent=self)',
        'InfoBar.success(tr("common.success"), tr("dialog.mcp_enabled", name=mcp_name), parent=self)',
    ),
    (
        'InfoBar.success("成功", f\'已禁用 "{mcp_name}"\', parent=self)',
        'InfoBar.success(tr("common.success"), tr("dialog.mcp_disabled", name=mcp_name), parent=self)',
    ),
    # InfoBar - 错误提示
    (
        'InfoBar.error("错误", f"重新加载失败：\\n{msg}", parent=self)',
        'InfoBar.error(tr("common.error"), tr("dialog.reload_failed", msg=msg), parent=self)',
    ),
]

# 新增翻译键
new_translations_zh = {
    "dialog": {
        "confirm_delete_agent": '确定要删除 Agent "{name}" 吗？',
        "confirm_delete_category": '确定要删除 Category "{name}" 吗？',
        "config_file_changed": "配置文件已变更",
        "config_file_conflict": "{config_name} 配置文件冲突",
        "agent_deleted": 'Agent "{name}" 已删除',
        "category_deleted": 'Category "{name}" 已删除',
        "models_added": "已添加 {count} 个模型",
        "agents_added": "已添加 {count} 个 Agent",
        "mcp_enabled": '已启用 "{name}"',
        "mcp_disabled": '已禁用 "{name}"',
        "reload_failed": "重新加载失败：\n{msg}",
    }
}

new_translations_en = {
    "dialog": {
        "confirm_delete_agent": 'Are you sure you want to delete Agent "{name}"?',
        "confirm_delete_category": 'Are you sure you want to delete Category "{name}"?',
        "config_file_changed": "Configuration File Changed",
        "config_file_conflict": "{config_name} Configuration File Conflict",
        "agent_deleted": 'Agent "{name}" deleted',
        "category_deleted": 'Category "{name}" deleted',
        "models_added": "Added {count} models",
        "agents_added": "Added {count} Agents",
        "mcp_enabled": '"{name}" enabled',
        "mcp_disabled": '"{name}" disabled',
        "reload_failed": "Reload failed:\n{msg}",
    }
}

# 执行替换
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

# 更新语言文件
with open("locales/zh_CN.json", "r", encoding="utf-8") as f:
    zh_data = json.load(f)

with open("locales/en_US.json", "r", encoding="utf-8") as f:
    en_data = json.load(f)

# 合并新翻译
if "dialog" not in zh_data:
    zh_data["dialog"] = {}
if "dialog" not in en_data:
    en_data["dialog"] = {}

zh_data["dialog"].update(new_translations_zh["dialog"])
en_data["dialog"].update(new_translations_en["dialog"])

# 保存语言文件
with open("locales/zh_CN.json", "w", encoding="utf-8") as f:
    json.dump(zh_data, f, ensure_ascii=False, indent=2)

with open("locales/en_US.json", "w", encoding="utf-8") as f:
    json.dump(en_data, f, ensure_ascii=False, indent=2)

# 输出结果
with open("remaining_translation_result.txt", "w", encoding="utf-8") as f:
    f.write(f"剩余翻译完成\n")
    f.write(f"成功替换: {replaced_count} 处\n")
    f.write(f"总规则数: {len(replacements)}\n")
    f.write(f"新增翻译键: {len(new_translations_zh['dialog'])} 个\n\n")

    if not_found:
        f.write(f"未找到的字符串 ({len(not_found)} 个):\n")
        for item in not_found:
            f.write(f"  - {item}\n")

print(f"完成！成功替换 {replaced_count}/{len(replacements)} 处")
print(f"新增翻译键: {len(new_translations_zh['dialog'])} 个")

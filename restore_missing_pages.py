#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""恢复被删除的 NativeProviderPage 和 ModelPage 类"""

# 读取当前文件
with open("opencode_config_manager_fluent.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 读取备份的类
with open("native_provider_page_backup.txt", "r", encoding="utf-8") as f:
    native_provider_lines = f.readlines()

with open("model_page_backup.txt", "r", encoding="utf-8") as f:
    model_page_lines = f.readlines()

# 找到 ProviderPage 类的结束位置（MCPPage 类的开始位置）
mcp_page_line = None
for i, line in enumerate(lines):
    if line.startswith("class MCPPage(BasePage):"):
        mcp_page_line = i
        break

if mcp_page_line is None:
    print("错误：找不到 MCPPage 类")
    exit(1)

print(f"找到 MCPPage 在第 {mcp_page_line + 1} 行")

# 在 MCPPage 之前插入两个类
new_lines = lines[:mcp_page_line]
new_lines.extend(native_provider_lines)
new_lines.append("\n\n")
new_lines.extend(model_page_lines)
new_lines.append("\n\n")
new_lines.extend(lines[mcp_page_line:])

# 保存文件
with open("opencode_config_manager_fluent.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"成功恢复 NativeProviderPage 和 ModelPage 类")
print(f"插入位置：第 {mcp_page_line + 1} 行之前")
print(f"NativeProviderPage: {len(native_provider_lines)} 行")
print(f"ModelPage: {len(model_page_lines)} 行")

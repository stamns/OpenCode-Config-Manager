# -*- coding: utf-8 -*-
"""
合并脚本v4：将10个部分文件合并为一个完整的 opencode_config_manager_v0.9.py
使用更简单的方法：只移除part文件之间的导入语句
"""

import os
import re

# 合并后的文件头部
HEADER = '''# -*- coding: utf-8 -*-
"""
OpenCode 配置管理器 v0.9.0 - PyQt5 + QFluentWidgets 版本
完整合并版本

功能特性：
- 服务商配置管理（支持18种预设SDK）
- 模型配置管理（Token限制、上下文窗口、特性支持）
- MCP服务器配置（本地/远程类型）
- Agent管理（自定义Agent、预设模板）
- 权限配置（allow/ask/deny列表、Bash命令权限）
- 分类配置（Temperature滑块、预设分类模板）
- 技能配置（SKILL.md编辑器）
- 规则配置（AGENTS.md编辑器、全局指令）
- 上下文压缩配置
- 导入导出功能
- 备份恢复功能
- 主题切换（明/暗）

依赖：
- PyQt5
- qfluentwidgets

作者: OpenCode Team
版本: 0.9.0
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from PyQt5.QtCore import Qt, QSize, pyqtSignal, QUrl, QTimer
from PyQt5.QtGui import QIcon, QFont, QDesktopServices
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QStackedWidget, QLabel, QFrame, QSizePolicy, QSpacerItem,
    QSplitter, QDialog, QDialogButtonBox, QFileDialog
)

from qfluentwidgets import (
    FluentWindow, NavigationInterface, NavigationItemPosition,
    FluentIcon, Theme, setTheme, isDarkTheme,
    InfoBar, InfoBarPosition, MessageBox,
    PushButton, PrimaryPushButton, TransparentPushButton,
    SubtitleLabel, BodyLabel, CaptionLabel, TitleLabel,
    CardWidget, SimpleCardWidget, ElevatedCardWidget,
    ScrollArea, SmoothScrollArea,
    ComboBox, LineEdit, TextEdit, SpinBox, DoubleSpinBox,
    SwitchButton, CheckBox, RadioButton,
    Slider, ProgressBar,
    TableWidget, ListWidget, TreeWidget,
    ToolTipFilter, ToolTipPosition,
    Action, RoundMenu,
    StateToolTip,
    setThemeColor, NavigationAvatarWidget,
    SplashScreen, HyperlinkButton, Dialog
)
from qfluentwidgets import FluentIcon as FIF

'''

def read_file(filepath):
    """读取文件内容"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def find_code_start(content):
    """找到实际代码开始的位置（跳过文件头docstring和import语句）"""
    lines = content.split('\n')
    i = 0
    n = len(lines)

    # 跳过编码声明
    while i < n and (lines[i].strip().startswith('# -*-') or lines[i].strip().startswith('# coding') or not lines[i].strip()):
        i += 1

    # 跳过文件头docstring
    if i < n and (lines[i].strip().startswith('"""') or lines[i].strip().startswith("'''")):
        quote = lines[i].strip()[:3]
        # 检查是否是单行docstring
        if lines[i].strip().count(quote) >= 2:
            i += 1
        else:
            i += 1
            while i < n and quote not in lines[i]:
                i += 1
            i += 1  # 跳过结束引号行

    # 跳过空行
    while i < n and not lines[i].strip():
        i += 1

    # 跳过import语句（包括多行import）
    in_multiline = False
    while i < n:
        line = lines[i]
        stripped = line.strip()

        if in_multiline:
            if ')' in line:
                in_multiline = False
            i += 1
            continue

        if stripped.startswith('import ') or stripped.startswith('from '):
            if '(' in line and ')' not in line:
                in_multiline = True
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        # 遇到非import、非空行，停止
        break

    return i

def extract_code_body(content):
    """提取代码主体部分"""
    lines = content.split('\n')
    start_idx = find_code_start(content)

    # 返回从代码开始位置到文件末尾的内容
    return '\n'.join(lines[start_idx:])

def main():
    """主函数"""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 部分文件列表和对应的分隔注释
    parts = [
        ('part1_constants.py', 'Part 1: 常量定义和预设数据'),
        ('part2_services.py', 'Part 2: 服务类'),
        ('part3_mainwindow.py', 'Part 3: 主窗口架构和UI组件'),
        ('part4_provider_model.py', 'Part 4: Provider页面和Model页面'),
        ('part5_mcp_agent.py', 'Part 5: MCP页面和Agent页面'),
        ('part6_category_permission.py', 'Part 6: Category页面和Permission页面'),
        ('part7_skill_rules.py', 'Part 7: Skill页面和Rules页面'),
        ('part8_compaction_import.py', 'Part 8: Compaction页面和Import页面'),
        ('part9_help_backup.py', 'Part 9: Help页面和备份恢复功能'),
        ('part10_main.py', 'Part 10: 主窗口和应用入口'),
    ]

    # 合并内容
    merged_content = HEADER

    for part_file, part_desc in parts:
        filepath = os.path.join(base_dir, part_file)
        if os.path.exists(filepath):
            print(f"处理: {part_file}")
            content = read_file(filepath)
            code = extract_code_body(content)

            # 添加分隔注释
            merged_content += f"\n\n# {'=' * 70}\n# {part_desc}\n# {'=' * 70}\n\n"
            merged_content += code
        else:
            print(f"警告: 文件不存在 {part_file}")

    # 写入合并后的文件
    output_file = os.path.join(base_dir, 'opencode_config_manager_v0.9.py')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(merged_content)

    print(f"\n合并完成: {output_file}")
    print(f"文件大小: {os.path.getsize(output_file)} 字节")
    print(f"总行数: {len(merged_content.splitlines())}")

if __name__ == '__main__':
    main()

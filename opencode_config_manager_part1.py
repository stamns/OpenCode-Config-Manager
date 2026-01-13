#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenCode & Oh My OpenCode 配置管理器
一个可视化的GUI工具，用于管理OpenCode和Oh My OpenCode的配置文件
支持读取Claude Code、Codex等编辑器的配置并导入
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import copy


class ConfigPaths:
    """配置文件路径管理"""
    
    @staticmethod
    def get_user_home() -> Path:
        return Path.home()
    
    @classmethod
    def get_opencode_config(cls) -> Path:
        return cls.get_user_home() / ".config" / "opencode" / "opencode.json"
    
    @classmethod
    def get_ohmyopencode_config(cls) -> Path:
        return cls.get_user_home() / ".config" / "opencode" / "oh-my-opencode.json"
    
    @classmethod
    def get_claude_settings(cls) -> Path:
        return cls.get_user_home() / ".claude" / "settings.json"
    
    @classmethod
    def get_claude_providers(cls) -> Path:
        return cls.get_user_home() / ".claude" / "providers.json"
    
    @classmethod
    def get_codex_config(cls) -> Path:
        return cls.get_user_home() / ".codex" / "config.toml"


class ConfigManager:
    """配置文件读写管理"""
    
    @staticmethod
    def load_json(path: Path) -> Optional[Dict]:
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载配置失败 {path}: {e}")
        return None
    
    @staticmethod
    def save_json(path: Path, data: Dict) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败 {path}: {e}")
            return False
    
    @staticmethod
    def load_toml(path: Path) -> Optional[Dict]:
        """简单的TOML解析器"""
        try:
            if not path.exists():
                return None
            result = {}
            current_section = result
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("["):
                        section_name = line[1:-1]
                        parts = section_name.split(".")
                        current_section = result
                        for part in parts:
                            if part not in current_section:
                                current_section[part] = {}
                            current_section = current_section[part]
                    elif "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        if value.lower() == "true":
                            value = True
                        elif value.lower() == "false":
                            value = False
                        current_section[key] = value
            return result
        except Exception as e:
            print(f"加载TOML失败 {path}: {e}")
            return None

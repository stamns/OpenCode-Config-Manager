#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenCode & Oh My OpenCode 配置管理器 v0.3.0
一个可视化的GUI工具，用于管理OpenCode和Oh My OpenCode的配置文件
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from pathlib import Path
from datetime import datetime
import shutil


# ==================== 预设常用模型 ====================
PRESET_MODELS = {
    "Claude 系列": [
        "claude-opus-4-5-20251101",
        "claude-sonnet-4-5-20250929",
        "claude-sonnet-4-20250514",
        "claude-haiku-3-5-20241022",
    ],
    "GPT 系列": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "o1-preview",
        "o1-mini",
    ],
    "Gemini 系列": [
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    ],
    "其他": [
        "deepseek-chat",
        "deepseek-coder",
        "qwen-max",
    ]
}

PRESET_SDKS = [
    "@ai-sdk/anthropic",
    "@ai-sdk/openai", 
    "@ai-sdk/google",
    "@ai-sdk/azure",
]

PRESET_AGENTS = {
    "oracle": "架构设计、代码审查、策略规划专家",
    "librarian": "多仓库分析、文档查找、实现示例专家",
    "explore": "快速代码库探索和模式匹配专家",
    "frontend-ui-ux-engineer": "UI/UX 设计和前端开发专家",
    "document-writer": "技术文档写作专家",
    "multimodal-looker": "视觉内容分析专家",
    "code-reviewer": "代码质量审查、安全分析专家",
    "debugger": "问题诊断、Bug 修复专家",
}

PRESET_CATEGORIES = {
    "visual": {"temperature": 0.7, "description": "前端、UI/UX、设计相关任务"},
    "business-logic": {"temperature": 0.1, "description": "后端逻辑、架构设计、战略推理"},
    "documentation": {"temperature": 0.3, "description": "文档编写、技术写作任务"},
    "code-analysis": {"temperature": 0.2, "description": "代码审查、重构分析任务"},
}


# ==================== 核心服务类 ====================
class ConfigPaths:
    @staticmethod
    def get_user_home():
        return Path.home()
    
    @classmethod
    def get_opencode_config(cls):
        return cls.get_user_home() / ".config" / "opencode" / "opencode.json"
    
    @classmethod
    def get_ohmyopencode_config(cls):
        return cls.get_user_home() / ".config" / "opencode" / "oh-my-opencode.json"
    
    @classmethod
    def get_claude_settings(cls):
        return cls.get_user_home() / ".claude" / "settings.json"
    
    @classmethod
    def get_claude_providers(cls):
        return cls.get_user_home() / ".claude" / "providers.json"
    
    @classmethod
    def get_backup_dir(cls):
        return cls.get_user_home() / ".config" / "opencode" / "backups"


class ConfigManager:
    @staticmethod
    def load_json(path):
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Load failed {path}: {e}")
        return None
    
    @staticmethod
    def save_json(path, data):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Save failed {path}: {e}")
            return False


class BackupManager:
    def __init__(self):
        self.backup_dir = ConfigPaths.get_backup_dir()
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup(self, config_path):
        try:
            if not config_path.exists():
                return None
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{config_path.stem}.{timestamp}.bak"
            backup_path = self.backup_dir / backup_name
            shutil.copy2(config_path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Backup failed: {e}")
            return None


class ModelRegistry:
    def __init__(self, opencode_config):
        self.config = opencode_config or {}
        self.models = {}
        self.refresh()
    
    def refresh(self):
        self.models = {}
        providers = self.config.get("provider", {})
        for provider_name, provider_data in providers.items():
            models = provider_data.get("models", {})
            for model_id in models.keys():
                full_ref = f"{provider_name}/{model_id}"
                self.models[full_ref] = True
    
    def get_all_models(self):
        return list(self.models.keys())


class ImportService:
    def scan_external_configs(self):
        results = {}
        claude_settings = ConfigPaths.get_claude_settings()
        results["claude_settings"] = {
            "path": str(claude_settings),
            "exists": claude_settings.exists(),
            "data": ConfigManager.load_json(claude_settings) if claude_settings.exists() else None
        }
        claude_providers = ConfigPaths.get_claude_providers()
        results["claude_providers"] = {
            "path": str(claude_providers),
            "exists": claude_providers.exists(),
            "data": ConfigManager.load_json(claude_providers) if claude_providers.exists() else None
        }
        return results


# ==================== OpenCode 配置选项卡 ====================
class ProviderTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        # 左侧列表
        left_frame = ttk.LabelFrame(self, text="Provider 列表", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(toolbar, text="+ 添加", command=self.add_provider, style="Accent.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_provider).pack(side=tk.LEFT, padx=2)
        
        columns = ("name", "display", "models")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=12)
        self.tree.heading("name", text="名称")
        self.tree.heading("display", text="显示名")
        self.tree.heading("models", text="模型数")
        self.tree.column("name", width=100)
        self.tree.column("display", width=140)
        self.tree.column("models", width=60)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # 右侧详情
        right_frame = ttk.LabelFrame(self, text="Provider 详情", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        row = 0
        ttk.Label(right_frame, text="名称:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.name_var, width=35).grid(row=row, column=1, pady=5, sticky=tk.W)
        
        row += 1
        ttk.Label(right_frame, text="显示名:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.display_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.display_var, width=35).grid(row=row, column=1, pady=5, sticky=tk.W)
        
        row += 1
        ttk.Label(right_frame, text="SDK:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.sdk_var = tk.StringVar()
        sdk_combo = ttk.Combobox(right_frame, textvariable=self.sdk_var, width=32, values=PRESET_SDKS)
        sdk_combo.grid(row=row, column=1, pady=5, sticky=tk.W)
        
        row += 1
        ttk.Label(right_frame, text="API 地址:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.url_var, width=35).grid(row=row, column=1, pady=5, sticky=tk.W)
        
        row += 1
        ttk.Label(right_frame, text="API 密钥:").grid(row=row, column=0, sticky=tk.W, pady=5)
        key_frame = ttk.Frame(right_frame)
        key_frame.grid(row=row, column=1, pady=5, sticky=tk.W)
        self.key_var = tk.StringVar()
        self.key_entry = ttk.Entry(key_frame, textvariable=self.key_var, width=28, show="*")
        self.key_entry.pack(side=tk.LEFT)
        self.show_key = tk.BooleanVar(value=False)
        ttk.Checkbutton(key_frame, text="显示", variable=self.show_key, command=self.toggle_key).pack(side=tk.LEFT, padx=5)
        
        row += 1
        ttk.Button(right_frame, text="保存修改", command=self.save_changes, style="Accent.TButton").grid(row=row, column=1, pady=20, sticky=tk.W)
    
    def toggle_key(self):
        self.key_entry.config(show="" if self.show_key.get() else "*")
    
    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        providers = self.app.opencode_config.get("provider", {})
        for name, data in providers.items():
            model_count = len(data.get("models", {}))
            display_name = data.get("name", name)
            self.tree.insert("", tk.END, values=(name, display_name, model_count))
    
    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        name = item["values"][0]
        providers = self.app.opencode_config.get("provider", {})
        if name in providers:
            data = providers[name]
            self.name_var.set(name)
            self.display_var.set(data.get("name", ""))
            self.sdk_var.set(data.get("npm", ""))
            self.url_var.set(data.get("options", {}).get("baseURL", ""))
            self.key_var.set(data.get("options", {}).get("apiKey", ""))
    
    def add_provider(self):
        name = f"provider_{len(self.app.opencode_config.get('provider', {}))}"
        providers = self.app.opencode_config.setdefault("provider", {})
        providers[name] = {"npm": "@ai-sdk/anthropic", "name": name, "options": {"baseURL": "", "apiKey": ""}, "models": {}}
        self.app.mark_modified()
        self.refresh_list()
    
    def delete_provider(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        name = item["values"][0]
        if messagebox.askyesno("确认删除", f"删除 Provider [{name}] 及其所有模型?"):
            del self.app.opencode_config["provider"][name]
            self.app.mark_modified()
            self.refresh_list()
    
    def save_changes(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "名称不能为空")
            return
        providers = self.app.opencode_config.setdefault("provider", {})
        if name not in providers:
            providers[name] = {"models": {}}
        providers[name]["npm"] = self.sdk_var.get()
        providers[name]["name"] = self.display_var.get()
        providers[name]["options"] = {"baseURL": self.url_var.get(), "apiKey": self.key_var.get()}
        self.app.mark_modified()
        self.refresh_list()
        messagebox.showinfo("成功", "Provider 已保存")

# ==================== Model 管理选项卡 ====================
class ModelTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.current_provider = None
        self.setup_ui()

    def setup_ui(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(toolbar, text="选择 Provider:").pack(side=tk.LEFT, padx=(0, 5))
        self.provider_var = tk.StringVar()
        self.provider_combo = ttk.Combobox(toolbar, textvariable=self.provider_var, width=20, state="readonly")
        self.provider_combo.pack(side=tk.LEFT, padx=5)
        self.provider_combo.bind("<<ComboboxSelected>>", self.on_provider_change)
        ttk.Button(toolbar, text="+ 添加模型", command=self.add_model, style="Accent.TButton").pack(side=tk.LEFT, padx=20)
        ttk.Button(toolbar, text="删除", command=self.delete_model).pack(side=tk.LEFT, padx=2)

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        left_frame = ttk.LabelFrame(main_frame, text="模型列表", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        columns = ("model_id", "name", "attachment")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=12)
        self.tree.heading("model_id", text="模型ID")
        self.tree.heading("name", text="显示名称")
        self.tree.heading("attachment", text="附件")
        self.tree.column("model_id", width=180)
        self.tree.column("name", width=150)
        self.tree.column("attachment", width=50)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_frame = ttk.LabelFrame(main_frame, text="模型详情", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        row = 0
        ttk.Label(right_frame, text="预设模型:").grid(row=row, column=0, sticky=tk.W, pady=5)
        preset_frame = ttk.Frame(right_frame)
        preset_frame.grid(row=row, column=1, pady=5, sticky=tk.W)
        self.preset_category_var = tk.StringVar(value="自定义")
        self.preset_category_combo = ttk.Combobox(preset_frame, textvariable=self.preset_category_var, values=["自定义"] + list(PRESET_MODELS.keys()), width=12, state="readonly")
        self.preset_category_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.preset_category_combo.bind("<<ComboboxSelected>>", self.on_preset_category_change)
        self.preset_model_var = tk.StringVar()
        self.preset_model_combo = ttk.Combobox(preset_frame, textvariable=self.preset_model_var, width=25, state="disabled")
        self.preset_model_combo.pack(side=tk.LEFT)
        self.preset_model_combo.bind("<<ComboboxSelected>>", self.on_preset_model_select)

        row += 1
        ttk.Label(right_frame, text="模型ID:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.model_id_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.model_id_var, width=35).grid(row=row, column=1, pady=5, sticky=tk.W)
        row += 1
        ttk.Label(right_frame, text="显示名称:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.model_name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.model_name_var, width=35).grid(row=row, column=1, pady=5, sticky=tk.W)
        row += 1
        ttk.Label(right_frame, text="附件支持:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.attachment_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_frame, text="启用", variable=self.attachment_var).grid(row=row, column=1, pady=5, sticky=tk.W)
        row += 1
        ttk.Label(right_frame, text="上下文限制:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.context_var = tk.StringVar(value="1048576")
        ttk.Entry(right_frame, textvariable=self.context_var, width=15).grid(row=row, column=1, pady=5, sticky=tk.W)
        row += 1
        ttk.Label(right_frame, text="输出限制:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar(value="65535")
        ttk.Entry(right_frame, textvariable=self.output_var, width=15).grid(row=row, column=1, pady=5, sticky=tk.W)
        row += 1
        ttk.Button(right_frame, text="保存模型", command=self.save_model, style="Accent.TButton").grid(row=row, column=1, pady=20, sticky=tk.W)

    def on_preset_category_change(self, event):
        category = self.preset_category_var.get()
        if category == "自定义":
            self.preset_model_combo.config(state="disabled", values=[])
            self.preset_model_var.set("")
        else:
            models = PRESET_MODELS.get(category, [])
            self.preset_model_combo.config(state="readonly", values=models)
            if models:
                self.preset_model_var.set(models[0])
                self.on_preset_model_select(None)

    def on_preset_model_select(self, event):
        model = self.preset_model_var.get()
        if model:
            self.model_id_var.set(model)
            self.model_name_var.set(model)

    def refresh_providers(self):
        providers = list(self.app.opencode_config.get("provider", {}).keys())
        self.provider_combo.config(values=providers)
        if providers and not self.current_provider:
            self.provider_var.set(providers[0])
            self.current_provider = providers[0]
            self.refresh_models()

    def on_provider_change(self, event):
        self.current_provider = self.provider_var.get()
        self.refresh_models()

    def refresh_models(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not self.current_provider:
            return
        providers = self.app.opencode_config.get("provider", {})
        if self.current_provider in providers:
            models = providers[self.current_provider].get("models", {})
            for model_id, data in models.items():
                name = data.get("name", model_id)
                attachment = "✓" if data.get("attachment", False) else ""
                self.tree.insert("", tk.END, values=(model_id, name, attachment))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        model_id = item["values"][0]
        providers = self.app.opencode_config.get("provider", {})
        if self.current_provider in providers:
            models = providers[self.current_provider].get("models", {})
            if model_id in models:
                data = models[model_id]
                self.model_id_var.set(model_id)
                self.model_name_var.set(data.get("name", ""))
                self.attachment_var.set(data.get("attachment", False))
                limit = data.get("limit", {})
                self.context_var.set(str(limit.get("context", 1048576)))
                self.output_var.set(str(limit.get("output", 65535)))

    def add_model(self):
        if not self.current_provider:
            messagebox.showwarning("提示", "请先选择 Provider")
            return
        self.model_id_var.set("")
        self.model_name_var.set("")
        self.attachment_var.set(True)
        self.context_var.set("1048576")
        self.output_var.set("65535")
        self.preset_category_var.set("自定义")
        self.preset_model_combo.config(state="disabled", values=[])

    def delete_model(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        model_id = item["values"][0]
        if messagebox.askyesno("确认删除", f"删除模型 [{model_id}]?"):
            del self.app.opencode_config["provider"][self.current_provider]["models"][model_id]
            self.app.mark_modified()
            self.refresh_models()

    def save_model(self):
        if not self.current_provider:
            messagebox.showwarning("提示", "请先选择 Provider")
            return
        model_id = self.model_id_var.get().strip()
        if not model_id:
            messagebox.showwarning("提示", "模型ID不能为空")
            return
        providers = self.app.opencode_config.setdefault("provider", {})
        if self.current_provider not in providers:
            providers[self.current_provider] = {"models": {}}
        models = providers[self.current_provider].setdefault("models", {})
        models[model_id] = {
            "name": self.model_name_var.get(),
            "attachment": self.attachment_var.get(),
            "limit": {"context": int(self.context_var.get() or 1048576), "output": int(self.output_var.get() or 65535)},
            "modalities": {"input": ["text", "image"], "output": ["text"]},
            "options": {}
        }
        self.app.mark_modified()
        self.refresh_models()
        messagebox.showinfo("成功", "模型已保存")


# ==================== Agent 管理选项卡 ====================
class AgentTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        left_frame = ttk.LabelFrame(self, text="Agent 列表", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(toolbar, text="+ 添加", command=self.add_agent, style="Accent.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_agent).pack(side=tk.LEFT, padx=2)

        columns = ("name", "model", "description")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=12)
        self.tree.heading("name", text="名称")
        self.tree.heading("model", text="绑定模型")
        self.tree.heading("description", text="描述")
        self.tree.column("name", width=100)
        self.tree.column("model", width=180)
        self.tree.column("description", width=200)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_frame = ttk.LabelFrame(self, text="Agent 详情", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        row = 0
        ttk.Label(right_frame, text="预设 Agent:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.preset_agent_var = tk.StringVar(value="自定义")
        preset_values = ["自定义"] + list(PRESET_AGENTS.keys())
        self.preset_combo = ttk.Combobox(right_frame, textvariable=self.preset_agent_var, values=preset_values, width=20, state="readonly")
        self.preset_combo.grid(row=row, column=1, pady=5, sticky=tk.W)
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_select)

        row += 1
        ttk.Label(right_frame, text="名称:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.name_var, width=35).grid(row=row, column=1, pady=5, sticky=tk.W)

        row += 1
        ttk.Label(right_frame, text="绑定模型:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(right_frame, textvariable=self.model_var, width=32)
        self.model_combo.grid(row=row, column=1, pady=5, sticky=tk.W)

        row += 1
        ttk.Label(right_frame, text="描述:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.desc_text = scrolledtext.ScrolledText(right_frame, width=30, height=4)
        self.desc_text.grid(row=row, column=1, pady=5, sticky=tk.W)

        row += 1
        ttk.Button(right_frame, text="保存修改", command=self.save_changes, style="Accent.TButton").grid(row=row, column=1, pady=20, sticky=tk.W)

    def on_preset_select(self, event):
        preset = self.preset_agent_var.get()
        if preset != "自定义" and preset in PRESET_AGENTS:
            self.name_var.set(preset)
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", PRESET_AGENTS[preset])

    def refresh_models(self):
        registry = ModelRegistry(self.app.opencode_config)
        models = registry.get_all_models()
        self.model_combo.config(values=models)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        agents = self.app.ohmyopencode_config.get("agents", {})
        for name, data in agents.items():
            model = data.get("model", "")
            desc = data.get("description", "")[:30]
            self.tree.insert("", tk.END, values=(name, model, desc))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        name = item["values"][0]
        agents = self.app.ohmyopencode_config.get("agents", {})
        if name in agents:
            data = agents[name]
            self.name_var.set(name)
            self.model_var.set(data.get("model", ""))
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", data.get("description", ""))

    def add_agent(self):
        self.name_var.set("")
        self.model_var.set("")
        self.desc_text.delete("1.0", tk.END)
        self.preset_agent_var.set("自定义")

    def delete_agent(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        name = item["values"][0]
        if messagebox.askyesno("确认删除", f"删除 Agent [{name}]?"):
            del self.app.ohmyopencode_config["agents"][name]
            self.app.mark_modified()
            self.refresh_list()

    def save_changes(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "名称不能为空")
            return
        agents = self.app.ohmyopencode_config.setdefault("agents", {})
        agents[name] = {
            "model": self.model_var.get(),
            "description": self.desc_text.get("1.0", tk.END).strip()
        }
        self.app.mark_modified()
        self.refresh_list()
        messagebox.showinfo("成功", "Agent 已保存")


# ==================== Category 管理选项卡 ====================
class CategoryTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        left_frame = ttk.LabelFrame(self, text="Category 列表", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(toolbar, text="+ 添加", command=self.add_category, style="Accent.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_category).pack(side=tk.LEFT, padx=2)

        columns = ("name", "model", "temp", "description")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=12)
        self.tree.heading("name", text="名称")
        self.tree.heading("model", text="绑定模型")
        self.tree.heading("temp", text="Temperature")
        self.tree.heading("description", text="描述")
        self.tree.column("name", width=100)
        self.tree.column("model", width=150)
        self.tree.column("temp", width=80)
        self.tree.column("description", width=150)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_frame = ttk.LabelFrame(self, text="Category 详情", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        row = 0
        ttk.Label(right_frame, text="预设分类:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.preset_var = tk.StringVar(value="自定义")
        preset_values = ["自定义"] + list(PRESET_CATEGORIES.keys())
        self.preset_combo = ttk.Combobox(right_frame, textvariable=self.preset_var, values=preset_values, width=20, state="readonly")
        self.preset_combo.grid(row=row, column=1, pady=5, sticky=tk.W)
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_select)

        row += 1
        ttk.Label(right_frame, text="名称:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.name_var, width=35).grid(row=row, column=1, pady=5, sticky=tk.W)

        row += 1
        ttk.Label(right_frame, text="绑定模型:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(right_frame, textvariable=self.model_var, width=32)
        self.model_combo.grid(row=row, column=1, pady=5, sticky=tk.W)

        row += 1
        ttk.Label(right_frame, text="Temperature:").grid(row=row, column=0, sticky=tk.W, pady=5)
        temp_frame = ttk.Frame(right_frame)
        temp_frame.grid(row=row, column=1, pady=5, sticky=tk.W)
        self.temp_var = tk.DoubleVar(value=0.7)
        self.temp_scale = ttk.Scale(temp_frame, from_=0.0, to=2.0, variable=self.temp_var, orient=tk.HORIZONTAL, length=200, command=self.on_temp_change)
        self.temp_scale.pack(side=tk.LEFT)
        self.temp_label = ttk.Label(temp_frame, text="0.7", width=5)
        self.temp_label.pack(side=tk.LEFT, padx=5)

        row += 1
        ttk.Label(right_frame, text="描述:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        self.desc_text = scrolledtext.ScrolledText(right_frame, width=30, height=4)
        self.desc_text.grid(row=row, column=1, pady=5, sticky=tk.W)

        row += 1
        ttk.Button(right_frame, text="保存修改", command=self.save_changes, style="Accent.TButton").grid(row=row, column=1, pady=20, sticky=tk.W)

    def on_temp_change(self, value):
        self.temp_label.config(text=f"{float(value):.1f}")

    def on_preset_select(self, event):
        preset = self.preset_var.get()
        if preset != "自定义" and preset in PRESET_CATEGORIES:
            data = PRESET_CATEGORIES[preset]
            self.name_var.set(preset)
            self.temp_var.set(data["temperature"])
            self.temp_label.config(text=f"{data['temperature']:.1f}")
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", data["description"])

    def refresh_models(self):
        registry = ModelRegistry(self.app.opencode_config)
        models = registry.get_all_models()
        self.model_combo.config(values=models)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        categories = self.app.ohmyopencode_config.get("categories", {})
        for name, data in categories.items():
            model = data.get("model", "")
            temp = data.get("temperature", 0.7)
            desc = data.get("description", "")[:20]
            self.tree.insert("", tk.END, values=(name, model, temp, desc))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        name = item["values"][0]
        categories = self.app.ohmyopencode_config.get("categories", {})
        if name in categories:
            data = categories[name]
            self.name_var.set(name)
            self.model_var.set(data.get("model", ""))
            temp = data.get("temperature", 0.7)
            self.temp_var.set(temp)
            self.temp_label.config(text=f"{temp:.1f}")
            self.desc_text.delete("1.0", tk.END)
            self.desc_text.insert("1.0", data.get("description", ""))

    def add_category(self):
        self.name_var.set("")
        self.model_var.set("")
        self.temp_var.set(0.7)
        self.temp_label.config(text="0.7")
        self.desc_text.delete("1.0", tk.END)
        self.preset_var.set("自定义")

    def delete_category(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        name = item["values"][0]
        if messagebox.askyesno("确认删除", f"删除 Category [{name}]?"):
            del self.app.ohmyopencode_config["categories"][name]
            self.app.mark_modified()
            self.refresh_list()

    def save_changes(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "名称不能为空")
            return
        categories = self.app.ohmyopencode_config.setdefault("categories", {})
        categories[name] = {
            "model": self.model_var.get(),
            "temperature": round(self.temp_var.get(), 1),
            "description": self.desc_text.get("1.0", tk.END).strip()
        }
        self.app.mark_modified()
        self.refresh_list()
        messagebox.showinfo("成功", "Category 已保存")


# ==================== 权限管理选项卡 ====================
class PermissionTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        left_frame = ttk.LabelFrame(self, text="权限列表", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(toolbar, text="+ 添加", command=self.add_permission, style="Accent.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_permission).pack(side=tk.LEFT, padx=2)

        columns = ("tool", "permission")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        self.tree.heading("tool", text="工具名称")
        self.tree.heading("permission", text="权限")
        self.tree.column("tool", width=200)
        self.tree.column("permission", width=100)
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_frame = ttk.LabelFrame(self, text="权限详情", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        row = 0
        ttk.Label(right_frame, text="工具名称:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tool_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.tool_var, width=35).grid(row=row, column=1, pady=5, sticky=tk.W)

        row += 1
        ttk.Label(right_frame, text="权限:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.perm_var = tk.StringVar(value="ask")
        perm_frame = ttk.Frame(right_frame)
        perm_frame.grid(row=row, column=1, pady=5, sticky=tk.W)
        ttk.Radiobutton(perm_frame, text="允许", variable=self.perm_var, value="allow").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(perm_frame, text="询问", variable=self.perm_var, value="ask").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(perm_frame, text="拒绝", variable=self.perm_var, value="deny").pack(side=tk.LEFT, padx=5)

        row += 1
        ttk.Label(right_frame, text="常用工具:").grid(row=row, column=0, sticky=tk.NW, pady=5)
        preset_frame = ttk.Frame(right_frame)
        preset_frame.grid(row=row, column=1, pady=5, sticky=tk.W)
        presets = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch", "WebSearch", "Task"]
        for i, preset in enumerate(presets):
            btn = ttk.Button(preset_frame, text=preset, width=10, command=lambda p=preset: self.tool_var.set(p))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)

        row += 1
        ttk.Button(right_frame, text="保存修改", command=self.save_changes, style="Accent.TButton").grid(row=row, column=1, pady=20, sticky=tk.W)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        permissions = self.app.opencode_config.get("permission", {})
        for tool, perm in permissions.items():
            self.tree.insert("", tk.END, values=(tool, perm))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        self.tool_var.set(item["values"][0])
        self.perm_var.set(item["values"][1])

    def add_permission(self):
        self.tool_var.set("")
        self.perm_var.set("ask")

    def delete_permission(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        tool = item["values"][0]
        if messagebox.askyesno("确认删除", f"删除权限 [{tool}]?"):
            del self.app.opencode_config["permission"][tool]
            self.app.mark_modified()
            self.refresh_list()

    def save_changes(self):
        tool = self.tool_var.get().strip()
        if not tool:
            messagebox.showwarning("提示", "工具名称不能为空")
            return
        permissions = self.app.opencode_config.setdefault("permission", {})
        permissions[tool] = self.perm_var.get()
        self.app.mark_modified()
        self.refresh_list()
        messagebox.showinfo("成功", "权限已保存")


# ==================== 外部导入选项卡 ====================
class ImportTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.import_service = ImportService()
        self.setup_ui()

    def setup_ui(self):
        top_frame = ttk.LabelFrame(self, text="检测到的外部配置", padding=10)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        toolbar = ttk.Frame(top_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(toolbar, text="刷新检测", command=self.refresh_scan, style="Accent.TButton").pack(side=tk.LEFT, padx=2)

        columns = ("source", "path", "status")
        self.tree = ttk.Treeview(top_frame, columns=columns, show="headings", height=6)
        self.tree.heading("source", text="来源")
        self.tree.heading("path", text="配置路径")
        self.tree.heading("status", text="状态")
        self.tree.column("source", width=120)
        self.tree.column("path", width=300)
        self.tree.column("status", width=80)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        bottom_frame = ttk.LabelFrame(self, text="配置预览", padding=10)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.preview_text = scrolledtext.ScrolledText(bottom_frame, height=10)
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(bottom_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text="导入选中配置", command=self.import_selected, style="Accent.TButton").pack(side=tk.LEFT, padx=5)

    def refresh_scan(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        results = self.import_service.scan_external_configs()
        for key, info in results.items():
            status = "✓ 已检测" if info["exists"] else "✗ 未找到"
            self.tree.insert("", tk.END, values=(key, info["path"], status), tags=(key,))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        source = item["values"][0]
        results = self.import_service.scan_external_configs()
        if source in results and results[source]["data"]:
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert("1.0", json.dumps(results[source]["data"], indent=2, ensure_ascii=False))

    def import_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要导入的配置")
            return
        item = self.tree.item(selection[0])
        source = item["values"][0]
        results = self.import_service.scan_external_configs()
        if source in results and results[source]["data"]:
            if messagebox.askyesno("确认导入", f"确定要导入 [{source}] 的配置吗?"):
                messagebox.showinfo("提示", "导入功能开发中...")


# ==================== 帮助说明选项卡 ====================
class HelpTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 配置优先级说明
        priority_frame = ttk.Frame(notebook, padding=10)
        notebook.add(priority_frame, text="配置优先级")
        priority_text = scrolledtext.ScrolledText(priority_frame, wrap=tk.WORD, font=("Microsoft YaHei", 10))
        priority_text.pack(fill=tk.BOTH, expand=True)
        priority_content = """配置优先顺序（从高到低）

1. 远程配置 (Remote)
   - 通过 API 或远程服务器获取的配置
   - 优先级最高，会覆盖所有本地配置

2. 全局配置 (Global)
   - 位置: ~/.config/opencode/opencode.json
   - 影响所有项目的默认配置

3. 自定义配置 (Custom)
   - 通过 --config 参数指定的配置文件
   - 用于特定场景的配置覆盖

4. 项目配置 (Project)
   - 位置: <项目根目录>/opencode.json
   - 项目级别的配置，仅影响当前项目

5. .opencode 目录配置
   - 位置: <项目根目录>/.opencode/config.json
   - 项目内的隐藏配置目录

6. 内联配置 (Inline)
   - 通过命令行参数直接指定的配置
   - 优先级最低，但最灵活

配置合并规则:
- 高优先级配置会覆盖低优先级的同名配置项
- 未指定的配置项会继承低优先级的值
- Provider 和 Model 配置会进行深度合并"""
        priority_text.insert("1.0", priority_content)
        priority_text.config(state=tk.DISABLED)

        # 使用说明
        usage_frame = ttk.Frame(notebook, padding=10)
        notebook.add(usage_frame, text="使用说明")
        usage_text = scrolledtext.ScrolledText(usage_frame, wrap=tk.WORD, font=("Microsoft YaHei", 10))
        usage_text.pack(fill=tk.BOTH, expand=True)
        usage_content = """OpenCode 配置管理器 使用说明

一、Provider 管理
   - 添加自定义 API 提供商
   - 配置 API 地址和密钥
   - 支持多种 SDK: @ai-sdk/anthropic, @ai-sdk/openai 等

二、Model 管理
   - 在 Provider 下添加模型
   - 支持预设常用模型快速选择
   - 配置模型参数（上下文限制、输出限制等）

三、Agent 管理 (Oh My OpenCode)
   - 配置不同用途的 Agent
   - 绑定已配置的 Provider/Model
   - 支持预设 Agent 模板

四、Category 管理 (Oh My OpenCode)
   - 配置任务分类
   - 设置不同分类的 Temperature
   - 绑定对应的模型

五、权限管理
   - 配置工具的使用权限
   - allow: 允许使用
   - ask: 每次询问
   - deny: 禁止使用

六、外部导入
   - 检测 Claude Code 等工具的配置
   - 一键导入已有配置

注意事项:
- 修改后请点击保存按钮
- 建议定期备份配置文件
- Agent/Category 的模型必须是已配置的 Provider/Model"""
        usage_text.insert("1.0", usage_content)
        usage_text.config(state=tk.DISABLED)

        # 关于
        about_frame = ttk.Frame(notebook, padding=10)
        notebook.add(about_frame, text="关于")
        about_text = scrolledtext.ScrolledText(about_frame, wrap=tk.WORD, font=("Microsoft YaHei", 10))
        about_text.pack(fill=tk.BOTH, expand=True)
        about_content = """OpenCode 配置管理器 v0.3.0

一个可视化的 GUI 工具，用于管理 OpenCode 和 Oh My OpenCode 的配置文件。

功能特点:
- 可视化管理 Provider、Model、Agent、Category
- 支持预设常用模型快速选择
- 支持从 Claude Code 等工具导入配置
- 自动备份配置文件

配置文件位置:
- OpenCode: ~/.config/opencode/opencode.json
- Oh My OpenCode: ~/.config/opencode/oh-my-opencode.json

相关链接:
- OpenCode: https://github.com/opencode-ai/opencode
- Oh My OpenCode: https://github.com/code-yeongyu/oh-my-opencode

开发日期: 2026-01-13"""
        about_text.insert("1.0", about_content)
        about_text.config(state=tk.DISABLED)


# ==================== 主窗口 ====================
class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OpenCode 配置管理器 v0.3.0")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        self.opencode_config = {}
        self.ohmyopencode_config = {}
        self.modified = False
        self.backup_manager = BackupManager()

        self.setup_style()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_notebook()
        self.setup_statusbar()
        self.load_configs()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#f0f0f0")
        style.configure("TNotebook.Tab", padding=[12, 6], font=("Microsoft YaHei", 9))
        style.configure("TLabelframe", background="#f5f5f5")
        style.configure("TLabelframe.Label", font=("Microsoft YaHei", 9, "bold"))
        style.configure("Accent.TButton", font=("Microsoft YaHei", 9))
        style.configure("Treeview", rowheight=25, font=("Microsoft YaHei", 9))
        style.configure("Treeview.Heading", font=("Microsoft YaHei", 9, "bold"))

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存", command=self.save_configs, accelerator="Ctrl+S")
        file_menu.add_command(label="重新加载", command=self.load_configs)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_close)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="备份配置", command=self.backup_configs)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

        self.root.bind("<Control-s>", lambda e: self.save_configs())

    def setup_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(toolbar, text="保存", command=self.save_configs, style="Accent.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="重新加载", command=self.load_configs).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="备份", command=self.backup_configs).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        self.status_label = ttk.Label(toolbar, text="就绪")
        self.status_label.pack(side=tk.RIGHT)

    def setup_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # OpenCode 配置选项卡
        opencode_frame = ttk.Frame(self.notebook)
        self.notebook.add(opencode_frame, text="  OpenCode 配置  ")
        opencode_notebook = ttk.Notebook(opencode_frame)
        opencode_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.provider_tab = ProviderTab(opencode_notebook, self)
        opencode_notebook.add(self.provider_tab, text="Provider")
        self.model_tab = ModelTab(opencode_notebook, self)
        opencode_notebook.add(self.model_tab, text="Model")
        self.permission_tab = PermissionTab(opencode_notebook, self)
        opencode_notebook.add(self.permission_tab, text="权限")

        # Oh My OpenCode 配置选项卡
        ohmyopencode_frame = ttk.Frame(self.notebook)
        self.notebook.add(ohmyopencode_frame, text="  Oh My OpenCode  ")
        ohmyopencode_notebook = ttk.Notebook(ohmyopencode_frame)
        ohmyopencode_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.agent_tab = AgentTab(ohmyopencode_notebook, self)
        ohmyopencode_notebook.add(self.agent_tab, text="Agent")
        self.category_tab = CategoryTab(ohmyopencode_notebook, self)
        ohmyopencode_notebook.add(self.category_tab, text="Category")

        # 外部导入选项卡
        self.import_tab = ImportTab(self.notebook, self)
        self.notebook.add(self.import_tab, text="  外部导入  ")

        # 帮助说明选项卡
        self.help_tab = HelpTab(self.notebook, self)
        self.notebook.add(self.help_tab, text="  帮助说明  ")

    def setup_statusbar(self):
        statusbar = ttk.Frame(self.root)
        statusbar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        self.config_status = ttk.Label(statusbar, text="配置: 未加载")
        self.config_status.pack(side=tk.LEFT)
        self.modified_label = ttk.Label(statusbar, text="")
        self.modified_label.pack(side=tk.RIGHT)

    def load_configs(self):
        opencode_path = ConfigPaths.get_opencode_config()
        ohmyopencode_path = ConfigPaths.get_ohmyopencode_config()
        self.opencode_config = ConfigManager.load_json(opencode_path) or {}
        self.ohmyopencode_config = ConfigManager.load_json(ohmyopencode_path) or {}
        self.refresh_all_tabs()
        provider_count = len(self.opencode_config.get("provider", {}))
        agent_count = len(self.ohmyopencode_config.get("agents", {}))
        self.config_status.config(text=f"配置: Provider {provider_count} | Agent {agent_count}")
        self.modified = False
        self.modified_label.config(text="")
        self.status_label.config(text="配置已加载")

    def refresh_all_tabs(self):
        self.provider_tab.refresh_list()
        self.model_tab.refresh_providers()
        self.permission_tab.refresh_list()
        self.agent_tab.refresh_models()
        self.agent_tab.refresh_list()
        self.category_tab.refresh_models()
        self.category_tab.refresh_list()
        self.import_tab.refresh_scan()

    def save_configs(self):
        opencode_path = ConfigPaths.get_opencode_config()
        ohmyopencode_path = ConfigPaths.get_ohmyopencode_config()
        self.backup_manager.backup(opencode_path)
        self.backup_manager.backup(ohmyopencode_path)
        if ConfigManager.save_json(opencode_path, self.opencode_config):
            if ConfigManager.save_json(ohmyopencode_path, self.ohmyopencode_config):
                self.modified = False
                self.modified_label.config(text="")
                self.status_label.config(text="配置已保存")
                messagebox.showinfo("成功", "配置已保存")
                return
        messagebox.showerror("错误", "保存配置失败")

    def backup_configs(self):
        opencode_path = ConfigPaths.get_opencode_config()
        ohmyopencode_path = ConfigPaths.get_ohmyopencode_config()
        b1 = self.backup_manager.backup(opencode_path)
        b2 = self.backup_manager.backup(ohmyopencode_path)
        if b1 or b2:
            messagebox.showinfo("成功", f"备份已创建")
        else:
            messagebox.showwarning("提示", "没有配置文件需要备份")

    def mark_modified(self):
        self.modified = True
        self.modified_label.config(text="* 已修改")

    def show_about(self):
        messagebox.showinfo("关于", "OpenCode 配置管理器 v0.3.0\n\n可视化管理 OpenCode 和 Oh My OpenCode 配置")

    def on_close(self):
        if self.modified:
            if messagebox.askyesno("确认", "有未保存的修改，确定要退出吗?"):
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()

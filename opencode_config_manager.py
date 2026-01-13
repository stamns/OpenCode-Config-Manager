#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenCode & Oh My OpenCode 配置管理器 v0.4.0
一个可视化的GUI工具，用于管理OpenCode和Oh My OpenCode的配置文件
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from pathlib import Path
from datetime import datetime
import shutil


# ==================== 配色方案 ====================
COLORS = {
    "bg": "#FAFBFC",           # 主背景色
    "card_bg": "#FFFFFF",      # 卡片背景
    "sidebar_bg": "#F6F8FA",   # 侧边栏背景
    "border": "#E1E4E8",       # 边框色
    "text": "#24292E",         # 主文字
    "text_secondary": "#586069", # 次要文字
    "primary": "#0366D6",      # 主色调（蓝色）
    "primary_hover": "#0256B9", # 主色调悬停
    "success": "#28A745",      # 成功色
    "warning": "#F9A825",      # 警告色
    "danger": "#D73A49",       # 危险色
    "accent": "#6F42C1",       # 强调色（紫色）
}

FONTS = {
    "title": ("Microsoft YaHei UI", 14, "bold"),
    "subtitle": ("Microsoft YaHei UI", 11, "bold"),
    "body": ("Microsoft YaHei UI", 10),
    "small": ("Microsoft YaHei UI", 9),
    "mono": ("Consolas", 10),
}


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


# ==================== 自定义控件 ====================
class ModernButton(tk.Canvas):
    """现代风格按钮"""
    def __init__(self, parent, text, command=None, style="primary", width=100, height=32):
        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=COLORS["bg"])
        self.command = command
        self.text = text
        self.style = style
        self.width = width
        self.height = height
        self.hover = False

        self.colors = {
            "primary": (COLORS["primary"], COLORS["primary_hover"], "#FFFFFF"),
            "secondary": (COLORS["sidebar_bg"], COLORS["border"], COLORS["text"]),
            "danger": (COLORS["danger"], "#C82333", "#FFFFFF"),
            "success": (COLORS["success"], "#218838", "#FFFFFF"),
        }

        self.draw()
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def draw(self):
        self.delete("all")
        bg, hover_bg, fg = self.colors.get(self.style, self.colors["primary"])
        color = hover_bg if self.hover else bg
        r = 6
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, r, fill=color, outline="")
        self.create_text(self.width//2, self.height//2, text=self.text, fill=fg, font=FONTS["body"])

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, e):
        self.hover = True
        self.draw()

    def on_leave(self, e):
        self.hover = False
        self.draw()

    def on_click(self, e):
        if self.command:
            self.command()


class Card(tk.Frame):
    """卡片容器"""
    def __init__(self, parent, title=None, **kwargs):
        super().__init__(parent, bg=COLORS["card_bg"], **kwargs)
        self.configure(highlightbackground=COLORS["border"], highlightthickness=1)
        if title:
            title_label = tk.Label(self, text=title, font=FONTS["subtitle"], bg=COLORS["card_bg"], fg=COLORS["text"], anchor="w")
            title_label.pack(fill=tk.X, padx=16, pady=(16, 8))
            sep = tk.Frame(self, height=1, bg=COLORS["border"])
            sep.pack(fill=tk.X, padx=16)
        self.content = tk.Frame(self, bg=COLORS["card_bg"])
        self.content.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)


class ModernEntry(tk.Frame):
    """现代风格输入框"""
    def __init__(self, parent, textvariable=None, width=30, show=None, placeholder=""):
        super().__init__(parent, bg=COLORS["card_bg"])
        self.var = textvariable or tk.StringVar()
        self.placeholder = placeholder
        self.showing_placeholder = False

        self.container = tk.Frame(self, bg=COLORS["card_bg"], highlightbackground=COLORS["border"], highlightthickness=1)
        self.container.pack(fill=tk.X)

        self.entry = tk.Entry(self.container, textvariable=self.var, font=FONTS["body"], width=width,
                              bd=0, bg=COLORS["card_bg"], fg=COLORS["text"], insertbackground=COLORS["text"])
        if show:
            self.entry.config(show=show)
        self.entry.pack(padx=10, pady=8)

        self.entry.bind("<FocusIn>", self.on_focus_in)
        self.entry.bind("<FocusOut>", self.on_focus_out)

    def on_focus_in(self, e):
        self.container.config(highlightbackground=COLORS["primary"], highlightthickness=2)

    def on_focus_out(self, e):
        self.container.config(highlightbackground=COLORS["border"], highlightthickness=1)

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)


# ==================== Provider 管理选项卡 ====================
class ProviderTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        # 左侧列表
        left_frame = Card(self, title="Provider 列表")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), pady=0)

        toolbar = tk.Frame(left_frame.content, bg=COLORS["card_bg"])
        toolbar.pack(fill=tk.X, pady=(0, 12))
        ModernButton(toolbar, "+ 添加", self.add_provider, "primary", 80, 30).pack(side=tk.LEFT, padx=(0, 8))
        ModernButton(toolbar, "删除", self.delete_provider, "danger", 70, 30).pack(side=tk.LEFT)

        # Treeview 样式
        style = ttk.Style()
        style.configure("Modern.Treeview", background=COLORS["card_bg"], foreground=COLORS["text"],
                       fieldbackground=COLORS["card_bg"], rowheight=36, font=FONTS["body"])
        style.configure("Modern.Treeview.Heading", font=FONTS["small"], background=COLORS["sidebar_bg"],
                       foreground=COLORS["text_secondary"])
        style.map("Modern.Treeview", background=[("selected", COLORS["primary"])],
                 foreground=[("selected", "#FFFFFF")])

        columns = ("name", "display", "models")
        self.tree = ttk.Treeview(left_frame.content, columns=columns, show="headings", height=12, style="Modern.Treeview")
        self.tree.heading("name", text="名称")
        self.tree.heading("display", text="显示名")
        self.tree.heading("models", text="模型数")
        self.tree.column("name", width=100)
        self.tree.column("display", width=140)
        self.tree.column("models", width=60)

        scrollbar = ttk.Scrollbar(left_frame.content, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # 右侧详情
        right_frame = Card(self, title="Provider 详情")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=0)

        form = right_frame.content
        row = 0

        tk.Label(form, text="名称", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.name_var = tk.StringVar()
        ModernEntry(form, textvariable=self.name_var, width=28).grid(row=row, column=0, sticky=tk.W, pady=(0, 12))

        row += 1
        tk.Label(form, text="显示名", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.display_var = tk.StringVar()
        ModernEntry(form, textvariable=self.display_var, width=28).grid(row=row, column=0, sticky=tk.W, pady=(0, 12))

        row += 1
        tk.Label(form, text="SDK", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.sdk_var = tk.StringVar()
        sdk_combo = ttk.Combobox(form, textvariable=self.sdk_var, values=PRESET_SDKS, width=26, font=FONTS["body"])
        sdk_combo.grid(row=row, column=0, sticky=tk.W, pady=(0, 12))

        row += 1
        tk.Label(form, text="API 地址", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.url_var = tk.StringVar()
        ModernEntry(form, textvariable=self.url_var, width=28).grid(row=row, column=0, sticky=tk.W, pady=(0, 12))

        row += 1
        tk.Label(form, text="API 密钥", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        key_frame = tk.Frame(form, bg=COLORS["card_bg"])
        key_frame.grid(row=row, column=0, sticky=tk.W, pady=(0, 16))
        self.key_var = tk.StringVar()
        self.key_entry = ModernEntry(key_frame, textvariable=self.key_var, width=22, show="*")
        self.key_entry.pack(side=tk.LEFT)
        self.show_key = tk.BooleanVar(value=False)
        tk.Checkbutton(key_frame, text="显示", variable=self.show_key, command=self.toggle_key,
                      bg=COLORS["card_bg"], fg=COLORS["text_secondary"], font=FONTS["small"],
                      activebackground=COLORS["card_bg"]).pack(side=tk.LEFT, padx=(8, 0))

        row += 1
        ModernButton(form, "保存修改", self.save_changes, "success", 100, 36).grid(row=row, column=0, sticky=tk.W, pady=(8, 0))

    def toggle_key(self):
        self.key_entry.entry.config(show="" if self.show_key.get() else "*")

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
class ModelTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self.current_provider = None
        self.setup_ui()

    def setup_ui(self):
        top_bar = tk.Frame(self, bg=COLORS["bg"])
        top_bar.pack(fill=tk.X, pady=(0, 12))
        tk.Label(top_bar, text="选择 Provider:", font=FONTS["body"], bg=COLORS["bg"], fg=COLORS["text"]).pack(side=tk.LEFT)
        self.provider_var = tk.StringVar()
        self.provider_combo = ttk.Combobox(top_bar, textvariable=self.provider_var, width=20, state="readonly", font=FONTS["body"])
        self.provider_combo.pack(side=tk.LEFT, padx=(8, 0))
        self.provider_combo.bind("<<ComboboxSelected>>", self.on_provider_change)

        main_frame = tk.Frame(self, bg=COLORS["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = Card(main_frame, title="模型列表")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        toolbar = tk.Frame(left_frame.content, bg=COLORS["card_bg"])
        toolbar.pack(fill=tk.X, pady=(0, 12))
        ModernButton(toolbar, "+ 添加", self.add_model, "primary", 80, 30).pack(side=tk.LEFT, padx=(0, 8))
        ModernButton(toolbar, "删除", self.delete_model, "danger", 70, 30).pack(side=tk.LEFT)

        columns = ("model_id", "name", "attachment")
        self.tree = ttk.Treeview(left_frame.content, columns=columns, show="headings", height=10, style="Modern.Treeview")
        self.tree.heading("model_id", text="模型ID")
        self.tree.heading("name", text="显示名称")
        self.tree.heading("attachment", text="附件")
        self.tree.column("model_id", width=180)
        self.tree.column("name", width=140)
        self.tree.column("attachment", width=50)
        scrollbar = ttk.Scrollbar(left_frame.content, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_frame = Card(main_frame, title="模型详情")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        form = right_frame.content
        row = 0
        tk.Label(form, text="预设模型", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        preset_frame = tk.Frame(form, bg=COLORS["card_bg"])
        preset_frame.grid(row=row, column=0, sticky=tk.W, pady=(0, 12))
        self.preset_category_var = tk.StringVar(value="自定义")
        self.preset_category_combo = ttk.Combobox(preset_frame, textvariable=self.preset_category_var, values=["自定义"] + list(PRESET_MODELS.keys()), width=10, state="readonly", font=FONTS["small"])
        self.preset_category_combo.pack(side=tk.LEFT, padx=(0, 8))
        self.preset_category_combo.bind("<<ComboboxSelected>>", self.on_preset_category_change)
        self.preset_model_var = tk.StringVar()
        self.preset_model_combo = ttk.Combobox(preset_frame, textvariable=self.preset_model_var, width=22, state="disabled", font=FONTS["small"])
        self.preset_model_combo.pack(side=tk.LEFT)
        self.preset_model_combo.bind("<<ComboboxSelected>>", self.on_preset_model_select)

        row += 1
        tk.Label(form, text="模型ID", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.model_id_var = tk.StringVar()
        ModernEntry(form, textvariable=self.model_id_var, width=28).grid(row=row, column=0, sticky=tk.W, pady=(0, 12))
        row += 1
        tk.Label(form, text="显示名称", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.model_name_var = tk.StringVar()
        ModernEntry(form, textvariable=self.model_name_var, width=28).grid(row=row, column=0, sticky=tk.W, pady=(0, 12))
        row += 1
        self.attachment_var = tk.BooleanVar(value=True)
        tk.Checkbutton(form, text="支持附件", variable=self.attachment_var, bg=COLORS["card_bg"], fg=COLORS["text"], font=FONTS["body"], activebackground=COLORS["card_bg"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 12))
        row += 1
        limit_frame = tk.Frame(form, bg=COLORS["card_bg"])
        limit_frame.grid(row=row, column=0, sticky=tk.W, pady=(0, 12))
        tk.Label(limit_frame, text="上下文:", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).pack(side=tk.LEFT)
        self.context_var = tk.StringVar(value="1048576")
        tk.Entry(limit_frame, textvariable=self.context_var, width=10, font=FONTS["small"], bd=1, relief=tk.SOLID).pack(side=tk.LEFT, padx=(4, 12))
        tk.Label(limit_frame, text="输出:", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).pack(side=tk.LEFT)
        self.output_var = tk.StringVar(value="65535")
        tk.Entry(limit_frame, textvariable=self.output_var, width=10, font=FONTS["small"], bd=1, relief=tk.SOLID).pack(side=tk.LEFT, padx=(4, 0))
        row += 1
        ModernButton(form, "保存模型", self.save_model, "success", 100, 36).grid(row=row, column=0, sticky=tk.W, pady=(8, 0))


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
class AgentTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        left_frame = Card(self, title="Agent 列表")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        toolbar = tk.Frame(left_frame.content, bg=COLORS["card_bg"])
        toolbar.pack(fill=tk.X, pady=(0, 12))
        ModernButton(toolbar, "+ 添加", self.add_agent, "primary", 80, 30).pack(side=tk.LEFT, padx=(0, 8))
        ModernButton(toolbar, "删除", self.delete_agent, "danger", 70, 30).pack(side=tk.LEFT)

        columns = ("name", "model", "description")
        self.tree = ttk.Treeview(left_frame.content, columns=columns, show="headings", height=12, style="Modern.Treeview")
        self.tree.heading("name", text="名称")
        self.tree.heading("model", text="绑定模型")
        self.tree.heading("description", text="描述")
        self.tree.column("name", width=100)
        self.tree.column("model", width=180)
        self.tree.column("description", width=200)
        scrollbar = ttk.Scrollbar(left_frame.content, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_frame = Card(self, title="Agent 详情")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        form = right_frame.content
        row = 0

        tk.Label(form, text="预设 Agent", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.preset_agent_var = tk.StringVar(value="自定义")
        preset_values = ["自定义"] + list(PRESET_AGENTS.keys())
        self.preset_combo = ttk.Combobox(form, textvariable=self.preset_agent_var, values=preset_values, width=26, state="readonly", font=FONTS["body"])
        self.preset_combo.grid(row=row, column=0, sticky=tk.W, pady=(0, 12))
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_select)

        row += 1
        tk.Label(form, text="名称", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.name_var = tk.StringVar()
        ModernEntry(form, textvariable=self.name_var, width=28).grid(row=row, column=0, sticky=tk.W, pady=(0, 12))

        row += 1
        tk.Label(form, text="绑定模型", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(form, textvariable=self.model_var, width=26, font=FONTS["body"])
        self.model_combo.grid(row=row, column=0, sticky=tk.W, pady=(0, 12))

        row += 1
        tk.Label(form, text="描述", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.desc_text = tk.Text(form, width=30, height=4, font=FONTS["body"], bd=1, relief=tk.SOLID, bg=COLORS["card_bg"])
        self.desc_text.grid(row=row, column=0, sticky=tk.W, pady=(0, 12))

        row += 1
        ModernButton(form, "保存修改", self.save_changes, "success", 100, 36).grid(row=row, column=0, sticky=tk.W, pady=(8, 0))

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
class CategoryTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        left_frame = Card(self, title="Category 列表")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        toolbar = tk.Frame(left_frame.content, bg=COLORS["card_bg"])
        toolbar.pack(fill=tk.X, pady=(0, 12))
        ModernButton(toolbar, "+ 添加", self.add_category, "primary", 80, 30).pack(side=tk.LEFT, padx=(0, 8))
        ModernButton(toolbar, "删除", self.delete_category, "danger", 70, 30).pack(side=tk.LEFT)

        columns = ("name", "model", "temp", "description")
        self.tree = ttk.Treeview(left_frame.content, columns=columns, show="headings", height=12, style="Modern.Treeview")
        self.tree.heading("name", text="名称")
        self.tree.heading("model", text="绑定模型")
        self.tree.heading("temp", text="Temp")
        self.tree.heading("description", text="描述")
        self.tree.column("name", width=100)
        self.tree.column("model", width=150)
        self.tree.column("temp", width=60)
        self.tree.column("description", width=150)
        scrollbar = ttk.Scrollbar(left_frame.content, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_frame = Card(self, title="Category 详情")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        form = right_frame.content
        row = 0

        tk.Label(form, text="预设分类", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.preset_var = tk.StringVar(value="自定义")
        preset_values = ["自定义"] + list(PRESET_CATEGORIES.keys())
        self.preset_combo = ttk.Combobox(form, textvariable=self.preset_var, values=preset_values, width=26, state="readonly", font=FONTS["body"])
        self.preset_combo.grid(row=row, column=0, sticky=tk.W, pady=(0, 12))
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_select)

        row += 1
        tk.Label(form, text="名称", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.name_var = tk.StringVar()
        ModernEntry(form, textvariable=self.name_var, width=28).grid(row=row, column=0, sticky=tk.W, pady=(0, 12))

        row += 1
        tk.Label(form, text="绑定模型", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(form, textvariable=self.model_var, width=26, font=FONTS["body"])
        self.model_combo.grid(row=row, column=0, sticky=tk.W, pady=(0, 12))

        row += 1
        tk.Label(form, text="Temperature", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        temp_frame = tk.Frame(form, bg=COLORS["card_bg"])
        temp_frame.grid(row=row, column=0, sticky=tk.W, pady=(0, 12))
        self.temp_var = tk.DoubleVar(value=0.7)
        self.temp_scale = ttk.Scale(temp_frame, from_=0.0, to=2.0, variable=self.temp_var, orient=tk.HORIZONTAL, length=180, command=self.on_temp_change)
        self.temp_scale.pack(side=tk.LEFT)
        self.temp_label = tk.Label(temp_frame, text="0.7", width=5, font=FONTS["body"], bg=COLORS["card_bg"], fg=COLORS["primary"])
        self.temp_label.pack(side=tk.LEFT, padx=(8, 0))

        row += 1
        tk.Label(form, text="描述", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.desc_text = tk.Text(form, width=30, height=3, font=FONTS["body"], bd=1, relief=tk.SOLID, bg=COLORS["card_bg"])
        self.desc_text.grid(row=row, column=0, sticky=tk.W, pady=(0, 12))

        row += 1
        ModernButton(form, "保存修改", self.save_changes, "success", 100, 36).grid(row=row, column=0, sticky=tk.W, pady=(8, 0))

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
class PermissionTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        left_frame = Card(self, title="权限列表")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        toolbar = tk.Frame(left_frame.content, bg=COLORS["card_bg"])
        toolbar.pack(fill=tk.X, pady=(0, 12))
        ModernButton(toolbar, "+ 添加", self.add_permission, "primary", 80, 30).pack(side=tk.LEFT, padx=(0, 8))
        ModernButton(toolbar, "删除", self.delete_permission, "danger", 70, 30).pack(side=tk.LEFT)

        columns = ("tool", "permission")
        self.tree = ttk.Treeview(left_frame.content, columns=columns, show="headings", height=15, style="Modern.Treeview")
        self.tree.heading("tool", text="工具名称")
        self.tree.heading("permission", text="权限")
        self.tree.column("tool", width=200)
        self.tree.column("permission", width=100)
        scrollbar = ttk.Scrollbar(left_frame.content, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        right_frame = Card(self, title="权限详情")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        form = right_frame.content
        row = 0

        tk.Label(form, text="工具名称", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.tool_var = tk.StringVar()
        ModernEntry(form, textvariable=self.tool_var, width=28).grid(row=row, column=0, sticky=tk.W, pady=(0, 12))

        row += 1
        tk.Label(form, text="权限设置", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        self.perm_var = tk.StringVar(value="ask")
        perm_frame = tk.Frame(form, bg=COLORS["card_bg"])
        perm_frame.grid(row=row, column=0, sticky=tk.W, pady=(0, 16))
        for val, txt, color in [("allow", "允许", COLORS["success"]), ("ask", "询问", COLORS["warning"]), ("deny", "拒绝", COLORS["danger"])]:
            tk.Radiobutton(perm_frame, text=txt, variable=self.perm_var, value=val, bg=COLORS["card_bg"],
                          fg=color, font=FONTS["body"], activebackground=COLORS["card_bg"], selectcolor=COLORS["card_bg"]).pack(side=tk.LEFT, padx=(0, 16))

        row += 1
        tk.Label(form, text="常用工具", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
        row += 1
        preset_frame = tk.Frame(form, bg=COLORS["card_bg"])
        preset_frame.grid(row=row, column=0, sticky=tk.W, pady=(0, 16))
        presets = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "WebFetch", "WebSearch", "Task"]
        for i, preset in enumerate(presets):
            btn = tk.Button(preset_frame, text=preset, width=9, font=FONTS["small"], bd=0, bg=COLORS["sidebar_bg"],
                           fg=COLORS["text"], activebackground=COLORS["border"], cursor="hand2",
                           command=lambda p=preset: self.tool_var.set(p))
            btn.grid(row=i//3, column=i%3, padx=2, pady=2)

        row += 1
        ModernButton(form, "保存修改", self.save_changes, "success", 100, 36).grid(row=row, column=0, sticky=tk.W, pady=(8, 0))

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
class ImportTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self.import_service = ImportService()
        self.setup_ui()

    def setup_ui(self):
        top_frame = Card(self, title="检测到的外部配置")
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        toolbar = tk.Frame(top_frame.content, bg=COLORS["card_bg"])
        toolbar.pack(fill=tk.X, pady=(0, 12))
        ModernButton(toolbar, "刷新检测", self.refresh_scan, "primary", 100, 30).pack(side=tk.LEFT)

        columns = ("source", "path", "status")
        self.tree = ttk.Treeview(top_frame.content, columns=columns, show="headings", height=5, style="Modern.Treeview")
        self.tree.heading("source", text="来源")
        self.tree.heading("path", text="配置路径")
        self.tree.heading("status", text="状态")
        self.tree.column("source", width=120)
        self.tree.column("path", width=350)
        self.tree.column("status", width=80)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        bottom_frame = Card(self, title="配置预览")
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self.preview_text = tk.Text(bottom_frame.content, height=12, font=FONTS["mono"], bd=1, relief=tk.SOLID, bg=COLORS["sidebar_bg"])
        self.preview_text.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(bottom_frame.content, bg=COLORS["card_bg"])
        btn_frame.pack(fill=tk.X, pady=(12, 0))
        ModernButton(btn_frame, "导入选中配置", self.import_selected, "success", 120, 36).pack(side=tk.LEFT)

    def refresh_scan(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        results = self.import_service.scan_external_configs()
        for key, info in results.items():
            status = "✓ 已检测" if info["exists"] else "✗ 未找到"
            self.tree.insert("", tk.END, values=(key, info["path"], status))

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
class HelpTab(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 配置优先级说明
        priority_frame = tk.Frame(notebook, bg=COLORS["card_bg"])
        notebook.add(priority_frame, text="  配置优先级  ")
        priority_card = Card(priority_frame)
        priority_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        priority_text = tk.Text(priority_card.content, wrap=tk.WORD, font=FONTS["body"], bd=0, bg=COLORS["card_bg"], fg=COLORS["text"])
        priority_text.pack(fill=tk.BOTH, expand=True)
        priority_content = """配置优先顺序（从高到低）

1. 远程配置 (Remote)
   通过 API 或远程服务器获取的配置
   优先级最高，会覆盖所有本地配置

2. 全局配置 (Global)
   位置: ~/.config/opencode/opencode.json
   影响所有项目的默认配置

3. 自定义配置 (Custom)
   通过 --config 参数指定的配置文件
   用于特定场景的配置覆盖

4. 项目配置 (Project)
   位置: <项目根目录>/opencode.json
   项目级别的配置，仅影响当前项目

5. .opencode 目录配置
   位置: <项目根目录>/.opencode/config.json
   项目内的隐藏配置目录

6. 内联配置 (Inline)
   通过命令行参数直接指定的配置
   优先级最低，但最灵活

配置合并规则:
- 高优先级配置会覆盖低优先级的同名配置项
- 未指定的配置项会继承低优先级的值
- Provider 和 Model 配置会进行深度合并"""
        priority_text.insert("1.0", priority_content)
        priority_text.config(state=tk.DISABLED)

        # 使用说明
        usage_frame = tk.Frame(notebook, bg=COLORS["card_bg"])
        notebook.add(usage_frame, text="  使用说明  ")
        usage_card = Card(usage_frame)
        usage_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        usage_text = tk.Text(usage_card.content, wrap=tk.WORD, font=FONTS["body"], bd=0, bg=COLORS["card_bg"], fg=COLORS["text"])
        usage_text.pack(fill=tk.BOTH, expand=True)
        usage_content = """OpenCode 配置管理器 使用说明

一、Provider 管理
   添加自定义 API 提供商
   配置 API 地址和密钥
   支持多种 SDK: @ai-sdk/anthropic, @ai-sdk/openai 等

二、Model 管理
   在 Provider 下添加模型
   支持预设常用模型快速选择
   配置模型参数（上下文限制、输出限制等）

三、Agent 管理 (Oh My OpenCode)
   配置不同用途的 Agent
   绑定已配置的 Provider/Model
   支持预设 Agent 模板

四、Category 管理 (Oh My OpenCode)
   配置任务分类
   设置不同分类的 Temperature
   绑定对应的模型

五、权限管理
   配置工具的使用权限
   allow: 允许使用
   ask: 每次询问
   deny: 禁止使用

六、外部导入
   检测 Claude Code 等工具的配置
   一键导入已有配置

注意事项:
- 修改后请点击保存按钮
- 建议定期备份配置文件
- Agent/Category 的模型必须是已配置的 Provider/Model"""
        usage_text.insert("1.0", usage_content)
        usage_text.config(state=tk.DISABLED)

        # 关于
        about_frame = tk.Frame(notebook, bg=COLORS["card_bg"])
        notebook.add(about_frame, text="  关于  ")
        about_card = Card(about_frame)
        about_card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        center_frame = tk.Frame(about_card.content, bg=COLORS["card_bg"])
        center_frame.pack(expand=True)
        
        tk.Label(center_frame, text="OpenCode 配置管理器", font=FONTS["title"], bg=COLORS["card_bg"], fg=COLORS["primary"]).pack(pady=(20, 5))
        tk.Label(center_frame, text="v0.4.0", font=FONTS["subtitle"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).pack(pady=(0, 20))
        tk.Label(center_frame, text="可视化管理 OpenCode 和 Oh My OpenCode 配置文件", font=FONTS["body"], bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        tk.Label(center_frame, text="支持 Provider、Model、Agent、Category 管理", font=FONTS["body"], bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        tk.Label(center_frame, text="支持从 Claude Code 等工具导入配置", font=FONTS["body"], bg=COLORS["card_bg"], fg=COLORS["text"]).pack(pady=5)
        tk.Label(center_frame, text="", font=FONTS["body"], bg=COLORS["card_bg"]).pack(pady=10)
        tk.Label(center_frame, text="开发日期: 2026-01-13", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"]).pack(pady=5)



# ==================== 侧边栏导航 ====================
class Sidebar(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS["sidebar_bg"], width=200)
        self.app = app
        self.pack_propagate(False)
        self.buttons = {}
        self.active = None
        self.setup_ui()

    def setup_ui(self):
        # Logo
        logo_frame = tk.Frame(self, bg=COLORS["sidebar_bg"])
        logo_frame.pack(fill=tk.X, padx=16, pady=20)
        tk.Label(logo_frame, text="OpenCode", font=FONTS["title"], bg=COLORS["sidebar_bg"], fg=COLORS["primary"]).pack(anchor=tk.W)
        tk.Label(logo_frame, text="配置管理器", font=FONTS["small"], bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"]).pack(anchor=tk.W)

        # 分隔线
        tk.Frame(self, height=1, bg=COLORS["border"]).pack(fill=tk.X, padx=16, pady=(0, 16))

        # OpenCode 分组
        tk.Label(self, text="OpenCode", font=FONTS["small"], bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"]).pack(anchor=tk.W, padx=16, pady=(0, 8))
        self.add_nav_button("provider", "Provider 管理")
        self.add_nav_button("model", "Model 管理")
        self.add_nav_button("permission", "权限管理")

        # Oh My OpenCode 分组
        tk.Label(self, text="Oh My OpenCode", font=FONTS["small"], bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"]).pack(anchor=tk.W, padx=16, pady=(20, 8))
        self.add_nav_button("agent", "Agent 管理")
        self.add_nav_button("category", "Category 管理")

        # 其他
        tk.Label(self, text="其他", font=FONTS["small"], bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"]).pack(anchor=tk.W, padx=16, pady=(20, 8))
        self.add_nav_button("import", "外部导入")
        self.add_nav_button("help", "帮助说明")

        # 底部状态
        bottom_frame = tk.Frame(self, bg=COLORS["sidebar_bg"])
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=16)
        self.status_label = tk.Label(bottom_frame, text="就绪", font=FONTS["small"], bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"])
        self.status_label.pack(anchor=tk.W)

    def add_nav_button(self, key, text):
        btn = tk.Label(self, text=text, font=FONTS["body"], bg=COLORS["sidebar_bg"], fg=COLORS["text"],
                      cursor="hand2", anchor=tk.W, padx=16, pady=10)
        btn.pack(fill=tk.X)
        btn.bind("<Enter>", lambda e, b=btn, k=key: self.on_hover(b, k, True))
        btn.bind("<Leave>", lambda e, b=btn, k=key: self.on_hover(b, k, False))
        btn.bind("<Button-1>", lambda e, k=key: self.on_click(k))
        self.buttons[key] = btn

    def on_hover(self, btn, key, enter):
        if key != self.active:
            btn.config(bg=COLORS["border"] if enter else COLORS["sidebar_bg"])

    def on_click(self, key):
        if self.active:
            self.buttons[self.active].config(bg=COLORS["sidebar_bg"], fg=COLORS["text"])
        self.active = key
        self.buttons[key].config(bg=COLORS["primary"], fg="#FFFFFF")
        self.app.show_page(key)

    def set_active(self, key):
        if self.active:
            self.buttons[self.active].config(bg=COLORS["sidebar_bg"], fg=COLORS["text"])
        self.active = key
        self.buttons[key].config(bg=COLORS["primary"], fg="#FFFFFF")



# ==================== 主窗口 ====================
class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OpenCode 配置管理器")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 600)
        self.root.configure(bg=COLORS["bg"])

        self.opencode_config = {}
        self.ohmyopencode_config = {}
        self.modified = False
        self.backup_manager = BackupManager()
        self.pages = {}

        self.setup_ui()
        self.load_configs()

    def setup_ui(self):
        # 主容器
        main_container = tk.Frame(self.root, bg=COLORS["bg"])
        main_container.pack(fill=tk.BOTH, expand=True)

        # 侧边栏
        self.sidebar = Sidebar(main_container, self)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # 右侧内容区
        right_container = tk.Frame(main_container, bg=COLORS["bg"])
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 顶部工具栏
        toolbar = tk.Frame(right_container, bg=COLORS["card_bg"], height=60)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)

        toolbar_inner = tk.Frame(toolbar, bg=COLORS["card_bg"])
        toolbar_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        ModernButton(toolbar_inner, "保存", self.save_configs, "primary", 80, 36).pack(side=tk.LEFT, padx=(0, 8))
        ModernButton(toolbar_inner, "重新加载", self.load_configs, "secondary", 90, 36).pack(side=tk.LEFT, padx=(0, 8))
        ModernButton(toolbar_inner, "备份", self.backup_configs, "secondary", 70, 36).pack(side=tk.LEFT)

        self.modified_label = tk.Label(toolbar_inner, text="", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["warning"])
        self.modified_label.pack(side=tk.RIGHT)

        self.config_status = tk.Label(toolbar_inner, text="配置: 未加载", font=FONTS["small"], bg=COLORS["card_bg"], fg=COLORS["text_secondary"])
        self.config_status.pack(side=tk.RIGHT, padx=(0, 20))

        # 分隔线
        tk.Frame(right_container, height=1, bg=COLORS["border"]).pack(fill=tk.X)

        # 内容区
        self.content_frame = tk.Frame(right_container, bg=COLORS["bg"])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 创建页面
        self.pages["provider"] = ProviderTab(self.content_frame, self)
        self.pages["model"] = ModelTab(self.content_frame, self)
        self.pages["permission"] = PermissionTab(self.content_frame, self)
        self.pages["agent"] = AgentTab(self.content_frame, self)
        self.pages["category"] = CategoryTab(self.content_frame, self)
        self.pages["import"] = ImportTab(self.content_frame, self)
        self.pages["help"] = HelpTab(self.content_frame, self)

        # 默认显示 Provider 页面
        self.show_page("provider")
        self.sidebar.set_active("provider")

        # 快捷键
        self.root.bind("<Control-s>", lambda e: self.save_configs())

    def show_page(self, key):
        for page in self.pages.values():
            page.pack_forget()
        if key in self.pages:
            self.pages[key].pack(fill=tk.BOTH, expand=True)

    def load_configs(self):
        opencode_path = ConfigPaths.get_opencode_config()
        ohmyopencode_path = ConfigPaths.get_ohmyopencode_config()
        self.opencode_config = ConfigManager.load_json(opencode_path) or {}
        self.ohmyopencode_config = ConfigManager.load_json(ohmyopencode_path) or {}
        self.refresh_all_tabs()
        provider_count = len(self.opencode_config.get("provider", {}))
        agent_count = len(self.ohmyopencode_config.get("agents", {}))
        self.config_status.config(text=f"Provider: {provider_count} | Agent: {agent_count}")
        self.modified = False
        self.modified_label.config(text="")
        self.sidebar.status_label.config(text="配置已加载")

    def refresh_all_tabs(self):
        self.pages["provider"].refresh_list()
        self.pages["model"].refresh_providers()
        self.pages["permission"].refresh_list()
        self.pages["agent"].refresh_models()
        self.pages["agent"].refresh_list()
        self.pages["category"].refresh_models()
        self.pages["category"].refresh_list()
        self.pages["import"].refresh_scan()

    def save_configs(self):
        opencode_path = ConfigPaths.get_opencode_config()
        ohmyopencode_path = ConfigPaths.get_ohmyopencode_config()
        self.backup_manager.backup(opencode_path)
        self.backup_manager.backup(ohmyopencode_path)
        if ConfigManager.save_json(opencode_path, self.opencode_config):
            if ConfigManager.save_json(ohmyopencode_path, self.ohmyopencode_config):
                self.modified = False
                self.modified_label.config(text="")
                self.sidebar.status_label.config(text="配置已保存")
                messagebox.showinfo("成功", "配置已保存")
                return
        messagebox.showerror("错误", "保存配置失败")

    def backup_configs(self):
        opencode_path = ConfigPaths.get_opencode_config()
        ohmyopencode_path = ConfigPaths.get_ohmyopencode_config()
        b1 = self.backup_manager.backup(opencode_path)
        b2 = self.backup_manager.backup(ohmyopencode_path)
        if b1 or b2:
            messagebox.showinfo("成功", "备份已创建")
        else:
            messagebox.showwarning("提示", "没有配置文件需要备份")

    def mark_modified(self):
        self.modified = True
        self.modified_label.config(text="● 已修改")

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

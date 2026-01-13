#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import copy
from datetime import datetime
import shutil
import re


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
    def get_codex_config(cls):
        return cls.get_user_home() / ".codex" / "config.toml"
    
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
    
    def restore(self, backup_path, target_path):
        try:
            if not backup_path.exists():
                return False
            shutil.copy2(backup_path, target_path)
            return True
        except Exception as e:
            print(f"Restore failed: {e}")
            return False
    
    def list_backups(self, config_name):
        pattern = f"{config_name}.*.bak"
        backups = sorted(self.backup_dir.glob(pattern), reverse=True)
        return backups
    
    def cleanup_old_backups(self, config_name, keep_count=10):
        backups = self.list_backups(config_name)
        for old_backup in backups[keep_count:]:
            try:
                old_backup.unlink()
            except Exception:
                pass


print("Part 1 classes defined")


class DataValidator:
    @staticmethod
    def validate_url(url):
        import re
        pattern = r"^https?://[\w\-.]+(:\d+)?(/.*)?$"
        return bool(re.match(pattern, url))
    
    @staticmethod
    def validate_provider(provider_data):
        if not provider_data.get("npm"):
            return False, "Missing npm field"
        options = provider_data.get("options", {})
        if not options.get("baseURL"):
            return False, "Missing baseURL"
        if not DataValidator.validate_url(options.get("baseURL", "")):
            return False, "Invalid URL format"
        if not options.get("apiKey"):
            return False, "Missing apiKey"
        return True, ""
    
    @staticmethod
    def validate_model(model_data):
        if not model_data.get("name"):
            return False, "Missing model name"
        return True, ""
    
    @staticmethod
    def validate_agent(agent_data, available_models):
        model_ref = agent_data.get("model", "")
        if not model_ref:
            return False, "Missing model reference"
        if model_ref not in available_models:
            return False, f"Model {model_ref} not found"
        return True, ""


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
            for model_id, model_info in models.items():
                full_ref = f"{provider_name}/{model_id}"
                self.models[full_ref] = {
                    "provider": provider_name,
                    "model_id": model_id,
                    "info": model_info
                }
    
    def get_all_models(self):
        return list(self.models.keys())
    
    def get_models_by_provider(self, provider):
        return [ref for ref, data in self.models.items() if data["provider"] == provider]
    
    def model_exists(self, model_ref):
        return model_ref in self.models
    
    def get_providers(self):
        providers = self.config.get("provider", {})
        return list(providers.keys())


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
        codex_config = ConfigPaths.get_codex_config()
        results["codex"] = {
            "path": str(codex_config),
            "exists": codex_config.exists()
        }
        return results


class ProviderTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        # Left panel - Provider list
        left_frame = ttk.LabelFrame(self, text="Provider 列表", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=5)
        ttk.Button(toolbar, text="添加", command=self.add_provider).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="编辑", command=self.edit_provider).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_provider).pack(side=tk.LEFT, padx=2)
        
        # Treeview
        columns = ("name", "display", "models", "status")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        self.tree.heading("name", text="名称")
        self.tree.heading("display", text="显示名")
        self.tree.heading("models", text="模型数")
        self.tree.heading("status", text="状态")
        self.tree.column("name", width=100)
        self.tree.column("display", width=120)
        self.tree.column("models", width=60)
        self.tree.column("status", width=60)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        # Right panel - Details
        right_frame = ttk.LabelFrame(self, text="Provider 详情", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Detail fields
        ttk.Label(right_frame, text="名称:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, pady=2)
        
        ttk.Label(right_frame, text="显示名:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.display_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.display_var, width=40).grid(row=1, column=1, pady=2)
        
        ttk.Label(right_frame, text="SDK:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.sdk_var = tk.StringVar()
        sdk_combo = ttk.Combobox(right_frame, textvariable=self.sdk_var, width=37)
        sdk_combo["values"] = ("@ai-sdk/anthropic", "@ai-sdk/openai", "@ai-sdk/google")
        sdk_combo.grid(row=2, column=1, pady=2)
        
        ttk.Label(right_frame, text="API地址:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.url_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.url_var, width=40).grid(row=3, column=1, pady=2)
        
        ttk.Label(right_frame, text="API密钥:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.key_var = tk.StringVar()
        self.key_entry = ttk.Entry(right_frame, textvariable=self.key_var, width=40, show="*")
        self.key_entry.grid(row=4, column=1, pady=2)
        
        self.show_key = tk.BooleanVar(value=False)
        ttk.Checkbutton(right_frame, text="显示密钥", variable=self.show_key, 
                       command=self.toggle_key_visibility).grid(row=5, column=1, sticky=tk.W)
        
        ttk.Button(right_frame, text="保存修改", command=self.save_changes).grid(row=6, column=1, pady=10)
    
    def toggle_key_visibility(self):
        self.key_entry.config(show="" if self.show_key.get() else "*")
    
    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        providers = self.app.opencode_config.get("provider", {})
        for name, data in providers.items():
            model_count = len(data.get("models", {}))
            display_name = data.get("name", name)
            self.tree.insert("", tk.END, values=(name, display_name, model_count, "启用"))
    
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
        dialog = ProviderDialog(self, self.app)
        self.wait_window(dialog)
        self.refresh_list()
    
    def edit_provider(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个 Provider")
            return
        item = self.tree.item(selection[0])
        name = item["values"][0]
        dialog = ProviderDialog(self, self.app, name)
        self.wait_window(dialog)
        self.refresh_list()
    
    def delete_provider(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个 Provider")
            return
        item = self.tree.item(selection[0])
        name = item["values"][0]
        if messagebox.askyesno("确认删除", f"确定要删除 Provider [{name}] 吗？\n这将同时删除其下所有模型配置。"):
            providers = self.app.opencode_config.get("provider", {})
            if name in providers:
                del providers[name]
                self.app.mark_modified()
                self.refresh_list()
    
    def save_changes(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "Provider 名称不能为空")
            return
        providers = self.app.opencode_config.setdefault("provider", {})
        if name not in providers:
            providers[name] = {"models": {}}
        providers[name]["npm"] = self.sdk_var.get()
        providers[name]["name"] = self.display_var.get()
        providers[name]["options"] = {
            "baseURL": self.url_var.get(),
            "apiKey": self.key_var.get()
        }
        self.app.mark_modified()
        self.refresh_list()
        messagebox.showinfo("成功", "Provider 配置已更新")


class ProviderDialog(tk.Toplevel):
    def __init__(self, parent, app, edit_name=None):
        super().__init__(parent)
        self.app = app
        self.edit_name = edit_name
        self.title("编辑 Provider" if edit_name else "添加 Provider")
        self.geometry("450x300")
        self.resizable(False, False)
        self.setup_ui()
        if edit_name:
            self.load_data()
    
    def setup_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(frame, textvariable=self.name_var, width=35)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="显示名:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.display_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.display_var, width=35).grid(row=1, column=1, pady=5)
        
        ttk.Label(frame, text="SDK:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.sdk_var = tk.StringVar(value="@ai-sdk/anthropic")
        sdk_combo = ttk.Combobox(frame, textvariable=self.sdk_var, width=32)
        sdk_combo["values"] = ("@ai-sdk/anthropic", "@ai-sdk/openai", "@ai-sdk/google")
        sdk_combo.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="API地址:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.url_var, width=35).grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text="API密钥:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.key_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.key_var, width=35).grid(row=4, column=1, pady=5)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="保存", command=self.save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=10)
        
        if self.edit_name:
            self.name_entry.config(state="disabled")
    
    def load_data(self):
        providers = self.app.opencode_config.get("provider", {})
        if self.edit_name in providers:
            data = providers[self.edit_name]
            self.name_var.set(self.edit_name)
            self.display_var.set(data.get("name", ""))
            self.sdk_var.set(data.get("npm", "@ai-sdk/anthropic"))
            self.url_var.set(data.get("options", {}).get("baseURL", ""))
            self.key_var.set(data.get("options", {}).get("apiKey", ""))
    
    def save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "名称不能为空")
            return
        if not self.url_var.get().strip():
            messagebox.showwarning("提示", "API地址不能为空")
            return
        if not self.key_var.get().strip():
            messagebox.showwarning("提示", "API密钥不能为空")
            return
        
        providers = self.app.opencode_config.setdefault("provider", {})
        if not self.edit_name and name in providers:
            messagebox.showwarning("提示", f"Provider [{name}] 已存在")
            return
        
        providers[name] = {
            "npm": self.sdk_var.get(),
            "name": self.display_var.get() or name,
            "options": {
                "baseURL": self.url_var.get(),
                "apiKey": self.key_var.get()
            },
            "models": providers.get(name, {}).get("models", {})
        }
        self.app.mark_modified()
        self.destroy()


class ModelTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(top_frame, text="选择 Provider:").pack(side=tk.LEFT)
        self.provider_var = tk.StringVar()
        self.provider_combo = ttk.Combobox(top_frame, textvariable=self.provider_var, width=30)
        self.provider_combo.pack(side=tk.LEFT, padx=5)
        self.provider_combo.bind("<<ComboboxSelected>>", self.on_provider_change)
        ttk.Button(top_frame, text="添加模型", command=self.add_model).pack(side=tk.RIGHT, padx=2)
        ttk.Button(top_frame, text="删除模型", command=self.delete_model).pack(side=tk.RIGHT, padx=2)
        left_frame = ttk.LabelFrame(self, text="模型列表", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        columns = ("model_id", "name")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=12)
        self.tree.heading("model_id", text="模型ID")
        self.tree.heading("name", text="显示名称")
        self.tree.column("model_id", width=200)
        self.tree.column("name", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        right_frame = ttk.LabelFrame(self, text="模型详情", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Label(right_frame, text="模型ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.model_id_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.model_id_var, width=35).grid(row=0, column=1, pady=2)
        ttk.Label(right_frame, text="显示名称:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.model_name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.model_name_var, width=35).grid(row=1, column=1, pady=2)
        ttk.Label(right_frame, text="附件支持:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.attachment_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(right_frame, variable=self.attachment_var).grid(row=2, column=1, sticky=tk.W, pady=2)
        ttk.Button(right_frame, text="保存修改", command=self.save_changes).grid(row=3, column=1, pady=10)

    def refresh_providers(self):
        providers = self.app.opencode_config.get("provider", {})
        self.provider_combo["values"] = list(providers.keys())
        if providers:
            self.provider_var.set(list(providers.keys())[0])
            self.refresh_models()

    def on_provider_change(self, event=None):
        self.refresh_models()

    def refresh_models(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        provider = self.provider_var.get()
        if not provider:
            return
        providers = self.app.opencode_config.get("provider", {})
        if provider in providers:
            models = providers[provider].get("models", {})
            for model_id, data in models.items():
                name = data.get("name", model_id)
                self.tree.insert("", tk.END, values=(model_id, name))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        model_id = item["values"][0]
        provider = self.provider_var.get()
        providers = self.app.opencode_config.get("provider", {})
        if provider in providers:
            models = providers[provider].get("models", {})
            if model_id in models:
                data = models[model_id]
                self.model_id_var.set(model_id)
                self.model_name_var.set(data.get("name", ""))
                self.attachment_var.set(data.get("attachment", True))

    def add_model(self):
        provider = self.provider_var.get()
        if not provider:
            return
        model_id = "new-model"
        models = self.app.opencode_config["provider"][provider].setdefault("models", {})
        models[model_id] = {"name": model_id, "attachment": True, "limit": {"context": 1048576, "output": 65535}, "modalities": {"input": ["text", "image"], "output": ["text"]}}
        self.app.mark_modified()
        self.refresh_models()

    def delete_model(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        model_id = item["values"][0]
        provider = self.provider_var.get()
        if messagebox.askyesno("确认", f"删除模型 [{model_id}]?"):
            del self.app.opencode_config["provider"][provider]["models"][model_id]
            self.app.mark_modified()
            self.refresh_models()

    def save_changes(self):
        provider = self.provider_var.get()
        model_id = self.model_id_var.get().strip()
        if not provider or not model_id:
            return
        models = self.app.opencode_config["provider"][provider].setdefault("models", {})
        models[model_id] = {"name": self.model_name_var.get() or model_id, "attachment": self.attachment_var.get(), "limit": {"context": 1048576, "output": 65535}, "modalities": {"input": ["text", "image"], "output": ["text"]}}
        self.app.mark_modified()
        self.refresh_models()
        messagebox.showinfo("成功", "已保存")



class AgentTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        left_frame = ttk.LabelFrame(self, text="Agent 列表", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=5)
        ttk.Button(toolbar, text="添加", command=self.add_agent).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_agent).pack(side=tk.LEFT, padx=2)
        columns = ("name", "model", "description")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=12)
        self.tree.heading("name", text="Agent 名称")
        self.tree.heading("model", text="绑定模型")
        self.tree.heading("description", text="描述")
        self.tree.column("name", width=100)
        self.tree.column("model", width=180)
        self.tree.column("description", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        right_frame = ttk.LabelFrame(self, text="Agent 详情", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Label(right_frame, text="Agent 名称:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.name_var, width=35).grid(row=0, column=1, pady=2)
        ttk.Label(right_frame, text="绑定模型:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(right_frame, textvariable=self.model_var, width=32)
        self.model_combo.grid(row=1, column=1, pady=2)
        ttk.Label(right_frame, text="描述:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.desc_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.desc_var, width=35).grid(row=2, column=1, pady=2)
        ttk.Button(right_frame, text="保存修改", command=self.save_changes).grid(row=3, column=1, pady=10)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        agents = self.app.ohmyopencode_config.get("agents", {})
        for name, data in agents.items():
            model = data.get("model", "")
            desc = data.get("description", "")
            self.tree.insert("", tk.END, values=(name, model, desc))
        registry = ModelRegistry(self.app.opencode_config)
        self.model_combo["values"] = registry.get_all_models()

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
            self.desc_var.set(data.get("description", ""))

    def add_agent(self):
        name = "new_agent"
        agents = self.app.ohmyopencode_config.setdefault("agents", {})
        agents[name] = {"model": "", "description": "新建 Agent"}
        self.app.mark_modified()
        self.refresh_list()

    def delete_agent(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        name = item["values"][0]
        if messagebox.askyesno("确认", f"删除 Agent [{name}]?"):
            del self.app.ohmyopencode_config["agents"][name]
            self.app.mark_modified()
            self.refresh_list()

    def save_changes(self):
        name = self.name_var.get().strip()
        if not name:
            return
        agents = self.app.ohmyopencode_config.setdefault("agents", {})
        agents[name] = {"model": self.model_var.get(), "description": self.desc_var.get()}
        self.app.mark_modified()
        self.refresh_list()
        messagebox.showinfo("成功", "已保存")



class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OpenCode 配置管理器 v0.1.0")
        self.root.geometry("1000x700")
        self.backup_manager = BackupManager()
        self.opencode_config = {}
        self.ohmyopencode_config = {}
        self.modified = False
        self.setup_menu()
        self.setup_toolbar()
        self.setup_notebook()
        self.setup_statusbar()
        self.load_configs()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件(F)", menu=file_menu)
        file_menu.add_command(label="保存", command=self.save_configs)
        file_menu.add_command(label="刷新", command=self.load_configs)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_close)
        self.root.bind("<Control-s>", lambda e: self.save_configs())

    def setup_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(toolbar, text="保存", command=self.save_configs).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="刷新", command=self.load_configs).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="备份", command=self.backup_configs).pack(side=tk.LEFT, padx=2)

    def setup_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.provider_tab = ProviderTab(self.notebook, self)
        self.model_tab = ModelTab(self.notebook, self)
        self.agent_tab = AgentTab(self.notebook, self)
        self.notebook.add(self.provider_tab, text="Provider")
        self.notebook.add(self.model_tab, text="Model")
        self.notebook.add(self.agent_tab, text="Agent")

    def setup_statusbar(self):
        self.statusbar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    def load_configs(self):
        self.opencode_config = ConfigManager.load_json(ConfigPaths.get_opencode_config()) or {}
        self.ohmyopencode_config = ConfigManager.load_json(ConfigPaths.get_ohmyopencode_config()) or {}
        self.provider_tab.refresh_list()
        self.model_tab.refresh_providers()
        self.agent_tab.refresh_list()
        self.modified = False
        self.statusbar.config(text="配置已加载")

    def save_configs(self):
        self.backup_manager.backup(ConfigPaths.get_opencode_config())
        self.backup_manager.backup(ConfigPaths.get_ohmyopencode_config())
        ConfigManager.save_json(ConfigPaths.get_opencode_config(), self.opencode_config)
        ConfigManager.save_json(ConfigPaths.get_ohmyopencode_config(), self.ohmyopencode_config)
        self.modified = False
        self.statusbar.config(text="配置已保存")
        messagebox.showinfo("成功", "配置已保存")

    def backup_configs(self):
        self.backup_manager.backup(ConfigPaths.get_opencode_config())
        self.backup_manager.backup(ConfigPaths.get_ohmyopencode_config())
        messagebox.showinfo("成功", "备份已创建")

    def mark_modified(self):
        self.modified = True
        self.statusbar.config(text="配置已修改 (未保存)")

    def on_close(self):
        if self.modified:
            if messagebox.askyesno("确认", "配置已修改但未保存，确定要退出吗？"):
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()



class CategoryTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        left_frame = ttk.LabelFrame(self, text="Category 列表", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=5)
        ttk.Button(toolbar, text="添加", command=self.add_category).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_category).pack(side=tk.LEFT, padx=2)
        columns = ("name", "model", "temp", "description")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=12)
        self.tree.heading("name", text="分类名称")
        self.tree.heading("model", text="绑定模型")
        self.tree.heading("temp", text="Temperature")
        self.tree.heading("description", text="描述")
        self.tree.column("name", width=100)
        self.tree.column("model", width=180)
        self.tree.column("temp", width=80)
        self.tree.column("description", width=120)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        right_frame = ttk.LabelFrame(self, text="Category 详情", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Label(right_frame, text="分类名称:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.name_var, width=35).grid(row=0, column=1, pady=2)
        ttk.Label(right_frame, text="绑定模型:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(right_frame, textvariable=self.model_var, width=32)
        self.model_combo.grid(row=1, column=1, pady=2)
        ttk.Label(right_frame, text="Temperature:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.temp_var = tk.DoubleVar(value=0.7)
        temp_frame = ttk.Frame(right_frame)
        temp_frame.grid(row=2, column=1, sticky=tk.W, pady=2)
        self.temp_scale = ttk.Scale(temp_frame, from_=0, to=2, variable=self.temp_var, orient=tk.HORIZONTAL, length=200)
        self.temp_scale.pack(side=tk.LEFT)
        self.temp_label = ttk.Label(temp_frame, text="0.7")
        self.temp_label.pack(side=tk.LEFT, padx=5)
        self.temp_var.trace("w", self.update_temp_label)
        ttk.Label(right_frame, text="描述:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.desc_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.desc_var, width=35).grid(row=3, column=1, pady=2)
        ttk.Button(right_frame, text="保存修改", command=self.save_changes).grid(row=4, column=1, pady=10)

    def update_temp_label(self, *args):
        self.temp_label.config(text=f"{self.temp_var.get():.2f}")

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        categories = self.app.ohmyopencode_config.get("categories", {})
        for name, data in categories.items():
            model = data.get("model", "")
            temp = data.get("temperature", 0.7)
            desc = data.get("description", "")
            self.tree.insert("", tk.END, values=(name, model, temp, desc))
        registry = ModelRegistry(self.app.opencode_config)
        self.model_combo["values"] = registry.get_all_models()

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
            self.temp_var.set(data.get("temperature", 0.7))
            self.desc_var.set(data.get("description", ""))

    def add_category(self):
        name = "new_category"
        categories = self.app.ohmyopencode_config.setdefault("categories", {})
        categories[name] = {"model": "", "temperature": 0.7, "description": "新建分类"}
        self.app.mark_modified()
        self.refresh_list()

    def delete_category(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        name = item["values"][0]
        if messagebox.askyesno("确认", f"删除 Category [{name}]?"):
            del self.app.ohmyopencode_config["categories"][name]
            self.app.mark_modified()
            self.refresh_list()

    def save_changes(self):
        name = self.name_var.get().strip()
        if not name:
            return
        categories = self.app.ohmyopencode_config.setdefault("categories", {})
        categories[name] = {"model": self.model_var.get(), "temperature": round(self.temp_var.get(), 2), "description": self.desc_var.get()}
        self.app.mark_modified()
        self.refresh_list()
        messagebox.showinfo("成功", "已保存")


class PermissionTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.setup_ui()

    def setup_ui(self):
        left_frame = ttk.LabelFrame(self, text="权限列表", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        toolbar = ttk.Frame(left_frame)
        toolbar.pack(fill=tk.X, pady=5)
        ttk.Button(toolbar, text="添加", command=self.add_permission).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="删除", command=self.delete_permission).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="全部允许", command=self.allow_all).pack(side=tk.RIGHT, padx=2)
        columns = ("tool", "permission")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=15)
        self.tree.heading("tool", text="工具名称")
        self.tree.heading("permission", text="权限")
        self.tree.column("tool", width=200)
        self.tree.column("permission", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        right_frame = ttk.LabelFrame(self, text="权限详情", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Label(right_frame, text="工具名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.tool_var = tk.StringVar()
        ttk.Entry(right_frame, textvariable=self.tool_var, width=30).grid(row=0, column=1, pady=5)
        ttk.Label(right_frame, text="权限:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.perm_var = tk.StringVar(value="allow")
        perm_combo = ttk.Combobox(right_frame, textvariable=self.perm_var, width=27)
        perm_combo["values"] = ("allow", "ask", "deny")
        perm_combo.grid(row=1, column=1, pady=5)
        ttk.Button(right_frame, text="保存修改", command=self.save_changes).grid(row=2, column=1, pady=10)
        ttk.Label(right_frame, text="常用工具:").grid(row=3, column=0, sticky=tk.W, pady=5)
        presets = ttk.Frame(right_frame)
        presets.grid(row=3, column=1, sticky=tk.W, pady=5)
        for tool in ["bash", "read", "edit", "write", "glob", "grep"]:
            ttk.Button(presets, text=tool, width=8, command=lambda t=tool: self.tool_var.set(t)).pack(side=tk.LEFT, padx=1)

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
        tool = item["values"][0]
        perm = item["values"][1]
        self.tool_var.set(tool)
        self.perm_var.set(perm)

    def add_permission(self):
        tool = "new_tool"
        permissions = self.app.opencode_config.setdefault("permission", {})
        permissions[tool] = "ask"
        self.app.mark_modified()
        self.refresh_list()

    def delete_permission(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        tool = item["values"][0]
        if messagebox.askyesno("确认", f"删除权限 [{tool}]?"):
            del self.app.opencode_config["permission"][tool]
            self.app.mark_modified()
            self.refresh_list()

    def allow_all(self):
        if messagebox.askyesno("确认", "将所有权限设为 allow?"):
            permissions = self.app.opencode_config.get("permission", {})
            for tool in permissions:
                permissions[tool] = "allow"
            self.app.mark_modified()
            self.refresh_list()

    def save_changes(self):
        tool = self.tool_var.get().strip()
        if not tool:
            return
        permissions = self.app.opencode_config.setdefault("permission", {})
        permissions[tool] = self.perm_var.get()
        self.app.mark_modified()
        self.refresh_list()
        messagebox.showinfo("成功", "已保存")


class ImportTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.import_service = ImportService()
        self.setup_ui()

    def setup_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(top_frame, text="检测外部配置并导入到 OpenCode").pack(side=tk.LEFT)
        ttk.Button(top_frame, text="刷新检测", command=self.scan_configs).pack(side=tk.RIGHT, padx=2)
        left_frame = ttk.LabelFrame(self, text="检测到的配置", padding=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        columns = ("source", "path", "status")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=10)
        self.tree.heading("source", text="来源")
        self.tree.heading("path", text="路径")
        self.tree.heading("status", text="状态")
        self.tree.column("source", width=120)
        self.tree.column("path", width=250)
        self.tree.column("status", width=80)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        right_frame = ttk.LabelFrame(self, text="配置预览", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.preview_text = scrolledtext.ScrolledText(right_frame, width=40, height=15, state=tk.DISABLED)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="导入选中配置", command=self.import_selected).pack(side=tk.LEFT, padx=5)
        self.scan_configs()

    def scan_configs(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        results = self.import_service.scan_external_configs()
        source_names = {"claude_settings": "Claude Code Settings", "claude_providers": "Claude Code Providers", "codex": "Codex"}
        for key, data in results.items():
            source = source_names.get(key, key)
            path = data.get("path", "")
            status = "已检测" if data.get("exists") else "未找到"
            self.tree.insert("", tk.END, values=(source, path, status), tags=(key,))

    def on_select(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        source = item["values"][0]
        results = self.import_service.scan_external_configs()
        key_map = {"Claude Code Settings": "claude_settings", "Claude Code Providers": "claude_providers", "Codex": "codex"}
        key = key_map.get(source, source)
        data = results.get(key, {})
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        if data.get("exists") and data.get("data"):
            self.preview_text.insert(tk.END, json.dumps(data["data"], indent=2, ensure_ascii=False))
        else:
            self.preview_text.insert(tk.END, "配置文件不存在或无法读取")
        self.preview_text.config(state=tk.DISABLED)

    def import_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要导入的配置")
            return
        item = self.tree.item(selection[0])
        source = item["values"][0]
        results = self.import_service.scan_external_configs()
        key_map = {"Claude Code Settings": "claude_settings", "Claude Code Providers": "claude_providers", "Codex": "codex"}
        key = key_map.get(source, source)
        data = results.get(key, {})
        if not data.get("exists") or not data.get("data"):
            messagebox.showwarning("提示", "该配置不存在或无法读取")
            return
        if key == "claude_providers":
            self.import_claude_providers(data["data"])
        else:
            messagebox.showinfo("提示", f"暂不支持导入 {source}")

    def import_claude_providers(self, data):
        if not isinstance(data, dict):
            return
        providers = self.app.opencode_config.setdefault("provider", {})
        imported = 0
        for name, provider_data in data.items():
            if name not in providers:
                providers[name] = {"npm": "@ai-sdk/anthropic", "name": name, "options": {"baseURL": provider_data.get("baseUrl", ""), "apiKey": provider_data.get("apiKey", "")}, "models": {}}
                imported += 1
        if imported > 0:
            self.app.mark_modified()
            messagebox.showinfo("成功", f"已导入 {imported} 个 Provider")
        else:
            messagebox.showinfo("提示", "没有新的 Provider 可导入")


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OpenCode 配置管理器 v0.2.0")
        self.root.geometry("1100x750")
        self.backup_manager = BackupManager()
        self.opencode_config = {}
        self.ohmyopencode_config = {}
        self.modified = False
        self.setup_menu()
        self.setup_toolbar()
        self.setup_notebook()
        self.setup_statusbar()
        self.load_configs()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件(F)", menu=file_menu)
        file_menu.add_command(label="保存", command=self.save_configs, accelerator="Ctrl+S")
        file_menu.add_command(label="刷新", command=self.load_configs, accelerator="F5")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_close)
        self.root.bind("<Control-s>", lambda e: self.save_configs())
        self.root.bind("<F5>", lambda e: self.load_configs())

    def setup_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(toolbar, text="保存", command=self.save_configs).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="刷新", command=self.load_configs).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="备份", command=self.backup_configs).pack(side=tk.LEFT, padx=2)

    def setup_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.provider_tab = ProviderTab(self.notebook, self)
        self.model_tab = ModelTab(self.notebook, self)
        self.agent_tab = AgentTab(self.notebook, self)
        self.category_tab = CategoryTab(self.notebook, self)
        self.permission_tab = PermissionTab(self.notebook, self)
        self.import_tab = ImportTab(self.notebook, self)
        self.notebook.add(self.provider_tab, text="Provider")
        self.notebook.add(self.model_tab, text="Model")
        self.notebook.add(self.agent_tab, text="Agent")
        self.notebook.add(self.category_tab, text="Category")
        self.notebook.add(self.permission_tab, text="权限")
        self.notebook.add(self.import_tab, text="导入")

    def setup_statusbar(self):
        self.statusbar = ttk.Label(self.root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    def load_configs(self):
        self.opencode_config = ConfigManager.load_json(ConfigPaths.get_opencode_config()) or {}
        self.ohmyopencode_config = ConfigManager.load_json(ConfigPaths.get_ohmyopencode_config()) or {}
        self.provider_tab.refresh_list()
        self.model_tab.refresh_providers()
        self.agent_tab.refresh_list()
        self.category_tab.refresh_list()
        self.permission_tab.refresh_list()
        self.modified = False
        providers = len(self.opencode_config.get("provider", {}))
        agents = len(self.ohmyopencode_config.get("agents", {}))
        self.statusbar.config(text=f"配置已加载 | Provider: {providers} | Agent: {agents}")

    def save_configs(self):
        self.backup_manager.backup(ConfigPaths.get_opencode_config())
        self.backup_manager.backup(ConfigPaths.get_ohmyopencode_config())
        ConfigManager.save_json(ConfigPaths.get_opencode_config(), self.opencode_config)
        ConfigManager.save_json(ConfigPaths.get_ohmyopencode_config(), self.ohmyopencode_config)
        self.modified = False
        self.statusbar.config(text="配置已保存")
        messagebox.showinfo("成功", "配置已保存")

    def backup_configs(self):
        self.backup_manager.backup(ConfigPaths.get_opencode_config())
        self.backup_manager.backup(ConfigPaths.get_ohmyopencode_config())
        messagebox.showinfo("成功", "备份已创建")

    def mark_modified(self):
        self.modified = True
        self.statusbar.config(text="配置已修改 (未保存)")

    def on_close(self):
        if self.modified:
            if messagebox.askyesno("确认", "配置已修改但未保存，确定要退出吗？"):
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()


if __name__ == "__main__":
    app = MainWindow()
    app.run()


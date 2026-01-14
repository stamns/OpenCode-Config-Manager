# -*- coding: utf-8 -*-
"""追加代码到 opencode_config_manager_fluent_v1.0.0.py"""

content = '''

# ==================== Oh My Agent 页面 ====================
class OhMyAgentPage(BasePage):
    """Oh My OpenCode Agent 管理页面"""
    
    def __init__(self, main_window, parent=None):
        super().__init__("Oh My Agent", parent)
        self.main_window = main_window
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.add_btn = PrimaryPushButton(FIF.ADD, "添加 Agent", self)
        self.add_btn.clicked.connect(self._on_add)
        toolbar.addWidget(self.add_btn)
        
        self.preset_btn = PushButton(FIF.LIBRARY, "从预设添加", self)
        self.preset_btn.clicked.connect(self._on_add_preset)
        toolbar.addWidget(self.preset_btn)
        
        self.edit_btn = PushButton(FIF.EDIT, "编辑", self)
        self.edit_btn.clicked.connect(self._on_edit)
        toolbar.addWidget(self.edit_btn)
        
        self.delete_btn = PushButton(FIF.DELETE, "删除", self)
        self.delete_btn.clicked.connect(self._on_delete)
        toolbar.addWidget(self.delete_btn)
        
        toolbar.addStretch()
        self.layout.addLayout(toolbar)
        
        # Agent 列表
        self.table = TableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["名称", "绑定模型", "描述"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.layout.addWidget(self.table)
    
    def _load_data(self):
        """加载 Agent 数据"""
        self.table.setRowCount(0)
        config = self.main_window.ohmyopencode_config or {}
        agents = config.get("agents", {})
        
        for name, data in agents.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(data.get("model", "")))
            self.table.setItem(row, 2, QTableWidgetItem(data.get("description", "")[:50]))
    
    def _on_add(self):
        """添加 Agent"""
        dialog = OhMyAgentDialog(self.main_window, parent=self)
        if dialog.exec_():
            self._load_data()
            self.show_success("成功", "Agent 已添加")
    
    def _on_add_preset(self):
        """从预设添加 Agent"""
        dialog = PresetOhMyAgentDialog(self.main_window, parent=self)
        if dialog.exec_():
            self._load_data()
            self.show_success("成功", "预设 Agent 已添加")
    
    def _on_edit(self):
        """编辑 Agent"""
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("提示", "请先选择一个 Agent")
            return
        
        name = self.table.item(row, 0).text()
        dialog = OhMyAgentDialog(self.main_window, agent_name=name, parent=self)
        if dialog.exec_():
            self._load_data()
            self.show_success("成功", "Agent 已更新")
    
    def _on_delete(self):
        """删除 Agent"""
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("提示", "请先选择一个 Agent")
            return
        
        name = self.table.item(row, 0).text()
        w = FluentMessageBox("确认删除", f'确定要删除 Agent "{name}" 吗？', self)
        if w.exec_():
            config = self.main_window.ohmyopencode_config or {}
            if "agents" in config and name in config["agents"]:
                del config["agents"][name]
                self.main_window.save_ohmyopencode_config()
                self._load_data()
                self.show_success("成功", f'Agent "{name}" 已删除')


class OhMyAgentDialog(QDialog):
    """Oh My Agent 编辑对话框"""
    
    def __init__(self, main_window, agent_name: str = None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.agent_name = agent_name
        self.is_edit = agent_name is not None
        
        self.setWindowTitle("编辑 Agent" if self.is_edit else "添加 Agent")
        self.setMinimumWidth(450)
        self._setup_ui()
        
        if self.is_edit:
            self._load_agent_data()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Agent 名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(BodyLabel("Agent 名称:", self))
        self.name_edit = LineEdit(self)
        self.name_edit.setPlaceholderText("如: oracle, librarian, explore")
        if self.is_edit:
            self.name_edit.setEnabled(False)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 绑定模型
        model_layout = QHBoxLayout()
        model_layout.addWidget(BodyLabel("绑定模型:", self))
        self.model_combo = ComboBox(self)
        self._load_models()
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)
        
        # 描述
        layout.addWidget(BodyLabel("描述:", self))
        self.desc_edit = TextEdit(self)
        self.desc_edit.setPlaceholderText("描述 Agent 的功能和适用场景")
        self.desc_edit.setMaximumHeight(100)
        layout.addWidget(self.desc_edit)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = PushButton("取消", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.save_btn = PrimaryPushButton("保存", self)
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_models(self):
        """加载可用模型列表"""
        self.model_combo.clear()
        registry = ModelRegistry(self.main_window.opencode_config)
        models = registry.get_all_models()
        self.model_combo.addItems(models)
    
    def _load_agent_data(self):
        config = self.main_window.ohmyopencode_config or {}
        agent = config.get("agents", {}).get(self.agent_name, {})
        
        self.name_edit.setText(self.agent_name)
        
        model = agent.get("model", "")
        if model:
            self.model_combo.setCurrentText(model)
        
        self.desc_edit.setPlainText(agent.get("description", ""))
    
    def _on_save(self):
        name = self.name_edit.text().strip()
        if not name:
            InfoBar.error("错误", "请输入 Agent 名称", parent=self)
            return
        
        config = self.main_window.ohmyopencode_config
        if config is None:
            config = {}
            self.main_window.ohmyopencode_config = config
        
        if "agents" not in config:
            config["agents"] = {}
        
        # 检查名称冲突
        if not self.is_edit and name in config["agents"]:
            InfoBar.error("错误", f'Agent "{name}" 已存在', parent=self)
            return
        
        # 保存数据
        config["agents"][name] = {
            "model": self.model_combo.currentText(),
            "description": self.desc_edit.toPlainText().strip(),
        }
        
        self.main_window.save_ohmyopencode_config()
        self.accept()


class PresetOhMyAgentDialog(QDialog):
    """预设 Oh My Agent 选择对话框"""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        self.setWindowTitle("从预设添加 Agent")
        self.setMinimumWidth(500)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        layout.addWidget(SubtitleLabel("选择预设 Agent", self))
        
        # 预设列表
        self.list_widget = ListWidget(self)
        for name, desc in PRESET_AGENTS.items():
            self.list_widget.addItem(f"{name} - {desc}")
        layout.addWidget(self.list_widget)
        
        # 绑定模型
        model_layout = QHBoxLayout()
        model_layout.addWidget(BodyLabel("绑定模型:", self))
        self.model_combo = ComboBox(self)
        self._load_models()
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = PushButton("取消", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.add_btn = PrimaryPushButton("添加", self)
        self.add_btn.clicked.connect(self._on_add)
        btn_layout.addWidget(self.add_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_models(self):
        self.model_combo.clear()
        registry = ModelRegistry(self.main_window.opencode_config)
        models = registry.get_all_models()
        self.model_combo.addItems(models)
    
    def _on_add(self):
        current = self.list_widget.currentItem()
        if not current:
            InfoBar.warning("提示", "请选择一个预设 Agent", parent=self)
            return
        
        # 解析选中的预设
        text = current.text()
        name = text.split(" - ")[0]
        desc = PRESET_AGENTS.get(name, "")
        
        config = self.main_window.ohmyopencode_config
        if config is None:
            config = {}
            self.main_window.ohmyopencode_config = config
        
        if "agents" not in config:
            config["agents"] = {}
        
        if name in config["agents"]:
            InfoBar.warning("提示", f'Agent "{name}" 已存在', parent=self)
            return
        
        config["agents"][name] = {
            "model": self.model_combo.currentText(),
            "description": desc,
        }
        
        self.main_window.save_ohmyopencode_config()
        self.accept()


# ==================== Category 页面 ====================
class CategoryPage(BasePage):
    """Category 管理页面"""
    
    def __init__(self, main_window, parent=None):
        super().__init__("Category 管理", parent)
        self.main_window = main_window
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        # 工具栏
        toolbar = QHBoxLayout()
        
        self.add_btn = PrimaryPushButton(FIF.ADD, "添加 Category", self)
        self.add_btn.clicked.connect(self._on_add)
        toolbar.addWidget(self.add_btn)
        
        self.preset_btn = PushButton(FIF.LIBRARY, "从预设添加", self)
        self.preset_btn.clicked.connect(self._on_add_preset)
        toolbar.addWidget(self.preset_btn)
        
        self.edit_btn = PushButton(FIF.EDIT, "编辑", self)
        self.edit_btn.clicked.connect(self._on_edit)
        toolbar.addWidget(self.edit_btn)
        
        self.delete_btn = PushButton(FIF.DELETE, "删除", self)
        self.delete_btn.clicked.connect(self._on_delete)
        toolbar.addWidget(self.delete_btn)
        
        toolbar.addStretch()
        self.layout.addLayout(toolbar)
        
        # Category 列表
        self.table = TableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["名称", "绑定模型", "Temperature", "描述"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.layout.addWidget(self.table)
    
    def _load_data(self):
        """加载 Category 数据"""
        self.table.setRowCount(0)
        config = self.main_window.ohmyopencode_config or {}
        categories = config.get("categories", {})
        
        for name, data in categories.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(data.get("model", "")))
            self.table.setItem(row, 2, QTableWidgetItem(str(data.get("temperature", 0.7))))
            self.table.setItem(row, 3, QTableWidgetItem(data.get("description", "")[:30]))
    
    def _on_add(self):
        dialog = CategoryDialog(self.main_window, parent=self)
        if dialog.exec_():
            self._load_data()
            self.show_success("成功", "Category 已添加")
    
    def _on_add_preset(self):
        dialog = PresetCategoryDialog(self.main_window, parent=self)
        if dialog.exec_():
            self._load_data()
            self.show_success("成功", "预设 Category 已添加")
    
    def _on_edit(self):
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("提示", "请先选择一个 Category")
            return
        
        name = self.table.item(row, 0).text()
        dialog = CategoryDialog(self.main_window, category_name=name, parent=self)
        if dialog.exec_():
            self._load_data()
            self.show_success("成功", "Category 已更新")
    
    def _on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("提示", "请先选择一个 Category")
            return
        
        name = self.table.item(row, 0).text()
        w = FluentMessageBox("确认删除", f'确定要删除 Category "{name}" 吗？', self)
        if w.exec_():
            config = self.main_window.ohmyopencode_config or {}
            if "categories" in config and name in config["categories"]:
                del config["categories"][name]
                self.main_window.save_ohmyopencode_config()
                self._load_data()
                self.show_success("成功", f'Category "{name}" 已删除')


class CategoryDialog(QDialog):
    """Category 编辑对话框"""
    
    def __init__(self, main_window, category_name: str = None, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.category_name = category_name
        self.is_edit = category_name is not None
        
        self.setWindowTitle("编辑 Category" if self.is_edit else "添加 Category")
        self.setMinimumWidth(450)
        self._setup_ui()
        
        if self.is_edit:
            self._load_category_data()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Category 名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(BodyLabel("Category 名称:", self))
        self.name_edit = LineEdit(self)
        self.name_edit.setPlaceholderText("如: visual, business-logic")
        if self.is_edit:
            self.name_edit.setEnabled(False)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # 绑定模型
        model_layout = QHBoxLayout()
        model_layout.addWidget(BodyLabel("绑定模型:", self))
        self.model_combo = ComboBox(self)
        self._load_models()
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)
        
        # Temperature 滑块
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(BodyLabel("Temperature:", self))
        self.temp_slider = Slider(Qt.Horizontal, self)
        self.temp_slider.setRange(0, 200)  # 0.0 - 2.0
        self.temp_slider.setValue(70)  # 默认 0.7
        self.temp_slider.valueChanged.connect(self._on_temp_changed)
        temp_layout.addWidget(self.temp_slider)
        self.temp_label = BodyLabel("0.7", self)
        self.temp_label.setMinimumWidth(40)
        temp_layout.addWidget(self.temp_label)
        layout.addLayout(temp_layout)
        
        # 描述
        layout.addWidget(BodyLabel("描述:", self))
        self.desc_edit = TextEdit(self)
        self.desc_edit.setPlaceholderText("描述该分类的用途和适用场景")
        self.desc_edit.setMaximumHeight(80)
        layout.addWidget(self.desc_edit)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = PushButton("取消", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.save_btn = PrimaryPushButton("保存", self)
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
    
    def _on_temp_changed(self, value):
        self.temp_label.setText(f"{value / 100:.1f}")
    
    def _load_models(self):
        self.model_combo.clear()
        registry = ModelRegistry(self.main_window.opencode_config)
        models = registry.get_all_models()
        self.model_combo.addItems(models)
    
    def _load_category_data(self):
        config = self.main_window.ohmyopencode_config or {}
        category = config.get("categories", {}).get(self.category_name, {})
        
        self.name_edit.setText(self.category_name)
        
        model = category.get("model", "")
        if model:
            self.model_combo.setCurrentText(model)
        
        temp = category.get("temperature", 0.7)
        self.temp_slider.setValue(int(temp * 100))
        self.temp_label.setText(f"{temp:.1f}")
        
        self.desc_edit.setPlainText(category.get("description", ""))
    
    def _on_save(self):
        name = self.name_edit.text().strip()
        if not name:
            InfoBar.error("错误", "请输入 Category 名称", parent=self)
            return
        
        config = self.main_window.ohmyopencode_config
        if config is None:
            config = {}
            self.main_window.ohmyopencode_config = config
        
        if "categories" not in config:
            config["categories"] = {}
        
        if not self.is_edit and name in config["categories"]:
            InfoBar.error("错误", f'Category "{name}" 已存在', parent=self)
            return
        
        config["categories"][name] = {
            "model": self.model_combo.currentText(),
            "temperature": round(self.temp_slider.value() / 100, 1),
            "description": self.desc_edit.toPlainText().strip(),
        }
        
        self.main_window.save_ohmyopencode_config()
        self.accept()


class PresetCategoryDialog(QDialog):
    """预设 Category 选择对话框"""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        
        self.setWindowTitle("从预设添加 Category")
        self.setMinimumWidth(500)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        layout.addWidget(SubtitleLabel("选择预设 Category", self))
        
        # 预设列表
        self.list_widget = ListWidget(self)
        for name, data in PRESET_CATEGORIES.items():
            temp = data.get("temperature", 0.7)
            desc = data.get("description", "")
            self.list_widget.addItem(f"{name} (temp={temp}) - {desc}")
        layout.addWidget(self.list_widget)
        
        # 绑定模型
        model_layout = QHBoxLayout()
        model_layout.addWidget(BodyLabel("绑定模型:", self))
        self.model_combo = ComboBox(self)
        self._load_models()
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = PushButton("取消", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.add_btn = PrimaryPushButton("添加", self)
        self.add_btn.clicked.connect(self._on_add)
        btn_layout.addWidget(self.add_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_models(self):
        self.model_combo.clear()
        registry = ModelRegistry(self.main_window.opencode_config)
        models = registry.get_all_models()
        self.model_combo.addItems(models)
    
    def _on_add(self):
        current = self.list_widget.currentItem()
        if not current:
            InfoBar.warning("提示", "请选择一个预设 Category", parent=self)
            return
        
        text = current.text()
        name = text.split(" (temp=")[0]
        preset = PRESET_CATEGORIES.get(name, {})
        
        config = self.main_window.ohmyopencode_config
        if config is None:
            config = {}
            self.main_window.ohmyopencode_config = config
        
        if "categories" not in config:
            config["categories"] = {}
        
        if name in config["categories"]:
            InfoBar.warning("提示", f'Category "{name}" 已存在', parent=self)
            return
        
        config["categories"][name] = {
            "model": self.model_combo.currentText(),
            "temperature": preset.get("temperature", 0.7),
            "description": preset.get("description", ""),
        }
        
        self.main_window.save_ohmyopencode_config()
        self.accept()

'''

# 读取原文件
with open(
    r"D:\opcdcfg\opencode_config_manager_fluent_v1.0.0.py", "r", encoding="utf-8"
) as f:
    original = f.read()

# 找到插入点 (在 "# ==================== 程序入口 ====================" 之前)
insert_marker = "# ==================== 程序入口 ===================="
if insert_marker in original:
    parts = original.split(insert_marker)
    new_content = parts[0] + content + "\n\n" + insert_marker + parts[1]

    with open(
        r"D:\opcdcfg\opencode_config_manager_fluent_v1.0.0.py", "w", encoding="utf-8"
    ) as f:
        f.write(new_content)
    print("成功追加 OhMyAgentPage 和 CategoryPage 代码")
else:
    print("未找到插入点标记")

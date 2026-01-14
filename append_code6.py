# -*- coding: utf-8 -*-
"""追加 SkillPage, RulesPage, CompactionPage 代码"""

content = '''

# ==================== Skill 页面 ====================
class SkillPage(BasePage):
    """Skill 权限配置和 SKILL.md 创建页面"""
    
    def __init__(self, main_window, parent=None):
        super().__init__("Skill 管理", parent)
        self.main_window = main_window
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        # 说明卡片
        desc_card = self.add_card("Skill 权限配置")
        desc_layout = desc_card.layout()
        desc_layout.addWidget(BodyLabel(
            "配置 Skill 的加载权限。Skill 是可复用的指令文件，Agent 可按需加载。",
            desc_card
        ))
        
        # 权限列表工具栏
        toolbar = QHBoxLayout()
        
        self.add_btn = PrimaryPushButton(FIF.ADD, "添加权限", self)
        self.add_btn.clicked.connect(self._on_add)
        toolbar.addWidget(self.add_btn)
        
        self.delete_btn = PushButton(FIF.DELETE, "删除", self)
        self.delete_btn.clicked.connect(self._on_delete)
        toolbar.addWidget(self.delete_btn)
        
        toolbar.addStretch()
        self.layout.addLayout(toolbar)
        
        # 权限列表
        self.table = TableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["模式", "权限"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self._on_select)
        self.layout.addWidget(self.table)
        
        # 编辑区域
        edit_card = self.add_card("编辑权限")
        edit_layout = edit_card.layout()
        
        # 模式输入
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(BodyLabel("模式:", edit_card))
        self.pattern_edit = LineEdit(edit_card)
        self.pattern_edit.setPlaceholderText("如: *, internal-*, my-skill")
        pattern_layout.addWidget(self.pattern_edit)
        edit_layout.addLayout(pattern_layout)
        
        # 权限选择
        perm_layout = QHBoxLayout()
        perm_layout.addWidget(BodyLabel("权限:", edit_card))
        self.perm_combo = ComboBox(edit_card)
        self.perm_combo.addItems(["allow", "ask", "deny"])
        perm_layout.addWidget(self.perm_combo)
        perm_layout.addStretch()
        edit_layout.addLayout(perm_layout)
        
        # 保存按钮
        save_btn = PrimaryPushButton("保存权限", edit_card)
        save_btn.clicked.connect(self._on_save)
        edit_layout.addWidget(save_btn)
        
        # 创建 SKILL.md 卡片
        create_card = self.add_card("创建 SKILL.md")
        create_layout = create_card.layout()
        
        # Skill 名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(BodyLabel("Skill 名称:", create_card))
        self.skill_name_edit = LineEdit(create_card)
        self.skill_name_edit.setPlaceholderText("小写字母、数字、连字符，如: git-release")
        name_layout.addWidget(self.skill_name_edit)
        create_layout.addLayout(name_layout)
        
        # Skill 描述
        desc_layout2 = QHBoxLayout()
        desc_layout2.addWidget(BodyLabel("描述:", create_card))
        self.skill_desc_edit = LineEdit(create_card)
        self.skill_desc_edit.setPlaceholderText("描述 Skill 的功能")
        desc_layout2.addWidget(self.skill_desc_edit)
        create_layout.addLayout(desc_layout2)
        
        # Skill 内容
        create_layout.addWidget(BodyLabel("Skill 内容 (Markdown):", create_card))
        self.skill_content_edit = TextEdit(create_card)
        self.skill_content_edit.setPlaceholderText("## What I do\\n- 描述功能\\n\\n## Instructions\\n- 具体指令")
        self.skill_content_edit.setMaximumHeight(150)
        create_layout.addWidget(self.skill_content_edit)
        
        # 保存位置
        loc_layout = QHBoxLayout()
        loc_layout.addWidget(BodyLabel("保存位置:", create_card))
        self.global_radio = RadioButton("全局 (~/.config/opencode/skill/)", create_card)
        self.global_radio.setChecked(True)
        loc_layout.addWidget(self.global_radio)
        self.project_radio = RadioButton("项目 (.opencode/skill/)", create_card)
        loc_layout.addWidget(self.project_radio)
        loc_layout.addStretch()
        create_layout.addLayout(loc_layout)
        
        # 创建按钮
        create_btn = PrimaryPushButton("创建 SKILL.md", create_card)
        create_btn.clicked.connect(self._on_create_skill)
        create_layout.addWidget(create_btn)
        
        self.layout.addStretch()
    
    def _load_data(self):
        """加载 Skill 权限数据"""
        self.table.setRowCount(0)
        config = self.main_window.opencode_config or {}
        permissions = config.get("permission", {}).get("skill", {})
        
        if isinstance(permissions, dict):
            for pattern, perm in permissions.items():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(pattern))
                self.table.setItem(row, 1, QTableWidgetItem(perm))
        elif isinstance(permissions, str):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem("*"))
            self.table.setItem(row, 1, QTableWidgetItem(permissions))
    
    def _on_select(self):
        row = self.table.currentRow()
        if row >= 0:
            pattern_item = self.table.item(row, 0)
            perm_item = self.table.item(row, 1)
            if pattern_item:
                self.pattern_edit.setText(pattern_item.text())
            if perm_item:
                self.perm_combo.setCurrentText(perm_item.text())
    
    def _on_add(self):
        self.pattern_edit.setText("")
        self.perm_combo.setCurrentText("ask")
    
    def _on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            self.show_warning("提示", "请先选择一个权限")
            return
        
        pattern = self.table.item(row, 0).text()
        w = FluentMessageBox("确认删除", f'确定要删除 Skill 权限 "{pattern}" 吗？', self)
        if w.exec_():
            config = self.main_window.opencode_config or {}
            skill_perms = config.get("permission", {}).get("skill", {})
            if isinstance(skill_perms, dict) and pattern in skill_perms:
                del skill_perms[pattern]
                self.main_window.save_opencode_config()
                self._load_data()
                self.show_success("成功", f'权限 "{pattern}" 已删除')
    
    def _on_save(self):
        pattern = self.pattern_edit.text().strip()
        if not pattern:
            self.show_warning("提示", "请输入模式")
            return
        
        config = self.main_window.opencode_config
        if config is None:
            config = {}
            self.main_window.opencode_config = config
        
        if "permission" not in config:
            config["permission"] = {}
        if "skill" not in config["permission"] or not isinstance(config["permission"]["skill"], dict):
            config["permission"]["skill"] = {}
        
        config["permission"]["skill"][pattern] = self.perm_combo.currentText()
        self.main_window.save_opencode_config()
        self._load_data()
        self.show_success("成功", f'Skill 权限 "{pattern}" 已保存')
    
    def _on_create_skill(self):
        name = self.skill_name_edit.text().strip()
        desc = self.skill_desc_edit.text().strip()
        content = self.skill_content_edit.toPlainText().strip()
        
        if not name:
            self.show_warning("提示", "请输入 Skill 名称")
            return
        if not desc:
            self.show_warning("提示", "请输入 Skill 描述")
            return
        
        # 验证名称格式
        import re
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            self.show_error("错误", "Skill 名称格式错误！要求：小写字母、数字、连字符")
            return
        
        # 确定保存路径
        if self.global_radio.isChecked():
            base_path = Path.home() / ".config" / "opencode" / "skill"
        else:
            base_path = Path.cwd() / ".opencode" / "skill"
        
        skill_dir = base_path / name
        skill_file = skill_dir / "SKILL.md"
        
        try:
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_content = f"""---
name: {name}
description: {desc}
---

{content if content else "## What I do\\n- 描述功能\\n\\n## Instructions\\n- 具体指令"}
"""
            with open(skill_file, "w", encoding="utf-8") as f:
                f.write(skill_content)
            
            self.show_success("成功", f"Skill 已创建: {skill_file}")
        except Exception as e:
            self.show_error("错误", f"创建失败: {e}")


# ==================== Rules 页面 ====================
class RulesPage(BasePage):
    """Rules/Instructions 管理和 AGENTS.md 编辑页面"""
    
    def __init__(self, main_window, parent=None):
        super().__init__("Rules 管理", parent)
        self.main_window = main_window
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        # Instructions 配置卡片
        inst_card = self.add_card("Instructions 配置")
        inst_layout = inst_card.layout()
        
        inst_layout.addWidget(BodyLabel(
            "配置额外的指令文件，这些文件会与 AGENTS.md 合并加载。",
            inst_card
        ))
        
        # Instructions 列表
        self.inst_list = ListWidget(inst_card)
        self.inst_list.setMaximumHeight(120)
        inst_layout.addWidget(self.inst_list)
        
        # 添加输入
        add_layout = QHBoxLayout()
        self.inst_path_edit = LineEdit(inst_card)
        self.inst_path_edit.setPlaceholderText("文件路径，如: CONTRIBUTING.md, docs/*.md")
        add_layout.addWidget(self.inst_path_edit)
        
        add_btn = PushButton(FIF.ADD, "添加", inst_card)
        add_btn.clicked.connect(self._on_add_instruction)
        add_layout.addWidget(add_btn)
        
        del_btn = PushButton(FIF.DELETE, "删除", inst_card)
        del_btn.clicked.connect(self._on_delete_instruction)
        add_layout.addWidget(del_btn)
        
        inst_layout.addLayout(add_layout)
        
        # 快捷路径
        quick_layout = QHBoxLayout()
        quick_layout.addWidget(BodyLabel("快捷:", inst_card))
        for path in ["CONTRIBUTING.md", "docs/*.md", ".cursor/rules/*.md"]:
            btn = PushButton(path, inst_card)
            btn.clicked.connect(lambda checked, p=path: self.inst_path_edit.setText(p))
            quick_layout.addWidget(btn)
        quick_layout.addStretch()
        inst_layout.addLayout(quick_layout)
        
        # 保存按钮
        save_inst_btn = PrimaryPushButton("保存 Instructions", inst_card)
        save_inst_btn.clicked.connect(self._on_save_instructions)
        inst_layout.addWidget(save_inst_btn)
        
        # AGENTS.md 编辑卡片
        agents_card = self.add_card("AGENTS.md 编辑")
        agents_layout = agents_card.layout()
        
        # 位置选择
        loc_layout = QHBoxLayout()
        loc_layout.addWidget(BodyLabel("编辑位置:", agents_card))
        self.global_radio = RadioButton("全局", agents_card)
        self.global_radio.setChecked(True)
        self.global_radio.clicked.connect(self._load_agents_md)
        loc_layout.addWidget(self.global_radio)
        self.project_radio = RadioButton("项目", agents_card)
        self.project_radio.clicked.connect(self._load_agents_md)
        loc_layout.addWidget(self.project_radio)
        loc_layout.addStretch()
        agents_layout.addLayout(loc_layout)
        
        # 路径显示
        self.path_label = CaptionLabel("", agents_card)
        agents_layout.addWidget(self.path_label)
        
        # 编辑器
        self.agents_edit = TextEdit(agents_card)
        self.agents_edit.setMinimumHeight(200)
        agents_layout.addWidget(self.agents_edit)
        
        # 按钮
        btn_layout = QHBoxLayout()
        save_btn = PrimaryPushButton("保存 AGENTS.md", agents_card)
        save_btn.clicked.connect(self._on_save_agents_md)
        btn_layout.addWidget(save_btn)
        
        reload_btn = PushButton("重新加载", agents_card)
        reload_btn.clicked.connect(self._load_agents_md)
        btn_layout.addWidget(reload_btn)
        
        template_btn = PushButton("使用模板", agents_card)
        template_btn.clicked.connect(self._use_template)
        btn_layout.addWidget(template_btn)
        
        btn_layout.addStretch()
        agents_layout.addLayout(btn_layout)
        
        self.layout.addStretch()
        
        # 初始加载
        self._load_agents_md()
    
    def _load_data(self):
        """加载 Instructions 列表"""
        self.inst_list.clear()
        config = self.main_window.opencode_config or {}
        instructions = config.get("instructions", [])
        for path in instructions:
            self.inst_list.addItem(path)
    
    def _on_add_instruction(self):
        path = self.inst_path_edit.text().strip()
        if not path:
            self.show_warning("提示", "请输入文件路径")
            return
        
        config = self.main_window.opencode_config
        if config is None:
            config = {}
            self.main_window.opencode_config = config
        
        instructions = config.setdefault("instructions", [])
        if path not in instructions:
            instructions.append(path)
            self._load_data()
            self.inst_path_edit.setText("")
    
    def _on_delete_instruction(self):
        current = self.inst_list.currentItem()
        if not current:
            self.show_warning("提示", "请先选择一个路径")
            return
        
        path = current.text()
        config = self.main_window.opencode_config or {}
        instructions = config.get("instructions", [])
        if path in instructions:
            instructions.remove(path)
            self._load_data()
    
    def _on_save_instructions(self):
        self.main_window.save_opencode_config()
        self.show_success("成功", "Instructions 配置已保存")
    
    def _get_agents_path(self) -> Path:
        if self.global_radio.isChecked():
            return Path.home() / ".config" / "opencode" / "AGENTS.md"
        else:
            return Path.cwd() / "AGENTS.md"
    
    def _load_agents_md(self):
        path = self._get_agents_path()
        self.path_label.setText(f"路径: {path}")
        
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.agents_edit.setPlainText(content)
            except Exception as e:
                self.agents_edit.setPlainText(f"# 读取失败: {e}")
        else:
            self.agents_edit.setPlainText('# AGENTS.md 文件不存在\\n# 点击"使用模板"创建新文件')
    
    def _on_save_agents_md(self):
        path = self._get_agents_path()
        content = self.agents_edit.toPlainText()
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self.show_success("成功", f"AGENTS.md 已保存: {path}")
        except Exception as e:
            self.show_error("错误", f"保存失败: {e}")
    
    def _use_template(self):
        template = """# Project Rules

This is a project-specific rules file for OpenCode.

## Project Structure
- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation

## Code Standards
- Use TypeScript with strict mode enabled
- Follow existing code patterns
- Write tests for new features

## Conventions
- Use meaningful variable names
- Add comments for complex logic
- Keep functions small and focused
"""
        self.agents_edit.setPlainText(template)


# ==================== Compaction 页面 ====================
class CompactionPage(BasePage):
    """上下文压缩配置页面"""
    
    def __init__(self, main_window, parent=None):
        super().__init__("Compaction 配置", parent)
        self.main_window = main_window
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        # 说明卡片
        desc_card = self.add_card("上下文压缩 (Compaction)")
        desc_layout = desc_card.layout()
        
        desc_layout.addWidget(BodyLabel(
            "上下文压缩用于在会话上下文接近满时自动压缩，以节省 tokens 并保持会话连续性。",
            desc_card
        ))
        
        # auto 选项
        self.auto_check = CheckBox("自动压缩 (auto) - 当上下文已满时自动压缩会话", desc_card)
        self.auto_check.setChecked(True)
        desc_layout.addWidget(self.auto_check)
        
        # prune 选项
        self.prune_check = CheckBox("修剪旧输出 (prune) - 删除旧的工具输出以节省 tokens", desc_card)
        self.prune_check.setChecked(True)
        desc_layout.addWidget(self.prune_check)
        
        # 保存按钮
        save_btn = PrimaryPushButton("保存设置", desc_card)
        save_btn.clicked.connect(self._on_save)
        desc_layout.addWidget(save_btn)
        
        # 配置预览卡片
        preview_card = self.add_card("配置预览")
        preview_layout = preview_card.layout()
        
        self.preview_edit = TextEdit(preview_card)
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setMaximumHeight(150)
        preview_layout.addWidget(self.preview_edit)
        
        self.layout.addStretch()
        
        # 连接信号更新预览
        self.auto_check.stateChanged.connect(self._update_preview)
        self.prune_check.stateChanged.connect(self._update_preview)
    
    def _load_data(self):
        """加载 Compaction 配置"""
        config = self.main_window.opencode_config or {}
        compaction = config.get("compaction", {})
        
        self.auto_check.setChecked(compaction.get("auto", True))
        self.prune_check.setChecked(compaction.get("prune", True))
        
        self._update_preview()
    
    def _update_preview(self):
        """更新配置预览"""
        import json
        config = {
            "compaction": {
                "auto": self.auto_check.isChecked(),
                "prune": self.prune_check.isChecked()
            }
        }
        self.preview_edit.setPlainText(json.dumps(config, indent=2, ensure_ascii=False))
    
    def _on_save(self):
        config = self.main_window.opencode_config
        if config is None:
            config = {}
            self.main_window.opencode_config = config
        
        config["compaction"] = {
            "auto": self.auto_check.isChecked(),
            "prune": self.prune_check.isChecked()
        }
        
        self.main_window.save_opencode_config()
        self._update_preview()
        self.show_success("成功", "上下文压缩配置已保存")

'''

# 读取原文件
with open(
    r"D:\opcdcfg\opencode_config_manager_fluent_v1.0.0.py", "r", encoding="utf-8"
) as f:
    original = f.read()

# 找到插入点
insert_marker = "# ==================== 程序入口 ===================="
if insert_marker in original:
    parts = original.split(insert_marker)
    new_content = parts[0] + content + "\n\n" + insert_marker + parts[1]

    with open(
        r"D:\opcdcfg\opencode_config_manager_fluent_v1.0.0.py", "w", encoding="utf-8"
    ) as f:
        f.write(new_content)
    print("成功追加 SkillPage, RulesPage, CompactionPage 代码")
else:
    print("未找到插入点标记")

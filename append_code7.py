# -*- coding: utf-8 -*-
"""追加 ImportPage 和 BackupDialog 代码"""

content = '''

# ==================== Import 页面 ====================
class ImportPage(BasePage):
    """外部配置导入页面"""
    
    def __init__(self, main_window, parent=None):
        super().__init__("外部导入", parent)
        self.main_window = main_window
        self.import_service = ImportService()
        self._setup_ui()
    
    def _setup_ui(self):
        # 检测到的配置卡片
        detect_card = self.add_card("检测到的外部配置")
        detect_layout = detect_card.layout()
        
        # 刷新按钮
        refresh_btn = PrimaryPushButton(FIF.SYNC, "刷新检测", detect_card)
        refresh_btn.clicked.connect(self._refresh_scan)
        detect_layout.addWidget(refresh_btn)
        
        # 配置列表
        self.config_table = TableWidget(detect_card)
        self.config_table.setColumnCount(3)
        self.config_table.setHorizontalHeaderLabels(["来源", "配置路径", "状态"])
        self.config_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.config_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.config_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.config_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.config_table.itemSelectionChanged.connect(self._on_select)
        self.config_table.setMaximumHeight(180)
        detect_layout.addWidget(self.config_table)
        
        # 预览卡片
        preview_card = self.add_card("配置预览与转换结果")
        preview_layout = preview_card.layout()
        
        # 原始配置预览
        preview_layout.addWidget(BodyLabel("原始配置:", preview_card))
        self.preview_edit = TextEdit(preview_card)
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setMaximumHeight(120)
        preview_layout.addWidget(self.preview_edit)
        
        # 转换结果预览
        preview_layout.addWidget(BodyLabel("转换为 OpenCode 格式:", preview_card))
        self.convert_edit = TextEdit(preview_card)
        self.convert_edit.setReadOnly(True)
        self.convert_edit.setMaximumHeight(120)
        preview_layout.addWidget(self.convert_edit)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        preview_btn = PushButton("预览转换", preview_card)
        preview_btn.clicked.connect(self._preview_convert)
        btn_layout.addWidget(preview_btn)
        
        import_btn = PrimaryPushButton("导入到 OpenCode", preview_card)
        import_btn.clicked.connect(self._import_selected)
        btn_layout.addWidget(import_btn)
        
        btn_layout.addStretch()
        preview_layout.addLayout(btn_layout)
        
        self.layout.addStretch()
        
        # 初始扫描
        self._refresh_scan()
    
    def _refresh_scan(self):
        """刷新扫描外部配置"""
        self.config_table.setRowCount(0)
        results = self.import_service.scan_external_configs()
        
        for key, info in results.items():
            row = self.config_table.rowCount()
            self.config_table.insertRow(row)
            self.config_table.setItem(row, 0, QTableWidgetItem(key))
            self.config_table.setItem(row, 1, QTableWidgetItem(info["path"]))
            status = "已检测" if info["exists"] else "未找到"
            self.config_table.setItem(row, 2, QTableWidgetItem(status))
    
    def _on_select(self):
        """选中配置时显示预览"""
        row = self.config_table.currentRow()
        if row < 0:
            return
        
        source = self.config_table.item(row, 0).text()
        results = self.import_service.scan_external_configs()
        
        if source in results and results[source]["data"]:
            import json
            self.preview_edit.setPlainText(
                json.dumps(results[source]["data"], indent=2, ensure_ascii=False)
            )
            self.convert_edit.setPlainText("")
        else:
            self.preview_edit.setPlainText("无数据")
            self.convert_edit.setPlainText("")
    
    def _preview_convert(self):
        """预览转换结果"""
        row = self.config_table.currentRow()
        if row < 0:
            self.show_warning("提示", "请先选择要转换的配置")
            return
        
        source = self.config_table.item(row, 0).text()
        results = self.import_service.scan_external_configs()
        
        if source in results and results[source]["data"]:
            source_type = results[source].get("type", "")
            converted = self.import_service.convert_to_opencode(
                source_type, results[source]["data"]
            )
            if converted:
                import json
                self.convert_edit.setPlainText(
                    json.dumps(converted, indent=2, ensure_ascii=False)
                )
            else:
                self.show_warning("提示", "无法转换此配置格式")
    
    def _import_selected(self):
        """导入选中的配置"""
        row = self.config_table.currentRow()
        if row < 0:
            self.show_warning("提示", "请先选择要导入的配置")
            return
        
        source = self.config_table.item(row, 0).text()
        results = self.import_service.scan_external_configs()
        
        if source not in results or not results[source]["data"]:
            self.show_warning("提示", "所选配置不存在或为空")
            return
        
        source_type = results[source].get("type", "")
        converted = self.import_service.convert_to_opencode(
            source_type, results[source]["data"]
        )
        
        if not converted:
            self.show_warning("提示", "无法转换此配置格式")
            return
        
        # 确认导入
        provider_count = len(converted.get("provider", {}))
        perm_count = len(converted.get("permission", {}))
        
        w = FluentMessageBox(
            "确认导入",
            f"将导入以下配置:\\n• Provider: {provider_count} 个\\n• 权限: {perm_count} 个\\n\\n是否继续?",
            self
        )
        if not w.exec_():
            return
        
        # 合并配置
        config = self.main_window.opencode_config
        if config is None:
            config = {}
            self.main_window.opencode_config = config
        
        for provider_name, provider_data in converted.get("provider", {}).items():
            if provider_name in config.get("provider", {}):
                w2 = FluentMessageBox(
                    "冲突",
                    f'Provider "{provider_name}" 已存在，是否覆盖?',
                    self
                )
                if not w2.exec_():
                    continue
            config.setdefault("provider", {})[provider_name] = provider_data
        
        for tool, perm in converted.get("permission", {}).items():
            config.setdefault("permission", {})[tool] = perm
        
        # 保存
        if self.main_window.save_opencode_config():
            self.show_success("成功", f"已导入 {source} 的配置")


# ==================== Backup 对话框 ====================
class BackupDialog(QDialog):
    """备份恢复对话框"""
    
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.backup_manager = main_window.backup_manager
        
        self.setWindowTitle("备份管理")
        self.setMinimumSize(600, 400)
        self._setup_ui()
        self._load_backups()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # 工具栏
        toolbar = QHBoxLayout()
        
        backup_opencode_btn = PrimaryPushButton(FIF.SAVE, "备份 OpenCode", self)
        backup_opencode_btn.clicked.connect(self._backup_opencode)
        toolbar.addWidget(backup_opencode_btn)
        
        backup_ohmy_btn = PushButton(FIF.SAVE, "备份 Oh My OpenCode", self)
        backup_ohmy_btn.clicked.connect(self._backup_ohmyopencode)
        toolbar.addWidget(backup_ohmy_btn)
        
        toolbar.addStretch()
        
        refresh_btn = PushButton(FIF.SYNC, "刷新", self)
        refresh_btn.clicked.connect(self._load_backups)
        toolbar.addWidget(refresh_btn)
        
        layout.addLayout(toolbar)
        
        # 备份列表
        layout.addWidget(SubtitleLabel("备份列表", self))
        
        self.backup_table = TableWidget(self)
        self.backup_table.setColumnCount(4)
        self.backup_table.setHorizontalHeaderLabels(["配置文件", "时间", "标签", "路径"])
        self.backup_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.backup_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.backup_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.backup_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.backup_table)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        restore_btn = PrimaryPushButton("恢复选中备份", self)
        restore_btn.clicked.connect(self._restore_backup)
        btn_layout.addWidget(restore_btn)
        
        delete_btn = PushButton(FIF.DELETE, "删除备份", self)
        delete_btn.clicked.connect(self._delete_backup)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        
        close_btn = PushButton("关闭", self)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_backups(self):
        """加载备份列表"""
        self.backup_table.setRowCount(0)
        backups = self.backup_manager.list_backups()
        
        for backup in backups:
            row = self.backup_table.rowCount()
            self.backup_table.insertRow(row)
            self.backup_table.setItem(row, 0, QTableWidgetItem(backup["name"]))
            self.backup_table.setItem(row, 1, QTableWidgetItem(backup["timestamp"]))
            self.backup_table.setItem(row, 2, QTableWidgetItem(backup["tag"]))
            self.backup_table.setItem(row, 3, QTableWidgetItem(str(backup["path"])))
    
    def _backup_opencode(self):
        """备份 OpenCode 配置"""
        path = self.backup_manager.backup(ConfigPaths.get_opencode_config(), tag="manual")
        if path:
            InfoBar.success("成功", f"已备份到: {path}", parent=self)
            self._load_backups()
        else:
            InfoBar.error("错误", "备份失败", parent=self)
    
    def _backup_ohmyopencode(self):
        """备份 Oh My OpenCode 配置"""
        path = self.backup_manager.backup(ConfigPaths.get_ohmyopencode_config(), tag="manual")
        if path:
            InfoBar.success("成功", f"已备份到: {path}", parent=self)
            self._load_backups()
        else:
            InfoBar.error("错误", "备份失败", parent=self)
    
    def _restore_backup(self):
        """恢复备份"""
        row = self.backup_table.currentRow()
        if row < 0:
            InfoBar.warning("提示", "请先选择一个备份", parent=self)
            return
        
        backup_path = Path(self.backup_table.item(row, 3).text())
        config_name = self.backup_table.item(row, 0).text()
        
        # 确定目标路径
        if "opencode" in config_name and "oh-my" not in config_name:
            target_path = ConfigPaths.get_opencode_config()
        else:
            target_path = ConfigPaths.get_ohmyopencode_config()
        
        w = FluentMessageBox(
            "确认恢复",
            f"确定要恢复此备份吗？\\n当前配置将被覆盖（会先自动备份）。",
            self
        )
        if w.exec_():
            if self.backup_manager.restore(backup_path, target_path):
                InfoBar.success("成功", "备份已恢复", parent=self)
                # 重新加载配置
                if target_path == ConfigPaths.get_opencode_config():
                    self.main_window.opencode_config = ConfigManager.load_json(target_path)
                else:
                    self.main_window.ohmyopencode_config = ConfigManager.load_json(target_path)
            else:
                InfoBar.error("错误", "恢复失败", parent=self)
    
    def _delete_backup(self):
        """删除备份"""
        row = self.backup_table.currentRow()
        if row < 0:
            InfoBar.warning("提示", "请先选择一个备份", parent=self)
            return
        
        backup_path = Path(self.backup_table.item(row, 3).text())
        
        w = FluentMessageBox("确认删除", "确定要删除此备份吗？", self)
        if w.exec_():
            if self.backup_manager.delete_backup(backup_path):
                InfoBar.success("成功", "备份已删除", parent=self)
                self._load_backups()
            else:
                InfoBar.error("错误", "删除失败", parent=self)

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
    print("成功追加 ImportPage 和 BackupDialog 代码")
else:
    print("未找到插入点标记")

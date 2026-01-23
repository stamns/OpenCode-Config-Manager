# 添加国内AI平台预设 - 实现指南

## 当前状态分析

### 现有 Provider 添加流程
1. 用户点击"添加 Provider"按钮
2. 打开 `ProviderDialog` 对话框
3. 手动填写：Provider 名称、显示名称、SDK、Base URL、API Key
4. 保存后创建 Provider

### 问题
- 没有预设选择功能
- 用户需要手动查找和填写每个平台的 Base URL
- 容易出错，体验不佳

## 实现方案

### 方案 A：在 ProviderDialog 中添加预设选择（推荐）

#### 1. 定义预设常量

在 `opencode_config_manager_fluent.py` 顶部添加：

```python
# ==================== Provider 预设配置 ====================
PROVIDER_PRESETS = {
    # 官方平台
    "anthropic": {
        "name": "Anthropic Claude",
        "display_name": "Anthropic Claude",
        "sdk": "@ai-sdk/anthropic",
        "base_url": "",  # 使用默认
        "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
        "category": "official"
    },
    "openai": {
        "name": "OpenAI",
        "display_name": "OpenAI",
        "sdk": "@ai-sdk/openai",
        "base_url": "",  # 使用默认
        "models": ["gpt-4o", "gpt-4o-mini", "o1", "o1-mini"],
        "category": "official"
    },
    "google": {
        "name": "Google Gemini",
        "display_name": "Google Gemini",
        "sdk": "@ai-sdk/google",
        "base_url": "",  # 使用默认
        "models": ["gemini-2.0-flash-exp", "gemini-1.5-pro"],
        "category": "official"
    },
    
    # 国内平台（OpenAI 兼容）
    "zhipu": {
        "name": "智谱 GLM",
        "display_name": "智谱 GLM",
        "sdk": "@ai-sdk/openai",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/",
        "models": ["glm-4-plus", "glm-4-air", "glm-4-flash"],
        "api_key_field": "ZHIPU_API_KEY",
        "category": "chinese",
        "docs": "https://open.bigmodel.cn/dev/api"
    },
    "qwen": {
        "name": "千问 Qwen",
        "display_name": "千问 Qwen (阿里云)",
        "sdk": "@ai-sdk/openai",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": ["qwen-max", "qwen-plus", "qwen-turbo"],
        "api_key_field": "DASHSCOPE_API_KEY",
        "category": "chinese",
        "docs": "https://help.aliyun.com/zh/dashscope/"
    },
    "kimi": {
        "name": "Kimi",
        "display_name": "Kimi (月之暗面)",
        "sdk": "@ai-sdk/openai",
        "base_url": "https://api.moonshot.cn/v1",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "api_key_field": "MOONSHOT_API_KEY",
        "category": "chinese",
        "docs": "https://platform.moonshot.cn/docs"
    },
    "yi": {
        "name": "零一万物 Yi",
        "display_name": "零一万物 Yi",
        "sdk": "@ai-sdk/openai",
        "base_url": "https://api.lingyiwanwu.com/v1",
        "models": ["yi-lightning", "yi-large", "yi-medium"],
        "api_key_field": "YI_API_KEY",
        "category": "chinese",
        "docs": "https://platform.lingyiwanwu.com/docs"
    },
    "minimax": {
        "name": "MiniMax",
        "display_name": "MiniMax",
        "sdk": "@ai-sdk/openai",
        "base_url": "https://api.minimax.chat/v1",
        "models": ["abab6.5s-chat", "abab6.5g-chat", "abab6.5t-chat"],
        "api_key_field": "MINIMAX_API_KEY",
        "category": "chinese",
        "docs": "https://www.minimaxi.com/document"
    },
    "deepseek": {
        "name": "DeepSeek",
        "display_name": "DeepSeek",
        "sdk": "@ai-sdk/openai",
        "base_url": "https://api.deepseek.com/v1",
        "models": ["deepseek-chat", "deepseek-coder"],
        "api_key_field": "DEEPSEEK_API_KEY",
        "category": "chinese",
        "docs": "https://platform.deepseek.com/api-docs/"
    },
    
    # 第三方服务
    "custom": {
        "name": "自定义",
        "display_name": "自定义 Provider",
        "sdk": "@ai-sdk/openai",
        "base_url": "",
        "models": [],
        "category": "custom"
    }
}

# 预设分类
PROVIDER_CATEGORIES = {
    "official": "官方平台",
    "chinese": "国内平台",
    "custom": "自定义"
}
```

#### 2. 修改 ProviderDialog

在 `_setup_ui()` 方法开头添加预设选择：

```python
def _setup_ui(self):
    layout = QVBoxLayout(self)
    layout.setSpacing(16)
    
    # 预设选择（仅在新建时显示）
    if not self.is_edit:
        preset_group = QGroupBox("选择预设", self)
        preset_layout = QVBoxLayout(preset_group)
        
        # 按分类显示预设
        for category_key, category_name in PROVIDER_CATEGORIES.items():
            category_label = StrongBodyLabel(category_name, self)
            preset_layout.addWidget(category_label)
            
            # 该分类下的预设
            presets = [
                (key, data) for key, data in PROVIDER_PRESETS.items()
                if data.get("category") == category_key
            ]
            
            for preset_key, preset_data in presets:
                preset_btn = PushButton(preset_data["display_name"], self)
                preset_btn.clicked.connect(
                    lambda checked, k=preset_key: self._apply_preset(k)
                )
                preset_layout.addWidget(preset_btn)
        
        layout.addWidget(preset_group)
        
        # 分隔线
        layout.addWidget(QFrame())
    
    # 原有的表单字段...
    # Provider 名称
    name_layout = QHBoxLayout()
    # ...
```

#### 3. 添加预设应用方法

```python
def _apply_preset(self, preset_key: str):
    """应用预设配置"""
    preset = PROVIDER_PRESETS.get(preset_key)
    if not preset:
        return
    
    # 填充表单
    self.name_edit.setText(preset_key)
    self.display_edit.setText(preset["display_name"])
    self.sdk_combo.setCurrentText(preset["sdk"])
    self.url_edit.setText(preset["base_url"])
    
    # 如果有文档链接，显示提示
    if "docs" in preset:
        InfoBar.info(
            "提示",
            f"请访问 {preset['docs']} 获取 API Key",
            parent=self
        )
```

#### 4. 添加翻译

在 `translations.py` 中添加：

```python
"provider": {
    "preset_title": {
        "zh_CN": "选择预设",
        "en_US": "Select Preset"
    },
    "official_platforms": {
        "zh_CN": "官方平台",
        "en_US": "Official Platforms"
    },
    "chinese_platforms": {
        "zh_CN": "国内平台",
        "en_US": "Chinese Platforms"
    },
    "custom_provider": {
        "zh_CN": "自定义",
        "en_US": "Custom"
    }
}
```

### 方案 B：创建独立的预设选择对话框

#### 1. 创建 ProviderPresetDialog

```python
class ProviderPresetDialog(BaseDialog):
    """Provider 预设选择对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_preset = None
        self.setWindowTitle("选择 Provider 预设")
        self.setMinimumSize(600, 500)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 搜索框
        search_layout = QHBoxLayout()
        self.search_edit = LineEdit(self)
        self.search_edit.setPlaceholderText("搜索平台...")
        self.search_edit.textChanged.connect(self._filter_presets)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # 预设列表
        self.preset_list = ListWidget(self)
        self._load_presets()
        self.preset_list.itemDoubleClicked.connect(self._on_preset_selected)
        layout.addWidget(self.preset_list)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = PushButton("取消", self)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        select_btn = PrimaryPushButton("选择", self)
        select_btn.clicked.connect(self._on_preset_selected)
        btn_layout.addWidget(select_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_presets(self):
        """加载预设列表"""
        for category_key, category_name in PROVIDER_CATEGORIES.items():
            # 添加分类标题
            category_item = QListWidgetItem(f"━━ {category_name} ━━")
            category_item.setFlags(Qt.NoItemFlags)
            self.preset_list.addItem(category_item)
            
            # 添加该分类下的预设
            presets = [
                (key, data) for key, data in PROVIDER_PRESETS.items()
                if data.get("category") == category_key
            ]
            
            for preset_key, preset_data in presets:
                item = QListWidgetItem(preset_data["display_name"])
                item.setData(Qt.UserRole, preset_key)
                self.preset_list.addItem(item)
    
    def _filter_presets(self, text: str):
        """过滤预设"""
        for i in range(self.preset_list.count()):
            item = self.preset_list.item(i)
            if item.flags() == Qt.NoItemFlags:  # 分类标题
                continue
            item.setHidden(text.lower() not in item.text().lower())
    
    def _on_preset_selected(self):
        """选择预设"""
        current = self.preset_list.currentItem()
        if current and current.flags() != Qt.NoItemFlags:
            self.selected_preset = current.data(Qt.UserRole)
            self.accept()
    
    def get_selected_preset(self) -> str:
        """获取选中的预设 key"""
        return self.selected_preset
```

#### 2. 修改添加 Provider 流程

在 ProviderPage 的添加按钮点击事件中：

```python
def _on_add_provider(self):
    """添加 Provider"""
    # 先显示预设选择对话框
    preset_dialog = ProviderPresetDialog(self)
    if preset_dialog.exec_():
        preset_key = preset_dialog.get_selected_preset()
        if preset_key:
            # 打开 Provider 对话框并应用预设
            dialog = ProviderDialog(self.main_window, parent=self)
            dialog._apply_preset(preset_key)
            dialog.exec_()
    else:
        # 用户取消，直接打开空白对话框
        dialog = ProviderDialog(self.main_window, parent=self)
        dialog.exec_()
```

## 实现优先级

### 第一阶段：基础预设（1-2小时）
1. ✅ 定义 PROVIDER_PRESETS 常量
2. ✅ 在 ProviderDialog 中添加预设选择 UI
3. ✅ 实现 _apply_preset() 方法
4. ✅ 添加翻译文本

### 第二阶段：优化体验（1小时）
1. ⏳ 添加预设搜索功能
2. ⏳ 显示预设文档链接
3. ⏳ 添加预设图标/Logo
4. ⏳ 优化 UI 布局

### 第三阶段：高级功能（1-2小时）
1. ⏳ 自动检测环境变量中的 API Key
2. ⏳ 一键测试 API 连接
3. ⏳ 预设模型自动添加
4. ⏳ 支持自定义预设

## 测试计划

### 测试用例
1. ✅ 选择官方平台预设（Anthropic、OpenAI、Google）
2. ✅ 选择国内平台预设（智谱、千问、Kimi、Yi、MiniMax、DeepSeek）
3. ✅ 验证 Base URL 正确填充
4. ✅ 验证 SDK 正确选择
5. ✅ 保存后配置正确写入
6. ✅ 编辑现有 Provider 不显示预设选择

### 验证步骤
1. 打开软件，进入 Provider 页面
2. 点击"添加 Provider"
3. 选择一个国内平台预设（如"智谱 GLM"）
4. 验证表单自动填充：
   - Provider 名称：zhipu
   - 显示名称：智谱 GLM
   - SDK：@ai-sdk/openai
   - Base URL：https://open.bigmodel.cn/api/paas/v4/
5. 填写 API Key
6. 保存并验证配置文件

## 下一步

1. 实现方案 A（在 ProviderDialog 中添加预设）
2. 测试所有预设平台
3. 更新用户文档
4. 发布 v1.5.0

## 参考资料

- `platform_support_plan.md` - 完整的平台支持计划
- OpenCode 官方文档：https://opencode.ai/docs/providers/
- 各平台 API 文档链接见 PROVIDER_PRESETS 定义

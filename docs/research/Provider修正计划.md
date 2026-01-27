# Provider配置修正计划

## 📋 基于实际验证的修正清单

### 已验证的Provider配置（从models.dev和GitHub）

| Provider ID | 名称 | API端点 | 环境变量 | SDK | 状态 |
|------------|------|---------|---------|-----|------|
| `anthropic` | Anthropic | `https://api.anthropic.com/v1` | `ANTHROPIC_API_KEY` | `@ai-sdk/anthropic` | ✅ 正确 |
| `openai` | OpenAI | `https://api.openai.com/v1` | `OPENAI_API_KEY` | `@ai-sdk/openai` | ✅ 正确 |
| `google` | Google | `https://generativelanguage.googleapis.com/v1beta` | `GOOGLE_API_KEY` | `@ai-sdk/google` | ⚠️ 当前用`gemini` |
| `deepseek` | DeepSeek | `https://api.deepseek.com` | `DEEPSEEK_API_KEY` | `@ai-sdk/openai-compatible` | ✅ 正确 |
| `groq` | Groq | `https://api.groq.com/openai/v1` | `GROQ_API_KEY` | `@ai-sdk/groq` | ✅ 正确 |
| `xai` | xAI | `https://api.x.ai/v1` | `XAI_API_KEY` | `@ai-sdk/xai` | ✅ 正确 |
| `openrouter` | OpenRouter | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | `@ai-sdk/openai-compatible` | ✅ 正确 |
| `amazon-bedrock` | Amazon Bedrock | - | `AWS_*` | `@ai-sdk/amazon-bedrock` | ✅ 正确 |
| `azure` | Azure OpenAI | - | `AZURE_*` | `@ai-sdk/azure` | ✅ 正确 |
| `google-vertex` | Google Vertex AI | - | `GOOGLE_*` | `@ai-sdk/google-vertex` | ⚠️ 当前用`vertexai` |
| `github-copilot` | GitHub Copilot | - | - | `@ai-sdk/openai` | ⚠️ 当前用`copilot` |
| `zhipuai-coding-plan` | Zhipu AI Coding Plan | `https://open.bigmodel.cn/api/coding/paas/v4` | `ZHIPU_API_KEY` | `@ai-sdk/openai-compatible` | ❌ 当前用`zhipu` |
| `zhipuai` | Zhipu AI | `https://open.bigmodel.cn/api/paas/v4` | `ZHIPU_API_KEY` | `@ai-sdk/openai-compatible` | ❌ 缺失 |
| `zai-coding-plan` | Z.AI Coding Plan | `https://api.z.ai/api/coding/paas/v4` | `ZHIPU_API_KEY` | `@ai-sdk/openai-compatible` | ❌ 缺失 |
| `zai` | Z.AI | `https://api.z.ai/api/paas/v4` | `ZHIPU_API_KEY` | `@ai-sdk/openai-compatible` | ❌ 缺失 |
| `moonshotai` | Moonshot AI | `https://api.moonshot.ai/v1` | `MOONSHOT_API_KEY` | `@ai-sdk/openai-compatible` | ⚠️ 当前用`kimi` |
| `alibaba` | Alibaba (Qwen) | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | `DASHSCOPE_API_KEY` | `@ai-sdk/openai-compatible` | ⚠️ 当前用`qwen` |
| `minimax` | MiniMax | `https://api.minimax.io/v1` | `MINIMAX_API_KEY` | `@ai-sdk/openai-compatible` | ✅ 正确 |
| `yi` | Yi (零一万物) | `https://api.lingyiwanwu.com/v1` | `YI_API_KEY` | `@ai-sdk/openai-compatible` | ✅ 正确 |
| `opencode` | OpenCode Zen | `https://api.opencode.ai/v1` | - | `@ai-sdk/openai-compatible` | ✅ 正确 |

### 用户确认的配置格式

**auth.json 正确格式（用户实际配置）：**
```json
{
  "zhipuai-coding-plan": {
    "type": "api",
    "key": "9b28de1ce4a34e468da2d848d8211fd7.luFZ1vWnEGQnA4ip"
  }
}
```

**关键字段：**
- ✅ `"type": "api"` - 必需字段
- ✅ `"key"` - 不是 `"apiKey"`

---

## 🔧 修正任务清单

### 任务1：修正AuthManager的auth.json格式 ⭐⭐⭐

**当前问题：**
```python
# 当前代码存储格式
{
  "anthropic": {
    "apiKey": "sk-ant-xxx"  # ❌ 缺少type字段，字段名错误
  }
}
```

**修正为：**
```python
# OpenCode官方格式
{
  "anthropic": {
    "type": "api",
    "key": "sk-ant-xxx"
  }
}
```

**修改位置：**
- `AuthManager.set_provider_auth()` 方法（约420行）
- `AuthManager.get_provider_auth()` 方法（约408行）

---

### 任务2：重命名和添加智谱AI Provider ⭐⭐⭐

**需要修改：**

1. **将 `"zhipu"` 重命名为 `"zhipuai-coding-plan"`**
   - 位置：第674行
   - 保持当前的Coding Plan API端点

2. **添加普通版 `"zhipuai"`**
   - API端点：`https://open.bigmodel.cn/api/paas/v4`（无`/coding/`）

**代码示例：**
```python
# 智谱AI - 普通版本
NativeProviderConfig(
    id="zhipuai",
    name="Zhipu AI (智谱GLM)",
    sdk="@ai-sdk/openai-compatible",
    auth_fields=[
        AuthField("apiKey", "API Key", "password", True, ""),
    ],
    option_fields=[
        OptionField(
            "baseURL",
            "Base URL",
            "text",
            [],
            "https://open.bigmodel.cn/api/paas/v4",
        ),
    ],
    env_vars=["ZHIPU_API_KEY"],
    test_endpoint="/models",
),

# 智谱AI - Coding Plan版本
NativeProviderConfig(
    id="zhipuai-coding-plan",
    name="Zhipu AI Coding Plan (智谱GLM编码套餐)",
    sdk="@ai-sdk/openai-compatible",
    auth_fields=[
        AuthField("apiKey", "API Key", "password", True, ""),
    ],
    option_fields=[
        OptionField(
            "baseURL",
            "Base URL",
            "text",
            [],
            "https://open.bigmodel.cn/api/coding/paas/v4",
        ),
    ],
    env_vars=["ZHIPU_API_KEY"],
    test_endpoint="/models",
),
```

---

### 任务3：添加Z.AI Provider ⭐⭐⭐

**添加两个新Provider：**

```python
# Z.AI - 普通版本
NativeProviderConfig(
    id="zai",
    name="Z.AI",
    sdk="@ai-sdk/openai-compatible",
    auth_fields=[
        AuthField("apiKey", "API Key", "password", True, ""),
    ],
    option_fields=[
        OptionField(
            "baseURL",
            "Base URL",
            "text",
            [],
            "https://api.z.ai/api/paas/v4",
        ),
    ],
    env_vars=["ZHIPU_API_KEY"],
    test_endpoint="/models",
),

# Z.AI - Coding Plan版本
NativeProviderConfig(
    id="zai-coding-plan",
    name="Z.AI Coding Plan",
    sdk="@ai-sdk/openai-compatible",
    auth_fields=[
        AuthField("apiKey", "API Key", "password", True, ""),
    ],
    option_fields=[
        OptionField(
            "baseURL",
            "Base URL",
            "text",
            [],
            "https://api.z.ai/api/coding/paas/v4",
        ),
    ],
    env_vars=["ZHIPU_API_KEY"],
    test_endpoint="/models",
),
```

---

### 任务4：修正其他Provider命名 ⚠️

**需要验证和可能修正的Provider：**

1. **Google Gemini**
   - 当前：`id="gemini"`
   - 可能应该：`id="google"`
   - 需要验证OpenCode官方文档

2. **Moonshot AI (Kimi)**
   - 当前：`id="kimi"`
   - models.dev中：`id="moonshotai"`
   - 需要验证哪个是OpenCode官方使用的

3. **Alibaba Qwen**
   - 当前：`id="qwen"`
   - models.dev中：`id="alibaba"`
   - 需要验证哪个是OpenCode官方使用的

4. **Google Vertex AI**
   - 当前：`id="vertexai"`
   - 可能应该：`id="google-vertex"`

5. **GitHub Copilot**
   - 当前：`id="copilot"`
   - 可能应该：`id="github-copilot"`

---

### 任务5：在首页添加auth.json路径显示 ⭐⭐

**修改位置：** HomePage类（约5685行）

**添加内容：**
```python
# 在配置文件路径卡片中添加auth.json路径
auth_layout = QHBoxLayout()
auth_layout.addWidget(create_path_label("Auth File:"))
self.auth_path_label = CaptionLabel(
    str(AuthManager().auth_path), paths_card
)
self.auth_path_label.setToolTip(str(AuthManager().auth_path))
auth_layout.addWidget(self.auth_path_label, 1)

auth_view_btn = ToolButton(FIF.VIEW, paths_card)
auth_view_btn.setToolTip("查看认证文件")
auth_view_btn.clicked.connect(
    lambda: self._view_config_file(AuthManager().auth_path)
)
auth_layout.addWidget(auth_view_btn)

auth_copy_btn = ToolButton(FIF.COPY, paths_card)
auth_copy_btn.setToolTip(tr("common.copy"))
auth_copy_btn.clicked.connect(
    lambda: self._copy_to_clipboard(str(AuthManager().auth_path))
)
auth_layout.addWidget(auth_copy_btn)

paths_layout.addLayout(auth_layout)
```

---

### 任务6：实现模型列表动态获取 ⭐⭐

**创建新类：**
```python
class ModelListFetcher:
    """动态获取Provider的模型列表"""
    
    @staticmethod
    def fetch_models(provider_id: str, api_key: str, base_url: str) -> List[str]:
        """
        从Provider的API获取模型列表
        
        Args:
            provider_id: Provider标识符
            api_key: API密钥
            base_url: API基础URL
            
        Returns:
            模型ID列表
        """
        endpoint = f"{base_url}/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # OpenAI格式：{"data": [{"id": "model-name"}, ...]}
            if "data" in data:
                return [model["id"] for model in data["data"]]
            
            return []
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            return []
```

**在NativeProviderPage中添加"刷新模型列表"按钮**

---

### 任务7：更新环境变量检测器 ⚠️

**添加新的Provider环境变量映射：**
```python
PROVIDER_ENV_VARS: Dict[str, List[str]] = {
    # ... 现有的 ...
    "zhipuai": ["ZHIPU_API_KEY"],
    "zhipuai-coding-plan": ["ZHIPU_API_KEY"],
    "zai": ["ZHIPU_API_KEY"],
    "zai-coding-plan": ["ZHIPU_API_KEY"],
    "moonshotai": ["MOONSHOT_API_KEY"],
    "alibaba": ["DASHSCOPE_API_KEY"],
}
```

---

## 📝 实施顺序

### 阶段1：紧急修正（立即执行）
1. ✅ 修正AuthManager的auth.json格式（任务1）
2. ✅ 重命名智谱AI Provider（任务2）
3. ✅ 添加Z.AI Provider（任务3）
4. ✅ 在首页添加auth.json路径（任务5）

### 阶段2：验证和完善（后续执行）
5. ⚠️ 验证其他Provider命名（任务4）
6. ⚠️ 更新环境变量检测器（任务7）

### 阶段3：功能增强（可选）
7. ⭐ 实现模型列表动态获取（任务6）

---

## 🎯 预期结果

修正后：
1. ✅ auth.json格式符合OpenCode官方规范
2. ✅ 智谱AI有两个独立的Provider（普通版和Coding Plan）
3. ✅ Z.AI有两个独立的Provider（普通版和Coding Plan）
4. ✅ 首页显示auth.json文件路径
5. ✅ 用户可以正确配置所有Provider
6. ✅ 环境变量检测正确识别所有Provider

---

**文档维护者**: OpenCode Config Manager开发团队  
**最后更新**: 2026-01-28  
**文档版本**: v1.0.0

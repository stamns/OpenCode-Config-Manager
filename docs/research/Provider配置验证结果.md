# Provider配置验证结果 - 2026-01-28

## 📊 核心发现总结

### ✅ 验证通过的配置

1. **auth.json 路径正确**
   - 当前代码：`~/.local/share/opencode/auth.json`
   - 官方文档：`~/.local/share/opencode/auth.json`
   - ✅ **完全一致**

2. **auth.json 结构格式**
   
   **官方格式（从GitHub实例中找到）：**
   ```json
   {
     "anthropic": {
       "type": "api",
       "key": "sk-ant-xxx"
     }
   }
   ```
   
   **当前代码存储格式：**
   ```json
   {
     "anthropic": {
       "apiKey": "sk-ant-xxx"
     }
   }
   ```
   
   ⚠️ **问题：缺少 `"type"` 字段，字段名不一致（`key` vs `apiKey`）**

### ⚠️ 需要修正的配置

#### 1. 智谱AI Provider命名问题

**从GitHub搜索结果发现的官方命名：**

| Provider ID | 名称 | API端点 | 环境变量 |
|------------|------|---------|---------|
| `zhipuai-coding-plan` | Zhipu AI Coding Plan | `https://open.bigmodel.cn/api/coding/paas/v4` | `ZHIPU_API_KEY` |
| `zhipuai` | Zhipu AI | `https://open.bigmodel.cn/api/paas/v4` | `ZHIPU_API_KEY` |

**当前代码配置（第674行）：**
```python
id="zhipu"  # ❌ 错误！应该是 "zhipuai"
```

**API URL（第686行）：**
```python
"https://open.bigmodel.cn/api/coding/paas/v4"  # 这是Coding Plan的URL
```

**问题：**
- Provider ID 应该是 `"zhipuai"` 或 `"zhipuai-coding-plan"`，不是 `"zhipu"`
- 当前配置混淆了普通版和Coding Plan版本

#### 2. Z.AI Provider配置

**从GitHub搜索结果发现：**

| Provider ID | 名称 | API端点 | 环境变量 |
|------------|------|---------|---------|
| `zai` | Z.AI | `https://api.z.ai/api/paas/v4` | `ZHIPU_API_KEY` |
| `zai-coding-plan` | Z.AI Coding Plan | `https://api.z.ai/api/coding/paas/v4` | `ZHIPU_API_KEY` |

**当前代码：**
- ❌ 完全缺失 `zai` 和 `zai-coding-plan` Provider

#### 3. 其他Provider验证

从OpenCode官方文档和GitHub搜索结果验证：

| Provider | 当前ID | 官方ID | 状态 |
|---------|--------|--------|------|
| Anthropic | `anthropic` | `anthropic` | ✅ 正确 |
| OpenAI | `openai` | `openai` | ✅ 正确 |
| Google | `gemini` | `google` | ⚠️ 可能需要验证 |
| DeepSeek | `deepseek` | `deepseek` | ✅ 正确 |
| Kimi | `kimi` | `moonshot` | ⚠️ 需要验证 |
| Qwen | `qwen` | `alibaba` | ⚠️ 需要验证 |

---

## 🔍 详细验证结果

### 1. OpenCode官方文档验证

**来源：** https://opencode.ai/docs/providers/

**关键发现：**

1. **认证存储位置：**
   > "When you add a provider's API keys with the `/connect` command, they are stored in `~/.local/share/opencode/auth.json`."

2. **Provider配置方式：**
   - 使用 `/connect` 命令添加认证
   - 在 `opencode.json` 中配置 provider 选项

3. **没有找到 "zhipu" Provider：**
   - 文档中没有列出 "zhipu" 作为官方Provider
   - 但提到了 "Z.AI" 和 "Moonshot AI"

### 2. GitHub代码实例验证

**来源：** GitHub搜索结果（多个仓库）

#### 实例1：mastra-ai/mastra
```json
{
  "zhipuai-coding-plan": {
    "url": "https://open.bigmodel.cn/api/coding/paas/v4",
    "apiKeyEnvVar": "ZHIPU_API_KEY",
    "apiKeyHeader": "Authorization",
    "name": "Zhipu AI Coding Plan",
    "models": ["glm-4.5", "glm-4.5-air", ...]
  }
}
```

#### 实例2：VoltAgent/voltagent
```typescript
zai: {
  id: "zai",
  name: "Z.AI",
  npm: "@ai-sdk/openai-compatible",
  api: "https://api.z.ai/api/paas/v4",
  env: ["ZHIPU_API_KEY"],
},
"zai-coding-plan": {
  id: "zai-coding-plan",
  name: "Z.AI Coding Plan",
  npm: "@ai-sdk/openai-compatible",
  api: "https://api.z.ai/api/coding/paas/v4",
  env: ["ZHIPU_API_KEY"],
}
```

#### 实例3：anomalyco/opencode (官方仓库)
```yaml
# GitLab CI配置示例
cat > ~/.local/share/opencode/auth.json << EOF
{
  "anthropic": {
    "type": "api",
    "key": "$ANTHROPIC_API_KEY"
  }
}
EOF
```

**关键发现：**
- ✅ auth.json 使用 `"type": "api"` 和 `"key"` 字段
- ✅ Provider ID 是 `"zhipuai-coding-plan"` 不是 `"zhipu"`
- ✅ Z.AI 是独立的Provider，有普通版和Coding Plan版

### 3. 智谱AI官方文档验证

**来源：** https://docs.bigmodel.cn/cn/coding-plan/tool/opencode

**关键配置步骤：**

1. **运行 `opencode auth login` 并选择 "Zhipu AI Coding Plan"**
   ```bash
   $ opencode auth login
   ◆  Select provider
   │  ● Zhipu AI Coding Plan
   ```

2. **低版本配置方式（如果没有Coding Plan选项）：**
   ```json
   {
     "$schema": "https://opencode.ai/config.json",
     "provider": {
       "zhipuai": {
         "api": "https://open.bigmodel.cn/api/coding/paas/v4"
       }
     }
   }
   ```

**关键发现：**
- ✅ Provider名称是 `"Zhipu AI Coding Plan"` 不是 "zhipu"
- ✅ 低版本使用 `"zhipuai"` 作为ID
- ✅ Coding Plan使用专属端点：`/api/coding/paas/v4`

### 4. Z.AI官方文档验证

**来源：** https://docs.z.ai/devpack/tool/opencode

**关键配置步骤：**

1. **选择Provider：**
   ```bash
   $ opencode auth login
   ◆  Select provider
   │  ● Z.AI Coding Plan
   ```

2. **Z.AI和智谱AI的关系：**
   - Z.AI使用相同的 `ZHIPU_API_KEY` 环境变量
   - 但使用不同的API端点：`https://api.z.ai/api/...`

---

## 📋 需要修正的清单

### 高优先级修正

#### 1. 修正auth.json数据结构

**当前代码（AuthManager.set_provider_auth）：**
```python
def set_provider_auth(self, provider_id: str, auth_config: Dict[str, Any]) -> None:
    auth_data = self.read_auth()
    auth_data[provider_id] = auth_config  # 直接存储 {'apiKey': 'xxx'}
    self.write_auth(auth_data)
```

**应该改为：**
```python
def set_provider_auth(self, provider_id: str, auth_config: Dict[str, Any]) -> None:
    auth_data = self.read_auth()
    # 转换为OpenCode官方格式
    auth_data[provider_id] = {
        "type": "api",  # 或 "oauth"
        "key": auth_config.get("apiKey") or auth_config.get("key")
    }
    self.write_auth(auth_data)
```

#### 2. 重命名智谱AI Provider

**当前代码（第674-690行）：**
```python
NativeProviderConfig(
    id="zhipu",  # ❌ 错误
    name="智谱 GLM",
    # ...
)
```

**应该改为两个独立的Provider：**

```python
# 普通版本
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

# Coding Plan版本
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
            "https://open.bigmodel.cn/api/coding/paas/v4",  # 注意 /coding/ 路径
        ),
    ],
    env_vars=["ZHIPU_API_KEY"],
    test_endpoint="/models",
),
```

#### 3. 添加Z.AI Provider

```python
# Z.AI 普通版本
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

# Z.AI Coding Plan版本
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
            "https://api.z.ai/api/coding/paas/v4",  # 注意 /coding/ 路径
        ),
    ],
    env_vars=["ZHIPU_API_KEY"],
    test_endpoint="/models",
),
```

### 中优先级修正

#### 4. 验证其他中国Provider的命名

需要进一步验证：
- Kimi：当前用 `"kimi"`，可能应该是 `"moonshot"`
- Qwen：当前用 `"qwen"`，可能应该是 `"alibaba"`

#### 5. 实现模型列表动态获取

**需要实现的功能：**
```python
class ModelListFetcher:
    """动态获取Provider的模型列表"""
    
    def fetch_models(self, provider_id: str, api_key: str, base_url: str) -> List[str]:
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

**支持模型列表API的Provider：**
- ✅ OpenAI: `/v1/models`
- ✅ Anthropic: 不支持（使用预设列表）
- ✅ Google: `/v1beta/models`
- ✅ DeepSeek: `/v1/models`
- ✅ 智谱AI: `/models`
- ✅ Qwen: `/models`
- ✅ Kimi: `/v1/models`

---

## 🎯 实施建议

### 阶段1：紧急修正（立即执行）

1. **修正auth.json数据结构**
   - 修改 `AuthManager.set_provider_auth()` 方法
   - 添加 `"type"` 字段
   - 使用 `"key"` 而不是 `"apiKey"`

2. **重命名智谱AI Provider**
   - 将 `"zhipu"` 改为 `"zhipuai"`
   - 添加 `"zhipuai-coding-plan"` 作为独立Provider

3. **添加Z.AI Provider**
   - 添加 `"zai"` 和 `"zai-coding-plan"`

### 阶段2：功能增强（后续执行）

1. **实现模型列表动态获取**
   - 创建 `ModelListFetcher` 类
   - 在Provider配置页面添加"刷新模型列表"按钮

2. **添加连接测试功能**
   - 验证API Key是否有效
   - 测试API端点连接

3. **验证其他Provider命名**
   - 确认Kimi、Qwen等Provider的正确命名

### 阶段3：用户体验优化

1. **迁移现有配置**
   - 检测旧的 `"zhipu"` 配置
   - 自动迁移到 `"zhipuai"` 或 `"zhipuai-coding-plan"`

2. **添加配置向导**
   - 引导用户选择正确的Provider版本
   - 提供配置示例和文档链接

---

## 📚 参考资料

### 官方文档
- OpenCode Providers: https://opencode.ai/docs/providers/
- 智谱AI Coding Plan: https://docs.bigmodel.cn/cn/coding-plan/tool/opencode
- Z.AI OpenCode: https://docs.z.ai/devpack/tool/opencode

### GitHub实例
- mastra-ai/mastra: Provider配置示例
- VoltAgent/voltagent: Provider注册表
- anomalyco/opencode: 官方仓库

### 环境变量
- `ZHIPU_API_KEY`: 智谱AI和Z.AI共用
- `ANTHROPIC_API_KEY`: Anthropic
- `OPENAI_API_KEY`: OpenAI
- `GOOGLE_API_KEY` / `GEMINI_API_KEY`: Google

---

**文档维护者**: OpenCode Config Manager开发团队  
**最后更新**: 2026-01-28  
**文档版本**: v2.0.0

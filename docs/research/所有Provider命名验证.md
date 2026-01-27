# 所有Provider命名验证结果

## 从OpenCode官方文档验证的Provider命名

### ✅ 已验证正确的Provider

| 当前ID | 官方文档名称 | 状态 |
|--------|-------------|------|
| `anthropic` | Anthropic | ✅ 正确 |
| `openai` | OpenAI | ✅ 正确 |
| `amazon-bedrock` | Amazon Bedrock | ✅ 正确 |
| `azure` | Azure OpenAI | ✅ 正确 |
| `xai` | xAI | ✅ 正确 |
| `groq` | Groq | ✅ 正确 |
| `openrouter` | OpenRouter | ✅ 正确 |
| `deepseek` | DeepSeek | ✅ 正确 |
| `minimax` | MiniMax | ✅ 正确 |
| `yi` | Yi (零一万物) | ✅ 正确 |
| `opencode` | OpenCode Zen | ✅ 正确 |

### ❌ 需要修正的Provider

| 当前ID | 应该是 | 官方文档名称 | 问题 |
|--------|--------|-------------|------|
| `gemini` | **保持不变** | Google Gemini | ⚠️ 文档中没有明确说明ID，但SDK是`@ai-sdk/google` |
| `copilot` | `github-copilot` | GitHub Copilot | ❌ 文档标题是"GitHub Copilot" |
| `vertexai` | `google-vertex` | Google Vertex AI | ❌ 文档标题是"Google Vertex AI" |
| `kimi` | `moonshot` | Moonshot AI | ❌ 文档标题是"Moonshot AI"，不是Kimi |
| `qwen` | **保持不变** | Qwen (千问) | ⚠️ 文档中没有明确说明，但环境变量是DASHSCOPE_API_KEY |

### 📋 从文档中提取的关键信息

#### 1. GitHub Copilot
**文档标题：** "GitHub Copilot"
**配置命令：** `/connect` 然后搜索 "GitHub Copilot"
**结论：** Provider ID应该是 `github-copilot`

#### 2. Google Vertex AI
**文档标题：** "Google Vertex AI"
**环境变量：** `GOOGLE_CLOUD_PROJECT`, `VERTEX_LOCATION`, `GOOGLE_APPLICATION_CREDENTIALS`
**结论：** Provider ID应该是 `google-vertex` 或 `vertex-ai`

#### 3. Moonshot AI
**文档标题：** "Moonshot AI"
**描述：** "To use Kimi K2 from Moonshot AI"
**配置命令：** `/connect` 然后搜索 "Moonshot AI"
**环境变量：** `MOONSHOT_API_KEY`
**结论：** Provider ID应该是 `moonshot` 或 `moonshotai`，不是 `kimi`

#### 4. Google Gemini
**文档标题：** 没有单独的"Google Gemini"章节
**SDK：** `@ai-sdk/google`
**结论：** 可能是 `google` 或 `gemini`，需要进一步验证

#### 5. Z.AI
**文档标题：** "Z.AI"
**结论：** ✅ 我们已经添加了 `zai` 和 `zai-coding-plan`

---

## 🔧 需要执行的修正

### 修正1：GitHub Copilot
```python
# 当前
id="copilot"

# 应该改为
id="github-copilot"
```

### 修正2：Google Vertex AI
```python
# 当前
id="vertexai"

# 应该改为
id="google-vertex"
```

### 修正3：Moonshot AI (Kimi)
```python
# 当前
id="kimi"
name="Kimi (月之暗面)"
env_vars=["MOONSHOT_API_KEY", "KIMI_API_KEY"]

# 应该改为
id="moonshot"
name="Moonshot AI (Kimi)"
env_vars=["MOONSHOT_API_KEY"]
```

### 待验证：Google Gemini
```python
# 当前
id="gemini"
sdk="@ai-sdk/google"

# 可能需要改为
id="google"
sdk="@ai-sdk/google"
```

---

## 📊 修正优先级

### 高优先级（明确错误）
1. ✅ `copilot` → `github-copilot`
2. ✅ `vertexai` → `google-vertex`
3. ✅ `kimi` → `moonshot`

### 中优先级（需要验证）
4. ⚠️ `gemini` → 可能需要改为 `google`
5. ⚠️ `qwen` → 保持不变（没有找到明确证据）

---

**文档维护者**: OpenCode Config Manager开发团队  
**验证时间**: 2026-01-28  
**文档版本**: v1.0.0

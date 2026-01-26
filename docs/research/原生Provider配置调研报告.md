# OpenCode 原生Provider配置调研报告

## 文档目的

本文档旨在全面调研OpenCode官方支持的所有原生Provider的配置方式，特别关注：
1. **auth.json中的key名称**（不是我们想当然的名字）
2. **API URL**（可能有OpenCode专用endpoint）
3. **模型列表API**（如何动态获取模型）
4. **环境变量名称**
5. **特殊配置要求**

## 核心发现

### 1. 认证文件位置
```
~/.local/share/opencode/auth.json
```

### 2. auth.json结构
```json
{
  "provider-key": {
    "type": "api",
    "key": "actual-api-key"
  }
}
```

### 3. 配置文件位置
```
~/.config/opencode/opencode.json
```

### 4. 配置原则
- **API Key存储在auth.json中，不存储在opencode.json中**
- **opencode.json只声明使用哪个Provider和模型配置**
- **支持环境变量覆盖**

---

## 国内厂商Provider配置（重点）

### 1. 智谱AI (Zhipu AI)

#### 1.1 普通版本
**auth.json key名称**: `zhipuai`
```json
{
  "zhipuai": {
    "type": "api",
    "key": "your-api-key.xxx"
  }
}
```

**API URL**: `https://open.bigmodel.cn/api/paas/v4`

**环境变量**: `ZHIPU_API_KEY`

**opencode.json配置**:
```json
{
  "provider": {
    "zhipuai": {
      "models": {
        "glm-4-plus": {},
        "glm-4-flash": {},
        "glm-4.6": {},
        "glm-4.6v": {},
        "glm-4.7": {}
      }
    }
  }
}
```

**可用模型**:
- glm-4-plus
- glm-4-flash
- glm-4.6
- glm-4.6v
- glm-4.6v-flash
- glm-4.7

**模型列表API**: `https://open.bigmodel.cn/api/paas/v4/models`

---

#### 1.2 Coding Plan版本（OpenCode专用）⭐⭐⭐

**auth.json key名称**: `zhipuai-coding-plan` （不是 `zhipu`！）

```json
{
  "zhipuai-coding-plan": {
    "type": "api",
    "key": "9b28de1ce4a34e468da2d848d8211fd7.luFZ1vWnEGQnA4ip"
  }
}
```

**API URL**: `https://open.bigmodel.cn/api/coding/paas/v4` （注意是 `/coding/` 路径！）

**环境变量**: `ZHIPU_API_KEY`

**官方文档**: https://docs.bigmodel.cn/cn/coding-plan/overview

**opencode.json配置**:
```json
{
  "provider": {
    "zhipuai-coding-plan": {
      "models": {
        "glm-4.5": {},
        "glm-4.5-air": {},
        "glm-4.5-flash": {},
        "glm-4.5v": {},
        "glm-4.6": {},
        "glm-4.6v": {},
        "glm-4.6v-flash": {},
        "glm-4.7": {}
      }
    }
  }
}
```

**可用模型**:
- glm-4.5
- glm-4.5-air
- glm-4.5-flash
- glm-4.5v
- glm-4.6
- glm-4.6v
- glm-4.6v-flash
- glm-4.7

**模型列表API**: `https://open.bigmodel.cn/api/coding/paas/v4/models`

**特殊说明**:
- Coding Plan是智谱AI专门为OpenCode提供的订阅计划
- 使用不同的API endpoint（`/coding/` 路径）
- 需要在智谱AI官网订阅Coding Plan
- 价格和配额与普通版本不同

---

### 2. MiniMax

**auth.json key名称**: `minimax`

```json
{
  "minimax": {
    "type": "api",
    "key": "your-api-key"
  }
}
```

**API URL**: `https://api.minimax.chat/v1`

**环境变量**: `MINIMAX_API_KEY`

**官方文档**: https://platform.minimax.io/

**opencode.json配置**:
```json
{
  "provider": {
    "minimax": {
      "models": {
        "abab6.5s-chat": {},
        "abab6.5g-chat": {},
        "abab6.5t-chat": {}
      }
    }
  }
}
```

**可用模型**:
- abab6.5s-chat
- abab6.5g-chat
- abab6.5t-chat

**模型列表API**: 需要调研（可能不支持动态获取）

---

### 3. Moonshot AI (Kimi)

**auth.json key名称**: `moonshot`

```json
{
  "moonshot": {
    "type": "api",
    "key": "your-api-key"
  }
}
```

**API URL**: `https://api.moonshot.cn/v1`

**环境变量**: `MOONSHOT_API_KEY`

**官方文档**: https://platform.moonshot.ai/

**opencode.json配置**:
```json
{
  "provider": {
    "moonshot": {
      "models": {
        "moonshot-v1-8k": {},
        "moonshot-v1-32k": {},
        "moonshot-v1-128k": {}
      }
    }
  }
}
```

**可用模型**:
- moonshot-v1-8k
- moonshot-v1-32k
- moonshot-v1-128k
- kimi-k2 (最新)

**模型列表API**: `https://api.moonshot.cn/v1/models`

---

### 4. Z.AI

#### 4.1 普通版本

**auth.json key名称**: `zai`

```json
{
  "zai": {
    "type": "api",
    "key": "your-api-key"
  }
}
```

**API URL**: `https://api.z.ai/v1`

**环境变量**: `ZAI_API_KEY`

**opencode.json配置**:
```json
{
  "provider": {
    "zai": {
      "models": {
        "glm-4.7": {},
        "glm-4.6": {}
      }
    }
  }
}
```

---

#### 4.2 Coding Plan版本（OpenCode专用）⭐⭐⭐

**auth.json key名称**: `zai-coding-plan`

```json
{
  "zai-coding-plan": {
    "type": "api",
    "key": "your-api-key"
  }
}
```

**API URL**: 需要调研（可能与普通版本不同）

**环境变量**: `ZAI_API_KEY`

**官方文档**: https://docs.z.ai/devpack/overview

**特殊说明**:
- Z.AI Coding Plan是专门为开发者提供的订阅计划
- 可能包含额外的模型或功能

---

## 国际厂商Provider配置

### 1. Anthropic (Claude)

**auth.json key名称**: `anthropic`

```json
{
  "anthropic": {
    "type": "api",
    "key": "sk-ant-xxx"
  }
}
```

**API URL**: `https://api.anthropic.com/v1`

**环境变量**: `ANTHROPIC_API_KEY`

**opencode.json配置**:
```json
{
  "provider": {
    "anthropic": {
      "models": {
        "claude-sonnet-4-5-20250929": {},
        "claude-opus-4-20250514": {},
        "claude-haiku-4-20250514": {}
      }
    }
  }
}
```

**可用模型**:
- claude-sonnet-4-5-20250929
- claude-opus-4-20250514
- claude-haiku-4-20250514
- claude-3-5-sonnet-20241022
- claude-3-5-haiku-20241022

**模型列表API**: 不支持（需要使用预设列表）

**特殊配置**:
- 支持Claude Pro/Max订阅（通过OAuth认证）
- 支持API Key认证

---

### 2. OpenAI

**auth.json key名称**: `openai`

```json
{
  "openai": {
    "type": "api",
    "key": "sk-xxx"
  }
}
```

**API URL**: `https://api.openai.com/v1`

**环境变量**: `OPENAI_API_KEY`

**opencode.json配置**:
```json
{
  "provider": {
    "openai": {
      "models": {
        "gpt-5": {},
        "gpt-4o": {},
        "gpt-4o-mini": {},
        "o1": {},
        "o1-mini": {}
      }
    }
  }
}
```

**可用模型**:
- gpt-5
- gpt-4o
- gpt-4o-mini
- o1
- o1-mini
- o3-mini

**模型列表API**: `https://api.openai.com/v1/models`

**特殊配置**:
- 支持ChatGPT Plus/Pro订阅（通过OAuth认证）
- 支持API Key认证

---

### 3. Google (Gemini)

**auth.json key名称**: `google` 或 `google-generative-ai`

```json
{
  "google": {
    "type": "api",
    "key": "your-api-key"
  }
}
```

**API URL**: `https://generativelanguage.googleapis.com/v1beta`

**环境变量**: `GOOGLE_API_KEY` 或 `GOOGLE_GENERATIVE_AI_API_KEY`

**opencode.json配置**:
```json
{
  "provider": {
    "google": {
      "models": {
        "gemini-2.0-flash-exp": {},
        "gemini-1.5-pro": {},
        "gemini-1.5-flash": {}
      }
    }
  }
}
```

**可用模型**:
- gemini-2.0-flash-exp
- gemini-1.5-pro
- gemini-1.5-flash
- gemini-1.5-flash-8b

**模型列表API**: `https://generativelanguage.googleapis.com/v1beta/models`

---

### 4. DeepSeek

**auth.json key名称**: `deepseek`

```json
{
  "deepseek": {
    "type": "api",
    "key": "your-api-key"
  }
}
```

**API URL**: `https://api.deepseek.com/v1`

**环境变量**: `DEEPSEEK_API_KEY`

**opencode.json配置**:
```json
{
  "provider": {
    "deepseek": {
      "models": {
        "deepseek-chat": {},
        "deepseek-reasoner": {}
      }
    }
  }
}
```

**可用模型**:
- deepseek-chat
- deepseek-reasoner

**模型列表API**: `https://api.deepseek.com/v1/models`

---

### 5. OpenCode Zen（官方）⭐⭐⭐

**auth.json key名称**: `opencode`

```json
{
  "opencode": {
    "type": "api",
    "key": "sk-Yxf8dPbBMs3CjAru7wDc13VpCtoNOFLgNC0aBhSu9JNFR6WUpt7BcAJYH9YIMFVK"
  }
}
```

**API URL**: `https://api.opencode.ai/v1`

**环境变量**: `OPENCODE_API_KEY`

**官方文档**: https://opencode.ai/zen

**opencode.json配置**:
```json
{
  "provider": {
    "opencode": {
      "models": {
        "qwen-3-coder-480b": {},
        "claude-sonnet-4-5": {},
        "gpt-5": {}
      }
    }
  }
}
```

**特殊说明**:
- OpenCode Zen是OpenCode官方提供的模型服务
- 包含经过测试和验证的模型
- 需要在opencode.ai/auth注册并添加支付方式
- 价格透明，按使用量计费

---

### 6. GitHub Copilot

**auth.json key名称**: `github-copilot`

```json
{
  "github-copilot": {
    "type": "oauth",
    "token": "gho_xxx"
  }
}
```

**API URL**: `https://api.githubcopilot.com`

**环境变量**: 不支持（必须通过OAuth认证）

**认证方式**: 
1. 运行 `/connect` 命令
2. 选择 GitHub Copilot
3. 访问 github.com/login/device
4. 输入设备码

**opencode.json配置**:
```json
{
  "provider": {
    "github-copilot": {
      "models": {
        "gpt-4o": {},
        "claude-sonnet-4": {},
        "o1-preview": {}
      }
    }
  }
}
```

**可用模型**:
- gpt-4o
- gpt-4o-mini
- claude-sonnet-4
- claude-sonnet-3.5
- o1-preview
- o1-mini

**特殊说明**:
- 需要GitHub Copilot订阅（个人版或企业版）
- 部分模型需要Pro+订阅
- 部分模型需要在GitHub Copilot设置中手动启用

---

### 7. Azure OpenAI

**auth.json key名称**: `azure`

```json
{
  "azure": {
    "type": "api",
    "key": "your-api-key"
  }
}
```

**API URL**: `https://{RESOURCE_NAME}.openai.azure.com/`

**环境变量**: 
- `AZURE_API_KEY`
- `AZURE_RESOURCE_NAME` (必需)

**opencode.json配置**:
```json
{
  "provider": {
    "azure": {
      "options": {
        "resourceName": "your-resource-name"
      },
      "models": {
        "gpt-4o": {},
        "gpt-4": {}
      }
    }
  }
}
```

**特殊说明**:
- 需要在Azure Portal创建Azure OpenAI资源
- 需要在Azure AI Foundry部署模型
- 部署名称必须与模型名称匹配
- 如果遇到内容过滤错误，尝试将过滤器从DefaultV2改为Default

---

### 8. Groq

**auth.json key名称**: `groq`

```json
{
  "groq": {
    "type": "api",
    "key": "gsk_xxx"
  }
}
```

**API URL**: `https://api.groq.com/openai/v1`

**环境变量**: `GROQ_API_KEY`

**opencode.json配置**:
```json
{
  "provider": {
    "groq": {
      "models": {
        "llama-3.3-70b-versatile": {},
        "mixtral-8x7b-32768": {}
      }
    }
  }
}
```

**可用模型**:
- llama-3.3-70b-versatile
- llama-3.1-70b-versatile
- mixtral-8x7b-32768
- gemma2-9b-it

**模型列表API**: `https://api.groq.com/openai/v1/models`

---

## 当前软件存在的问题

### 1. 认证管理问题

**问题描述**:
- ❌ 当前软件完全没有处理 `~/.local/share/opencode/auth.json` 文件
- ❌ 把API Key错误地写入 `opencode.json` 的 `provider.xxx.apiKey` 字段
- ❌ AuthManager类读写的是错误的文件位置

**正确做法**:
- ✅ API Key应该存储在 `~/.local/share/opencode/auth.json`
- ✅ `opencode.json` 中不应该包含API Key
- ✅ 支持环境变量覆盖

---

### 2. Provider Key名称错误

**问题描述**:
- ❌ 智谱GLM使用 `zhipu` 作为key，实际应该是 `zhipuai` 或 `zhipuai-coding-plan`
- ❌ 没有区分普通版本和Coding Plan版本
- ❌ 其他Provider的key名称可能也不正确

**正确做法**:
- ✅ 使用OpenCode官方定义的Provider key名称
- ✅ 区分普通版本和Coding Plan版本
- ✅ 参考 models.dev 的Provider列表

---

### 3. API URL错误

**问题描述**:
- ❌ 智谱GLM Coding Plan使用普通API URL，实际应该是 `/coding/` 路径
- ❌ 没有考虑到厂商可能有OpenCode专用endpoint
- ❌ 硬编码API URL，不支持自定义

**正确做法**:
- ✅ 使用正确的API URL
- ✅ 智谱Coding Plan: `https://open.bigmodel.cn/api/coding/paas/v4`
- ✅ 智谱普通版: `https://open.bigmodel.cn/api/paas/v4`
- ✅ 支持在opencode.json中自定义baseURL

---

### 4. 模型列表问题

**问题描述**:
- ❌ 模型列表是硬编码的预设列表
- ❌ 无法动态获取Provider的最新模型
- ❌ 用户配置Provider后看不到可用模型

**正确做法**:
- ✅ 对于支持模型列表API的Provider，调用API动态获取
- ✅ 智谱GLM: `GET https://open.bigmodel.cn/api/paas/v4/models`
- ✅ OpenAI: `GET https://api.openai.com/v1/models`
- ✅ 对于不支持的Provider，使用预设列表
- ✅ 缓存模型列表，避免频繁请求

---

### 5. 环境变量检测不完整

**问题描述**:
- ❌ 只检测了部分环境变量
- ❌ 环境变量名称可能不正确
- ❌ 没有检测Coding Plan相关的环境变量

**正确做法**:
- ✅ 检测所有官方支持的环境变量
- ✅ 智谱: `ZHIPU_API_KEY`
- ✅ OpenAI: `OPENAI_API_KEY`
- ✅ Anthropic: `ANTHROPIC_API_KEY`
- ✅ 等等

---

### 6. 配置验证缺失

**问题描述**:
- ❌ 配置后无法验证API Key是否有效
- ❌ 无法测试连接
- ❌ 用户不知道配置是否成功

**正确做法**:
- ✅ 添加"测试连接"功能
- ✅ 调用API验证Key是否有效
- ✅ 显示验证结果（成功/失败/错误信息）
- ✅ 对于模型列表API，验证时同时获取模型列表

---

## 重构计划

### 阶段1：AuthManager重构

**目标**: 正确处理 `~/.local/share/opencode/auth.json`

**任务**:
1. 修改AuthManager类，读写正确的文件路径
2. 实现auth.json的读取、写入、更新、删除
3. 支持多种认证类型（api、oauth）
4. 添加环境变量检测功能
5. 添加"从auth.json导入"功能

**文件**:
- `opencode_config_manager_fluent.py` - AuthManager类

---

### 阶段2：NativeProviderPage重构

**目标**: 正确配置原生Provider

**任务**:
1. 修改配置逻辑，API Key写入auth.json而不是opencode.json
2. 使用正确的Provider key名称
3. 使用正确的API URL
4. 区分普通版本和Coding Plan版本
5. 添加"测试连接"功能
6. 添加"获取模型列表"功能

**文件**:
- `opencode_config_manager_fluent.py` - NativeProviderPage类

---

### 阶段3：模型列表动态获取

**目标**: 动态获取Provider的模型列表

**任务**:
1. 实现模型列表API调用
2. 智谱GLM: `GET https://open.bigmodel.cn/api/paas/v4/models`
3. 智谱Coding Plan: `GET https://open.bigmodel.cn/api/coding/paas/v4/models`
4. OpenAI: `GET https://api.openai.com/v1/models`
5. Google: `GET https://generativelanguage.googleapis.com/v1beta/models`
6. 添加模型列表缓存
7. 添加"刷新模型列表"功能

**文件**:
- `opencode_config_manager_fluent.py` - 新增ModelListFetcher类

---

### 阶段4：Provider配置模板

**目标**: 提供正确的Provider配置模板

**任务**:
1. 更新所有Provider的配置模板
2. 使用正确的key名称、API URL、环境变量
3. 添加Coding Plan版本的模板
4. 添加配置说明和文档链接

**文件**:
- `opencode_config_manager_fluent.py` - NATIVE_PROVIDERS常量

---

### 阶段5：测试和验证

**目标**: 确保所有Provider配置正确

**任务**:
1. 测试每个Provider的配置流程
2. 验证API Key存储位置正确
3. 验证模型列表获取正确
4. 验证测试连接功能正常
5. 更新用户文档

**测试清单**:
- [ ] 智谱GLM普通版
- [ ] 智谱GLM Coding Plan
- [ ] MiniMax
- [ ] Moonshot AI (Kimi)
- [ ] Z.AI
- [ ] Z.AI Coding Plan
- [ ] Anthropic
- [ ] OpenAI
- [ ] Google
- [ ] DeepSeek
- [ ] OpenCode Zen
- [ ] GitHub Copilot
- [ ] Azure OpenAI
- [ ] Groq

---

## 参考资料

### 官方文档
- OpenCode Providers: https://opencode.ai/docs/providers/
- OpenCode Config: https://opencode.ai/docs/config/
- OpenCode Zen: https://opencode.ai/zen
- AI SDK: https://ai-sdk.dev/
- Models.dev: https://models.dev

### 国内厂商文档
- 智谱AI Coding Plan: https://docs.bigmodel.cn/cn/coding-plan/overview
- 智谱AI API: https://open.bigmodel.cn/dev/api
- MiniMax API: https://platform.minimax.io/
- Moonshot AI API: https://platform.moonshot.ai/
- Z.AI: https://docs.z.ai/

### GitHub仓库参考
- anomalyco/opencode: https://github.com/anomalyco/opencode
- VoltAgent/voltagent: https://github.com/VoltAgent/voltagent
- mastra-ai/mastra: https://github.com/mastra-ai/mastra
- code-yeongyu/oh-my-opencode: https://github.com/code-yeongyu/oh-my-opencode

---

## 附录：完整Provider列表

### 支持的Provider（按字母排序）

1. 302.AI
2. Amazon Bedrock
3. Anthropic ⭐
4. Azure OpenAI
5. Azure Cognitive Services
6. Baseten
7. Cerebras
8. Cloudflare AI Gateway
9. Cortecs
10. DeepSeek ⭐
11. Deep Infra
12. Firmware
13. Fireworks AI
14. GitLab Duo
15. GitHub Copilot ⭐
16. Google Vertex AI ⭐
17. Groq
18. Hugging Face
19. Helicone
20. llama.cpp (本地)
21. IO.NET
22. LM Studio (本地)
23. Moonshot AI (Kimi) ⭐
24. MiniMax ⭐
25. Nebius Token Factory
26. Ollama (本地)
27. Ollama Cloud
28. OpenAI ⭐
29. OpenCode Zen ⭐
30. OpenRouter
31. SAP AI Core
32. OVHcloud AI Endpoints
33. Scaleway
34. Together AI
35. Venice AI
36. Vercel AI Gateway
37. xAI
38. Z.AI ⭐
39. Z.AI Coding Plan ⭐
40. ZenMux
41. Zhipu AI (智谱GLM) ⭐
42. Zhipu AI Coding Plan (智谱GLM Coding Plan) ⭐

**标注说明**:
- ⭐ = 重点支持的Provider
- (本地) = 本地模型服务

---

## 更新日志

- 2026-01-27: 初始版本，完成基础调研
- 待补充: 每个Provider的详细测试结果
- 待补充: 模型列表API的响应格式
- 待补充: 特殊配置要求的详细说明

---

**文档维护者**: OpenCode Config Manager开发团队  
**最后更新**: 2026-01-27  
**文档版本**: v1.0.0

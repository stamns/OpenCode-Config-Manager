# 原生Provider与CLI导出功能技术说明

## 日期
2026-01-26 18:30

## 责任人
开发团队

## 背景 / 问题描述

用户对以下几个概念存在混淆：
1. **原生Provider（Native Provider）** 的作用和配置方式
2. **CLI工具导出** 的作用和使用场景
3. 两者之间的关系和区别
4. `modelListUrl` 字段的作用和是否应该写入配置文件

## 核心概念说明

### 1. 原生Provider（Native Provider）

**定义**：原生Provider是OpenCode官方支持的AI服务提供商，通过AI SDK直接集成。

**作用**：
- 在OpenCode中**直接使用**这些AI服务
- 通过标准化的SDK接口调用模型
- 支持完整的OpenCode功能（工具调用、流式输出、上下文管理等）

**支持的Provider列表**（共16个）：
1. Anthropic (Claude)
2. OpenAI
3. Google Gemini
4. Amazon Bedrock
5. Azure OpenAI
6. GitHub Copilot
7. xAI (Grok)
8. Groq
9. OpenRouter
10. Google Vertex AI
11. DeepSeek
12. 智谱 GLM
13. 千问 Qwen
14. Kimi (月之暗面)
15. 零一万物 Yi
16. MiniMax

**配置方式**：
```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "zhipu": {
      "options": {
        "baseURL": "https://open.bigmodel.cn/api/paas/v4/"
      },
      "models": {
        "glm-4-plus": {
          "name": "GLM-4 Plus"
        }
      }
    }
  },
  "model": "zhipu/glm-4-plus"
}
```

**关键点**：
- 配置写入 `~/.config/opencode/opencode.json`
- 使用 `@ai-sdk/*` 系列npm包
- 支持OpenCode的所有高级功能

### 2. CLI工具导出

**定义**：CLI工具导出是将OpenCode的配置**转换**为其他AI编程工具的配置格式。

**作用**：
- 从OpenCode配置**导出**到其他工具
- 支持的目标工具：
  - **Claude Code** (Anthropic官方CLI)
  - **Codex** (OpenAI官方CLI)
  - **Gemini Code Assist** (Google官方CLI)

**使用场景**：
```
OpenCode配置 → 导出 → Claude Code配置
OpenCode配置 → 导出 → Codex配置
OpenCode配置 → 导出 → Gemini配置
```

**导出流程**：
1. 在OpenCode Config Manager中配置Provider和Model
2. 点击"CLI导出"页面
3. 选择目标工具（Claude Code / Codex / Gemini）
4. 预览生成的配置文件
5. 一键写入到目标工具的配置路径

**关键点**：
- 这是**单向转换**，不是双向同步
- 导出的配置文件格式不同：
  - Claude Code: `auth.json` + `config.toml`
  - Codex: `.env` + `settings.json`
  - Gemini: `.env` + `settings.json`

### 3. 两者的关系

```
┌─────────────────────────────────────────────────────────┐
│                  OpenCode Config Manager                 │
│                                                          │
│  ┌────────────────────┐      ┌────────────────────┐   │
│  │  原生Provider配置   │      │   CLI工具导出      │   │
│  │                    │      │                    │   │
│  │  • 智谱GLM         │      │  • Claude Code     │   │
│  │  • 千问Qwen        │      │  • Codex           │   │
│  │  • Kimi            │      │  • Gemini          │   │
│  │  • 零一万物Yi      │      │                    │   │
│  │  • MiniMax         │      │                    │   │
│  │  • Anthropic       │      │                    │   │
│  │  • OpenAI          │      │                    │   │
│  │  • ...             │      │                    │   │
│  └────────────────────┘      └────────────────────┘   │
│           │                           │                │
│           ↓                           ↓                │
│  写入 opencode.json          导出到其他工具配置       │
└─────────────────────────────────────────────────────────┘
```

**区别总结**：

| 维度 | 原生Provider | CLI工具导出 |
|------|-------------|------------|
| **用途** | 在OpenCode中使用AI服务 | 将配置导出到其他工具 |
| **方向** | 配置 → OpenCode使用 | OpenCode配置 → 其他工具 |
| **配置文件** | `opencode.json` | `auth.json`, `config.toml`, `.env`, `settings.json` |
| **支持的Provider** | 16个官方Provider | 仅支持Anthropic/OpenAI/Google |
| **功能完整性** | 完整支持所有OpenCode功能 | 受目标工具限制 |
| **使用场景** | 主要使用OpenCode | 使用多个AI编程工具 |

## OpenCode官方支持的配置字段

根据OpenCode官方文档（https://opencode.ai/docs/config/），Provider配置支持的字段：

### 通用字段（所有Provider）
```json
{
  "provider": {
    "provider-id": {
      "npm": "@ai-sdk/package-name",  // SDK包名
      "name": "Provider Display Name", // 显示名称
      "options": {
        "apiKey": "xxx",              // API密钥
        "baseURL": "https://...",     // API端点
        "timeout": 600000,            // 超时时间（毫秒）
        "setCacheKey": true,          // 缓存键设置
        "headers": {}                 // 自定义请求头
      },
      "models": {
        "model-id": {
          "name": "Model Display Name",
          "id": "actual-model-id",    // 实际模型ID（可选）
          "limit": {
            "context": 128000,
            "output": 4096
          },
          "options": {},              // 模型级别的options
          "variants": {}              // 模型变体配置
        }
      }
    }
  }
}
```

### Provider特定字段

#### Amazon Bedrock
```json
{
  "options": {
    "region": "us-east-1",
    "profile": "my-aws-profile",
    "endpoint": "https://..."  // VPC端点
  }
}
```

#### Azure OpenAI
```json
{
  "options": {
    "resourceName": "my-resource"
  }
}
```

### ❌ 不支持的字段

OpenCode官方文档中**没有**提到以下字段：
- `modelListUrl` - 这个字段不存在于官方配置规范中
- `description` - 仅用于UI显示，不应写入配置
- `tags` - 仅用于UI显示，不应写入配置
- `homepage` - 仅用于UI显示，不应写入配置
- `docs` - 仅用于UI显示，不应写入配置

## 智谱GLM配置问题分析

### 问题现象
用户配置智谱GLM后，在OpenCode中不生效。

### 根本原因

根据智谱官方文档（https://docs.bigmodel.cn/cn/coding-plan/tool/opencode），智谱GLM有两种配置方式：

#### 方式一：使用Coding Plan专属端点（推荐）
```json
{
  "provider": {
    "zhipuai": {
      "api": "https://open.bigmodel.cn/api/coding/paas/v4"
    }
  }
}
```

**注意**：这里使用的是 `api` 字段，不是 `baseURL`！

#### 方式二：使用通用端点
```json
{
  "provider": {
    "zhipu": {
      "options": {
        "baseURL": "https://open.bigmodel.cn/api/paas/v4/"
      }
    }
  }
}
```

### 我们的配置问题

当前代码中智谱GLM的配置：
```python
NativeProviderConfig(
    id="zhipu",
    name="智谱 GLM",
    sdk="@ai-sdk/openai-compatible",
    option_fields=[
        OptionField(
            "baseURL",
            "Base URL",
            "text",
            [],
            "https://open.bigmodel.cn/api/paas/v4/",  # 通用端点
        ),
    ],
)
```

**问题**：
1. 默认使用通用端点，不是Coding Plan专属端点
2. 用户可能需要使用Coding Plan端点才能获得完整功能
3. 没有提供切换端点的选项

## 解决方案

### 1. 移除 `modelListUrl` 字段

**原因**：
- OpenCode官方不支持此字段
- 这是我们自己添加的非标准字段
- 会导致配置文件不符合OpenCode规范

**修改位置**：
- 移除UI中的"模型列表地址"输入框
- 移除保存配置时写入 `modelListUrl` 的逻辑
- 移除读取配置时处理 `modelListUrl` 的逻辑

### 2. 修复智谱GLM配置

**方案A：提供端点选择**
```python
NativeProviderConfig(
    id="zhipu",
    name="智谱 GLM",
    sdk="@ai-sdk/openai-compatible",
    option_fields=[
        OptionField(
            "baseURL",
            "API端点",
            "select",
            [
                "https://open.bigmodel.cn/api/coding/paas/v4",  # Coding Plan专属
                "https://open.bigmodel.cn/api/paas/v4/",        # 通用端点
            ],
            "https://open.bigmodel.cn/api/coding/paas/v4",  # 默认使用Coding Plan
        ),
    ],
)
```

**方案B：添加说明文档**
在Provider配置页面添加提示：
```
智谱GLM配置说明：
- Coding Plan端点：https://open.bigmodel.cn/api/coding/paas/v4
  （推荐，支持完整的编程功能）
- 通用端点：https://open.bigmodel.cn/api/paas/v4/
  （基础功能）
```

### 3. 清理非标准字段

移除以下字段的写入逻辑：
- `description` - 仅在UI中使用
- `tags` - 仅在UI中使用
- `homepage` - 仅在UI中使用
- `docs` - 仅在UI中使用
- `modelListUrl` - 非标准字段

## 测试验证

### 测试用例1：智谱GLM配置
1. 添加智谱GLM Provider
2. 配置API Key
3. 选择Coding Plan端点
4. 保存配置
5. 检查 `opencode.json` 中只包含标准字段
6. 在OpenCode中测试模型调用

### 测试用例2：CLI导出
1. 配置Anthropic Provider
2. 导出到Claude Code
3. 检查生成的 `auth.json` 和 `config.toml`
4. 验证Claude Code可以正常使用

### 测试用例3：配置文件验证
1. 保存Provider配置
2. 检查 `opencode.json` 不包含非标准字段
3. 使用OpenCode官方工具验证配置文件

## 相关文件

### 需要修改的文件
- `opencode_config_manager_fluent.py`
  - 移除 `modelListUrl` 相关代码（第1493, 5072, 6278, 8115, 8145, 8152行）
  - 修改智谱GLM配置（第673-691行）
  - 清理非标准字段的写入逻辑

### 参考文档
- OpenCode官方配置文档：https://opencode.ai/docs/config/
- OpenCode Provider文档：https://opencode.ai/docs/providers/
- 智谱GLM OpenCode集成文档：https://docs.bigmodel.cn/cn/coding-plan/tool/opencode

## 版本信息
- 当前版本：v1.5.0
- 计划修复版本：v1.5.2
- 优先级：高

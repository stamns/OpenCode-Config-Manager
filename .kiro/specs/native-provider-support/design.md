# Design Document: Native Provider Support

## Overview

本设计文档描述了 OpenCode Config Manager 原生 Provider 支持功能的技术实现方案。该功能允许用户通过图形界面配置 OpenCode 官方支持的原生 AI 服务提供商，包括认证凭证管理和 Provider 选项配置。

### 原生 Provider vs 自定义 Provider 的区别

| 特性 | 原生 Provider | 自定义 Provider（现有功能） |
|------|--------------|---------------------------|
| 认证存储位置 | `~/.local/share/opencode/auth.json` | `opencode.json` 的 `provider.xxx.options.apiKey` |
| 配置方式 | `/connect` 命令或本工具 | 手动编辑 `opencode.json` |
| 需要 npm 字段 | 否（OpenCode 内置） | 是（指定 SDK 包） |
| 认证方式 | 多样化（API Key、OAuth、AWS 凭证等） | 仅 API Key |
| Provider 选项 | `opencode.json` 的 `provider.xxx.options` | 同左 |

### 核心设计原则

1. **双文件配置模型**: 认证凭证存储在 `auth.json`，Provider 选项存储在 `opencode.json`
2. **环境变量优先**: 支持 `{env:VAR}` 格式引用环境变量，避免明文存储敏感信息
3. **与现有功能集成**: 原生 Provider 与自定义 Provider 共存，但使用不同的配置路径
4. **复用现有 Provider 选项管理**: `opencode.json` 中的 `provider.xxx.options` 部分复用现有的 ProviderPage 逻辑

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    OpenCode Config Manager                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  NativeProvider │  │   AuthManager   │  │ ProviderOptions │  │
│  │      Page       │  │                 │  │     Manager     │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
│           │                    │                    │           │
│           └────────────────────┼────────────────────┘           │
│                                │                                │
│  ┌─────────────────────────────┴─────────────────────────────┐  │
│  │                    ConfigService                           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐    │  │
│  │  │ AuthConfig  │  │ OpenCodeCfg │  │ EnvVarDetector  │    │  │
│  │  │   Reader    │  │   Reader    │  │                 │    │  │
│  │  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘    │  │
│  └─────────┼────────────────┼──────────────────┼─────────────┘  │
│            │                │                  │                │
└────────────┼────────────────┼──────────────────┼────────────────┘
             │                │                  │
             ▼                ▼                  ▼
    ~/.local/share/     opencode.json      Environment
    opencode/auth.json                      Variables
```

## Components and Interfaces

### 1. NativeProviderPage (UI Component)

新增的导航页面，用于管理原生 Provider 配置。

```python
class NativeProviderPage(QWidget):
    """原生 Provider 配置页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_manager = AuthManager()
        self.provider_options_manager = ProviderOptionsManager()
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI 布局"""
        # 左侧: Provider 列表
        # 右侧: 配置表单
        pass
    
    def _load_providers(self):
        """加载所有支持的原生 Provider"""
        pass
    
    def _on_provider_selected(self, provider_id: str):
        """Provider 选中事件处理"""
        pass
    
    def _save_provider_config(self, provider_id: str, config: dict):
        """保存 Provider 配置"""
        pass
    
    def _test_connection(self, provider_id: str):
        """测试 Provider 连接"""
        pass
```

### 2. AuthManager (认证管理器)

管理 `auth.json` 文件的读写操作。

```python
class AuthManager:
    """认证凭证管理器"""
    
    def __init__(self):
        self.auth_path = self._get_auth_path()
    
    def _get_auth_path(self) -> Path:
        """获取 auth.json 路径（跨平台）"""
        if sys.platform == "win32":
            base = Path(os.environ.get("LOCALAPPDATA", "")) / "opencode"
            if not base.exists():
                base = Path.home() / ".local" / "share" / "opencode"
        else:
            base = Path.home() / ".local" / "share" / "opencode"
        return base / "auth.json"
    
    def read_auth(self) -> dict:
        """读取 auth.json"""
        pass
    
    def write_auth(self, auth_data: dict):
        """写入 auth.json"""
        pass
    
    def get_provider_auth(self, provider_id: str) -> Optional[dict]:
        """获取指定 Provider 的认证信息"""
        pass
    
    def set_provider_auth(self, provider_id: str, auth_data: dict):
        """设置指定 Provider 的认证信息"""
        pass
    
    def delete_provider_auth(self, provider_id: str):
        """删除指定 Provider 的认证信息"""
        pass
    
    def mask_api_key(self, api_key: str) -> str:
        """遮蔽 API Key，只显示首尾 4 字符"""
        if len(api_key) <= 8:
            return "****"
        return f"{api_key[:4]}...{api_key[-4:]}"
```

### 3. ProviderOptionsManager (Provider 选项管理器)

管理 `opencode.json` 中的 Provider 选项配置。**注意：此功能复用现有的 Provider 管理逻辑，原生 Provider 的 options 部分与自定义 Provider 共享相同的配置结构。**

```python
class ProviderOptionsManager:
    """Provider 选项管理器 - 复用现有逻辑"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
    
    def get_provider_options(self, provider_id: str) -> dict:
        """获取 Provider 选项（从 opencode.json 的 provider.xxx.options）"""
        pass
    
    def set_provider_options(self, provider_id: str, options: dict):
        """设置 Provider 选项（保留现有配置）
        
        注意：原生 Provider 不需要 npm 字段，只设置 options
        """
        pass
    
    def delete_provider_options(self, provider_id: str):
        """删除 Provider 选项"""
        pass
```

**与现有 Provider 管理的区别：**
- 现有自定义 Provider 需要 `npm`、`name`、`options.baseURL`、`options.apiKey`
- 原生 Provider 只需要 `options`（如 `baseURL`、`region` 等），认证信息在 `auth.json`

### 4. EnvVarDetector (环境变量检测器)

检测系统中已设置的 Provider 相关环境变量。

```python
class EnvVarDetector:
    """环境变量检测器"""
    
    # Provider 与环境变量的映射
    PROVIDER_ENV_VARS = {
        "anthropic": ["ANTHROPIC_API_KEY"],
        "openai": ["OPENAI_API_KEY"],
        "gemini": ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        "amazon-bedrock": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_PROFILE", "AWS_REGION"],
        "azure": ["AZURE_OPENAI_API_KEY", "AZURE_RESOURCE_NAME"],
        "xai": ["XAI_API_KEY"],
        "groq": ["GROQ_API_KEY"],
        "openrouter": ["OPENROUTER_API_KEY"],
        "vertexai": ["GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "VERTEX_LOCATION"],
        "deepseek": ["DEEPSEEK_API_KEY"],
    }
    
    def detect_env_vars(self, provider_id: str) -> dict:
        """检测指定 Provider 的环境变量"""
        pass
    
    def detect_all_env_vars(self) -> dict:
        """检测所有 Provider 的环境变量"""
        pass
    
    def format_env_reference(self, var_name: str) -> str:
        """格式化环境变量引用"""
        return f"{{env:{var_name}}}"
```

### 5. NativeProviderRegistry (原生 Provider 注册表)

定义所有支持的原生 Provider 及其配置模式。

```python
@dataclass
class NativeProviderConfig:
    """原生 Provider 配置定义"""
    id: str                          # Provider ID
    name: str                        # 显示名称
    sdk: str                         # SDK 包名
    auth_fields: List[AuthField]     # 认证字段
    option_fields: List[OptionField] # 选项字段
    env_vars: List[str]              # 相关环境变量
    test_endpoint: Optional[str]     # 测试端点

@dataclass
class AuthField:
    """认证字段定义"""
    key: str           # 字段键名
    label: str         # 显示标签
    type: str          # 字段类型: text, password, file
    required: bool     # 是否必填
    placeholder: str   # 占位符文本

@dataclass
class OptionField:
    """选项字段定义"""
    key: str           # 字段键名
    label: str         # 显示标签
    type: str          # 字段类型: text, select
    options: List[str] # 可选值（select 类型）
    default: str       # 默认值

NATIVE_PROVIDERS = [
    NativeProviderConfig(
        id="anthropic",
        name="Anthropic (Claude)",
        sdk="@ai-sdk/anthropic",
        auth_fields=[
            AuthField("apiKey", "API Key", "password", True, "sk-ant-..."),
        ],
        option_fields=[
            OptionField("baseURL", "Base URL", "text", [], ""),
        ],
        env_vars=["ANTHROPIC_API_KEY"],
        test_endpoint="/v1/models",
    ),
    NativeProviderConfig(
        id="openai",
        name="OpenAI",
        sdk="@ai-sdk/openai",
        auth_fields=[
            AuthField("apiKey", "API Key", "password", True, "sk-..."),
        ],
        option_fields=[
            OptionField("baseURL", "Base URL", "text", [], ""),
        ],
        env_vars=["OPENAI_API_KEY"],
        test_endpoint="/v1/models",
    ),
    NativeProviderConfig(
        id="gemini",
        name="Google Gemini",
        sdk="@ai-sdk/google",
        auth_fields=[
            AuthField("apiKey", "API Key", "password", True, ""),
        ],
        option_fields=[
            OptionField("baseURL", "Base URL", "text", [], ""),
        ],
        env_vars=["GEMINI_API_KEY", "GOOGLE_API_KEY"],
        test_endpoint="/v1/models",
    ),
    NativeProviderConfig(
        id="amazon-bedrock",
        name="Amazon Bedrock",
        sdk="@ai-sdk/amazon-bedrock",
        auth_fields=[
            AuthField("accessKeyId", "Access Key ID", "password", False, "AKIA..."),
            AuthField("secretAccessKey", "Secret Access Key", "password", False, ""),
            AuthField("profile", "AWS Profile", "text", False, "default"),
        ],
        option_fields=[
            OptionField("region", "Region", "select", 
                       ["us-east-1", "us-west-2", "eu-west-1", "ap-northeast-1"], "us-east-1"),
            OptionField("endpoint", "VPC Endpoint", "text", [], ""),
        ],
        env_vars=["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_PROFILE", "AWS_REGION"],
        test_endpoint=None,
    ),
    NativeProviderConfig(
        id="azure",
        name="Azure OpenAI",
        sdk="@ai-sdk/azure",
        auth_fields=[
            AuthField("apiKey", "API Key", "password", True, ""),
            AuthField("resourceName", "Resource Name", "text", True, ""),
        ],
        option_fields=[
            OptionField("baseURL", "Base URL", "text", [], ""),
        ],
        env_vars=["AZURE_OPENAI_API_KEY", "AZURE_RESOURCE_NAME"],
        test_endpoint=None,
    ),
    NativeProviderConfig(
        id="copilot",
        name="GitHub Copilot",
        sdk="@ai-sdk/openai",
        auth_fields=[
            AuthField("token", "GitHub Token", "password", True, ""),
        ],
        option_fields=[],
        env_vars=[],
        test_endpoint=None,
    ),
    NativeProviderConfig(
        id="xai",
        name="xAI (Grok)",
        sdk="@ai-sdk/xai",
        auth_fields=[
            AuthField("apiKey", "API Key", "password", True, ""),
        ],
        option_fields=[
            OptionField("baseURL", "Base URL", "text", [], ""),
        ],
        env_vars=["XAI_API_KEY"],
        test_endpoint="/v1/models",
    ),
    NativeProviderConfig(
        id="groq",
        name="Groq",
        sdk="@ai-sdk/groq",
        auth_fields=[
            AuthField("apiKey", "API Key", "password", True, "gsk_..."),
        ],
        option_fields=[
            OptionField("baseURL", "Base URL", "text", [], ""),
        ],
        env_vars=["GROQ_API_KEY"],
        test_endpoint="/openai/v1/models",
    ),
    NativeProviderConfig(
        id="openrouter",
        name="OpenRouter",
        sdk="@ai-sdk/openai-compatible",
        auth_fields=[
            AuthField("apiKey", "API Key", "password", True, "sk-or-..."),
        ],
        option_fields=[
            OptionField("baseURL", "Base URL", "text", [], "https://openrouter.ai/api/v1"),
        ],
        env_vars=["OPENROUTER_API_KEY"],
        test_endpoint="/models",
    ),
    NativeProviderConfig(
        id="vertexai",
        name="Google Vertex AI",
        sdk="@ai-sdk/google-vertex",
        auth_fields=[
            AuthField("credentials", "Service Account JSON", "file", False, ""),
            AuthField("projectId", "Project ID", "text", True, ""),
        ],
        option_fields=[
            OptionField("location", "Location", "select",
                       ["global", "us-central1", "us-east1", "europe-west1", "asia-east1"], "global"),
        ],
        env_vars=["GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "VERTEX_LOCATION"],
        test_endpoint=None,
    ),
    NativeProviderConfig(
        id="deepseek",
        name="DeepSeek",
        sdk="@ai-sdk/openai-compatible",
        auth_fields=[
            AuthField("apiKey", "API Key", "password", True, "sk-..."),
        ],
        option_fields=[
            OptionField("baseURL", "Base URL", "text", [], "https://api.deepseek.com"),
        ],
        env_vars=["DEEPSEEK_API_KEY"],
        test_endpoint="/models",
    ),
    NativeProviderConfig(
        id="opencode",
        name="OpenCode Zen",
        sdk="@ai-sdk/openai-compatible",
        auth_fields=[
            AuthField("apiKey", "API Key", "password", True, ""),
        ],
        option_fields=[
            OptionField("baseURL", "Base URL", "text", [], "https://api.opencode.ai/v1"),
        ],
        env_vars=[],
        test_endpoint="/models",
    ),
]
```

## Data Models

### auth.json 结构

```json
{
  "anthropic": {
    "apiKey": "sk-ant-xxx..."
  },
  "openai": {
    "apiKey": "{env:OPENAI_API_KEY}"
  },
  "amazon-bedrock": {
    "accessKeyId": "{env:AWS_ACCESS_KEY_ID}",
    "secretAccessKey": "{env:AWS_SECRET_ACCESS_KEY}",
    "profile": "default"
  },
  "azure": {
    "apiKey": "xxx...",
    "resourceName": "my-resource"
  },
  "vertexai": {
    "projectId": "my-project",
    "credentials": "/path/to/service-account.json"
  }
}
```

### opencode.json provider 部分结构

```json
{
  "provider": {
    "anthropic": {
      "options": {
        "baseURL": "https://api.anthropic.com/v1"
      }
    },
    "amazon-bedrock": {
      "options": {
        "region": "us-east-1",
        "profile": "production",
        "endpoint": "https://bedrock-runtime.us-east-1.vpce-xxxxx.amazonaws.com"
      }
    },
    "vertexai": {
      "options": {
        "location": "global"
      }
    }
  }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Auth Config Round-Trip

*For any* valid authentication configuration, writing it to auth.json and then reading it back should produce an equivalent configuration object.

**Validates: Requirements 2.3, 5.1**

### Property 2: Provider Options Preservation

*For any* existing provider configuration in opencode.json, adding new options for a provider should preserve all existing options for that provider and other providers.

**Validates: Requirements 3.3, 3.4**

### Property 3: Environment Variable Reference Format

*For any* environment variable import, the resulting configuration value should match the format `{env:VARIABLE_NAME}` where VARIABLE_NAME is the original environment variable name.

**Validates: Requirements 2.4, 4.3**

### Property 4: API Key Masking

*For any* API key string with length > 8, the masked version should show exactly the first 4 characters, followed by "...", followed by the last 4 characters.

**Validates: Requirements 5.5**

### Property 5: Provider Auth Field Mapping

*For any* native provider, selecting it should display exactly the authentication fields defined in its NativeProviderConfig.auth_fields.

**Validates: Requirements 2.1**

### Property 6: Cross-Platform Path Resolution

*For any* operating system (Windows, macOS, Linux), the auth.json path should resolve to a valid, writable location within the user's home directory structure.

**Validates: Requirements 8.1, 8.3**

### Property 7: No Provider Duplication

*For any* provider configuration operation, there should never be duplicate entries for the same provider ID in either auth.json or the provider section of opencode.json.

**Validates: Requirements 7.4**

### Property 8: Credential Deletion Completeness

*For any* provider credential deletion, the provider entry should be completely removed from auth.json, and subsequent reads should not return any data for that provider.

**Validates: Requirements 5.4**

## Error Handling

### 文件操作错误

| 错误场景 | 处理方式 |
|---------|---------|
| auth.json 不存在 | 首次保存时自动创建 |
| auth.json 格式错误 | 显示错误提示，提供重置选项 |
| 目录不存在 | 自动创建父目录 |
| 权限不足 | 显示错误提示，建议检查权限 |
| 文件被锁定 | 重试或提示用户关闭其他程序 |

### 认证错误

| 错误场景 | 处理方式 |
|---------|---------|
| API Key 格式无效 | 显示格式要求提示 |
| 环境变量不存在 | 显示警告，允许保存引用 |
| 连接测试失败 | 显示 API 返回的错误信息 |

### 配置冲突

| 错误场景 | 处理方式 |
|---------|---------|
| 原生与自定义 Provider 重复 | 提示用户选择保留哪个 |
| 配置版本不兼容 | 提供迁移或重置选项 |

## Testing Strategy

### 单元测试

1. **AuthManager 测试**
   - 测试 auth.json 读写操作
   - 测试 API Key 遮蔽功能
   - 测试跨平台路径解析

2. **ProviderOptionsManager 测试**
   - 测试选项读写操作
   - 测试配置保留逻辑

3. **EnvVarDetector 测试**
   - 测试环境变量检测
   - 测试引用格式化

### 属性测试

使用 Hypothesis 库进行属性测试：

1. **Property 1**: Auth Config Round-Trip
   - 生成随机有效的认证配置
   - 写入后读取，验证等价性

2. **Property 4**: API Key Masking
   - 生成随机长度的 API Key 字符串
   - 验证遮蔽结果符合规则

3. **Property 7**: No Provider Duplication
   - 执行随机的配置操作序列
   - 验证无重复 Provider

### 集成测试

1. **UI 集成测试**
   - 测试 Provider 选择和配置流程
   - 测试环境变量导入流程

2. **文件系统集成测试**
   - 测试实际文件读写
   - 测试目录创建逻辑

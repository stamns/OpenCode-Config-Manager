# Requirements Document

## Introduction

本功能为 OpenCode Config Manager 添加原生 Provider 支持，允许用户配置和管理 OpenCode 官方支持的原生 AI 服务提供商（如 Anthropic、OpenAI、Google Gemini、AWS Bedrock、Azure OpenAI 等），而不仅仅是第三方 API 中转站。

根据 OpenCode 官方文档，原生 Provider 通过 `/connect` 命令配置，凭证存储在 `~/.local/share/opencode/auth.json`，而 Provider 选项配置在 `opencode.json` 的 `provider` 部分。

## Glossary

- **Native_Provider**: OpenCode 官方支持的原生 AI 服务提供商，如 Anthropic、OpenAI、Google Gemini 等
- **Auth_Config**: 存储在 `~/.local/share/opencode/auth.json` 中的认证凭证配置
- **Provider_Options**: 存储在 `opencode.json` 的 `provider` 部分的提供商选项配置
- **Config_Manager**: OpenCode Config Manager 应用程序
- **Environment_Variable**: 系统环境变量，用于存储 API 密钥等敏感信息

## Requirements

### Requirement 1: 原生 Provider 配置界面

**User Story:** As a user, I want to configure native AI providers through a dedicated UI, so that I can easily set up official provider connections without manually editing config files.

#### Acceptance Criteria

1. THE Config_Manager SHALL provide a dedicated "原生 Provider" page in the navigation menu
2. WHEN the user opens the native provider page, THE Config_Manager SHALL display a list of supported native providers with their configuration status
3. THE Config_Manager SHALL support the following native providers:
   - Anthropic (Claude)
   - OpenAI
   - Google Gemini
   - Amazon Bedrock
   - Azure OpenAI
   - GitHub Copilot
   - xAI (Grok)
   - Groq
   - OpenRouter
   - Google Vertex AI
   - DeepSeek
   - OpenCode Zen
4. WHEN a provider is configured, THE Config_Manager SHALL display a visual indicator showing the provider is active

### Requirement 2: Provider 认证配置

**User Story:** As a user, I want to configure API keys and authentication for native providers, so that I can connect to official AI services.

#### Acceptance Criteria

1. WHEN the user selects a provider to configure, THE Config_Manager SHALL display the appropriate authentication fields for that provider
2. THE Config_Manager SHALL support the following authentication methods:
   - API Key input (for Anthropic, OpenAI, Gemini, xAI, Groq, OpenRouter, DeepSeek)
   - AWS credentials (for Bedrock: Access Key, Secret Key, Region, Profile)
   - Azure credentials (for Azure OpenAI: Resource Name, API Key)
   - OAuth flow (for GitHub Copilot)
   - Google Cloud credentials (for Vertex AI: Project ID, Location, Service Account)
3. WHEN the user saves authentication credentials, THE Config_Manager SHALL write them to `~/.local/share/opencode/auth.json`
4. THE Config_Manager SHALL support environment variable references in the format `{env:VARIABLE_NAME}` for sensitive values
5. IF the user enters an invalid credential format, THEN THE Config_Manager SHALL display a validation error message

### Requirement 3: Provider 选项配置

**User Story:** As a user, I want to configure provider-specific options like base URL and region, so that I can customize how OpenCode connects to providers.

#### Acceptance Criteria

1. WHEN the user configures a provider, THE Config_Manager SHALL display provider-specific options fields
2. THE Config_Manager SHALL support the following provider options:
   - baseURL: Custom API endpoint (all providers)
   - region: AWS region (Bedrock)
   - profile: AWS profile name (Bedrock)
   - endpoint: VPC endpoint URL (Bedrock)
   - resourceName: Azure resource name (Azure OpenAI)
   - projectId: Google Cloud project ID (Vertex AI)
   - location: Vertex AI location (Vertex AI)
3. WHEN the user saves provider options, THE Config_Manager SHALL write them to `opencode.json` under the `provider` section
4. THE Config_Manager SHALL preserve existing provider configurations when adding new options

### Requirement 4: 环境变量导入

**User Story:** As a user, I want to import API keys from environment variables, so that I can quickly configure providers using existing credentials.

#### Acceptance Criteria

1. THE Config_Manager SHALL detect common environment variables for each provider:
   - ANTHROPIC_API_KEY for Anthropic
   - OPENAI_API_KEY for OpenAI
   - GEMINI_API_KEY or GOOGLE_API_KEY for Gemini
   - AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_PROFILE for Bedrock
   - AZURE_OPENAI_API_KEY, AZURE_RESOURCE_NAME for Azure
   - XAI_API_KEY for xAI
   - GROQ_API_KEY for Groq
   - OPENROUTER_API_KEY for OpenRouter
   - GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_CLOUD_PROJECT for Vertex AI
   - DEEPSEEK_API_KEY for DeepSeek
2. WHEN environment variables are detected, THE Config_Manager SHALL offer to import them with a single click
3. WHEN importing from environment variables, THE Config_Manager SHALL use the `{env:VARIABLE_NAME}` reference format instead of copying the actual value
4. THE Config_Manager SHALL display which environment variables are currently set in the system

### Requirement 5: 认证文件管理

**User Story:** As a user, I want to view and manage the auth.json file, so that I can see all configured credentials and remove unused ones.

#### Acceptance Criteria

1. THE Config_Manager SHALL read and parse the `~/.local/share/opencode/auth.json` file
2. WHEN the auth.json file does not exist, THE Config_Manager SHALL create it with an empty object when saving credentials
3. THE Config_Manager SHALL display a list of all configured provider credentials from auth.json
4. WHEN the user deletes a provider credential, THE Config_Manager SHALL remove it from auth.json
5. THE Config_Manager SHALL mask sensitive values (API keys) in the display, showing only the first and last 4 characters
6. IF the auth.json file is malformed, THEN THE Config_Manager SHALL display an error and offer to reset it

### Requirement 6: Provider 状态检测

**User Story:** As a user, I want to see the connection status of configured providers, so that I can verify my credentials are working.

#### Acceptance Criteria

1. THE Config_Manager SHALL provide a "测试连接" button for each configured provider
2. WHEN the user clicks test connection, THE Config_Manager SHALL attempt to validate the credentials with the provider's API
3. WHEN the connection test succeeds, THE Config_Manager SHALL display a success indicator with response time
4. IF the connection test fails, THEN THE Config_Manager SHALL display the error message from the provider
5. THE Config_Manager SHALL support testing connections for providers that have a models endpoint

### Requirement 7: 配置同步

**User Story:** As a user, I want my native provider configurations to sync with the existing provider management, so that I can use native providers alongside custom providers.

#### Acceptance Criteria

1. WHEN a native provider is configured, THE Config_Manager SHALL make it available in the model selection for Agents
2. THE Config_Manager SHALL distinguish between native providers and custom providers in the UI
3. WHEN the user configures models for a native provider, THE Config_Manager SHALL write the model configuration to the appropriate provider section in opencode.json
4. THE Config_Manager SHALL not duplicate provider configurations between native and custom provider sections

### Requirement 8: 跨平台路径支持

**User Story:** As a user on different operating systems, I want the auth.json path to be correctly resolved, so that the application works on Windows, macOS, and Linux.

#### Acceptance Criteria

1. THE Config_Manager SHALL resolve the auth.json path correctly on all platforms:
   - Windows: `%LOCALAPPDATA%\opencode\auth.json` or `~/.local/share/opencode/auth.json`
   - macOS: `~/.local/share/opencode/auth.json`
   - Linux: `~/.local/share/opencode/auth.json`
2. THE Config_Manager SHALL create the parent directory if it does not exist when saving auth.json
3. THE Config_Manager SHALL handle path separators correctly for each operating system

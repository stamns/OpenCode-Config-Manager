# Implementation Plan: Native Provider Support

## Overview

本实现计划将原生 Provider 支持功能分解为可执行的编码任务。实现顺序遵循：核心数据层 → 业务逻辑层 → UI 层的原则，确保每个任务都能独立验证。

所有代码将添加到现有的 `opencode_config_manager_fluent.py` 文件中。

## Tasks

- [x] 1. 实现 AuthManager 核心类
  - [x] 1.1 实现跨平台 auth.json 路径解析
    - 创建 `AuthManager` 类和 `_get_auth_path()` 方法
    - 支持 Windows (`%LOCALAPPDATA%/opencode`) 和 Unix (`~/.local/share/opencode`)
    - 自动创建父目录
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 1.2 实现 auth.json 读写操作
    - 创建 `read_auth()` 方法读取 auth.json
    - 创建 `write_auth()` 方法写入 auth.json
    - 处理文件不存在的情况（返回空对象）
    - 处理 JSON 解析错误
    - _Requirements: 5.1, 5.2, 5.6_

  - [x] 1.3 实现 Provider 认证 CRUD 操作
    - 创建 `get_provider_auth()` 获取单个 Provider 认证
    - 创建 `set_provider_auth()` 设置单个 Provider 认证
    - 创建 `delete_provider_auth()` 删除单个 Provider 认证
    - _Requirements: 5.3, 5.4_

  - [x] 1.4 实现 API Key 遮蔽功能
    - 创建 `mask_api_key()` 方法
    - 长度 > 8 时显示首尾 4 字符
    - 长度 <= 8 时显示 `****`
    - _Requirements: 5.5_

  - [ ]* 1.5 编写 AuthManager 属性测试
    - **Property 1: Auth Config Round-Trip**
    - **Property 4: API Key Masking**
    - **Property 6: Cross-Platform Path Resolution**
    - **Property 8: Credential Deletion Completeness**
    - **Validates: Requirements 2.3, 5.1, 5.4, 5.5, 8.1, 8.3**

- [x] 2. 实现 NativeProviderRegistry 数据定义
  - [x] 2.1 定义 NativeProviderConfig 数据类
    - 创建 `NativeProviderConfig` dataclass
    - 创建 `AuthField` dataclass
    - 创建 `OptionField` dataclass
    - _Requirements: 1.3, 2.1, 2.2_

  - [x] 2.2 定义所有支持的原生 Provider
    - 定义 Anthropic、OpenAI、Gemini 配置
    - 定义 Amazon Bedrock、Azure OpenAI 配置
    - 定义 GitHub Copilot、xAI、Groq 配置
    - 定义 OpenRouter、Vertex AI、DeepSeek、OpenCode Zen 配置
    - _Requirements: 1.3_

  - [ ]* 2.3 编写 Provider 配置属性测试
    - **Property 5: Provider Auth Field Mapping**
    - **Validates: Requirements 2.1**

- [x] 3. 实现 EnvVarDetector 环境变量检测
  - [x] 3.1 实现环境变量检测逻辑
    - 创建 `EnvVarDetector` 类
    - 创建 `PROVIDER_ENV_VARS` 映射表
    - 创建 `detect_env_vars()` 检测单个 Provider 的环境变量
    - 创建 `detect_all_env_vars()` 检测所有 Provider 的环境变量
    - _Requirements: 4.1, 4.4_

  - [x] 3.2 实现环境变量引用格式化
    - 创建 `format_env_reference()` 方法
    - 返回 `{env:VARIABLE_NAME}` 格式
    - _Requirements: 2.4, 4.3_

  - [ ]* 3.3 编写环境变量属性测试
    - **Property 3: Environment Variable Reference Format**
    - **Validates: Requirements 2.4, 4.3**

- [x] 4. Checkpoint - 核心逻辑验证
  - 确保所有测试通过，ask the user if questions arise.

- [x] 5. 实现 NativeProviderPage UI 页面
  - [x] 5.1 创建页面基础布局
    - 创建 `NativeProviderPage` 类继承 `BasePage`
    - 使用表格布局显示 Provider 列表（与 ProviderPage 风格一致）
    - 工具栏包含配置、测试、删除按钮
    - 添加到主窗口导航菜单（在 `MainWindow` 中注册）
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 5.2 实现 Provider 列表组件
    - 使用 `TableWidget` 显示所有支持的原生 Provider
    - 列：Provider 名称、SDK、状态、环境变量
    - 显示配置状态指示器（已配置/未配置，颜色区分）
    - 支持选择 Provider
    - _Requirements: 1.2, 1.4_

  - [x] 5.3 实现认证配置表单
    - 创建 `NativeProviderDialog` 对话框
    - 根据 Provider 动态生成认证字段
    - 支持 text、password、file 类型输入
    - 显示环境变量检测结果和导入按钮
    - _Requirements: 2.1, 2.2, 4.2_

  - [x] 5.4 实现 Provider 选项配置表单
    - 在对话框中根据 Provider 动态生成选项字段
    - 支持 text、select 类型输入
    - _Requirements: 3.1, 3.2_

  - [x] 5.5 实现保存和删除功能
    - 保存认证到 auth.json（调用 `AuthManager`）
    - 保存选项到 opencode.json（复用现有配置服务）
    - 删除 Provider 配置
    - _Requirements: 2.3, 3.3, 5.4_

  - [x] 5.6 实现输入验证
    - 验证必填字段
    - 验证格式（如 API Key 格式）
    - 显示验证错误信息
    - _Requirements: 2.5_

- [x] 6. 实现连接测试功能
  - [x] 6.1 实现测试连接按钮和逻辑
    - 添加"测试连接"按钮
    - 调用 Provider 的 models 端点验证凭证
    - 显示成功/失败状态和响应时间
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 7. 实现配置同步功能
  - [x] 7.1 集成到现有 Provider/Model 选择
    - 在 Agent 模型选择中显示已配置的原生 Provider
    - 区分原生 Provider 和自定义 Provider
    - _Requirements: 7.1, 7.2_

  - [x] 7.2 实现配置去重逻辑
    - 检测原生与自定义 Provider 重复
    - 提示用户处理重复配置
    - _Requirements: 7.4_

  - [ ]* 7.3 编写配置同步属性测试
    - **Property 2: Provider Options Preservation**
    - **Property 7: No Provider Duplication**
    - **Validates: Requirements 3.3, 3.4, 7.4**

- [x] 8. Final Checkpoint - 完整功能验证
  - [x] 8.1 删除旧代码（_OldNativeProviderCode 类）
  - [x] 8.2 验证语法正确性
  - [x] 8.3 验证应用程序正常启动
  - [x] 8.4 更新版本号到 1.1.6
  - [x] 8.5 更新 CHANGELOG.md

## Notes

- 所有代码添加到现有的 `opencode_config_manager_fluent.py` 文件中
- 每个任务都引用了具体的需求条款以便追溯
- Checkpoints 用于阶段性验证
- 属性测试使用 Hypothesis 库实现（标记为可选 `*`）
- UI 组件使用 QFluentWidgets 保持风格一致
- 任务标记 `*` 为可选，可跳过以加快 MVP 开发
- NativeProviderPage 使用表格布局，与 ProviderPage 风格保持一致

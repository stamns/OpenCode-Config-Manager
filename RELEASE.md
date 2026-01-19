## [v1.1.7] - 2026-01-20 02:54
**版本代号**: CLI 导出与 UI 优化版

### 🆕 CLI 工具导出功能
- **Claude Code 多模型配置**：支持 4 个模型字段 (主模型、Haiku、Sonnet、Opus) 可独立配置或留空
- **Codex/Gemini 双文件预览**：Codex (auth.json + config.toml)、Gemini (.env + settings.json) 双文件标签页预览
- **Base URL 临时修改**：每个 CLI 工具标签页可临时修改 Base URL 用于导出 不影响原始配置
- **模型自定义输入**：模型下拉框支持手动输入自定义模型名称 使用原生 QComboBox 实现
- **语法高亮与格式化**：新增 ConfigSyntaxHighlighter 类支持 JSON/TOML/ENV 格式 添加格式化按钮
- **通用配置功能**：添加"写入通用配置"复选框和"编辑通用配置"对话框
- **配置检测动画**：切换 Provider 时显示"⏳ 配置检测中..."状态

### 🎨 UI 优化
- **导航菜单字体加粗**：所有导航菜单项字体设置为 bold 提升可读性和视觉层次
- **CLI 导出页面标签页布局**：采用主标签页设计 (Claude/Codex/Gemini) 更清晰直观
- **CLI 工具状态显示**：固定尺寸 (150x100px) 居中对齐 状态文字加粗
- **配置预览框优化**：最小高度 350px 移除最大高度限制 显示更多内容
- **模型下拉框宽度**：从 200px 增加到 300px 显示更完整的模型名称

### 🔧 监控页面优化
- **启动/停止按钮切换**：默认不启动对话延迟检测 需手动点击"启动"按钮 点击后切换为"停止"

### 🐛 Bug 修复
- **模型留空处理**：选择"(留空使用默认)"时配置预览不包含占位符文本
- **删除重复样式**：Codex 和 Gemini 标签页中的重复样式定义已删除
- **外部导入功能修复**：修复外部配置导入相关问题 提升导入稳定性

### 📁 文件变更
- 更新：`opencode_config_manager_fluent.py`

---

## [v1.1.6] - 2026-01-19 12:00
**版本代号**: 原生 Provider 支持版

### 🆕 新增功能
- **原生 Provider 支持**：
  - 新增"原生 Provider"页面 管理 OpenCode 官方支持的 AI 服务提供商
  - 支持 12 个原生 Provider：Anthropic、OpenAI、Gemini、Amazon Bedrock、Azure OpenAI、GitHub Copilot、xAI、Groq、OpenRouter、Vertex AI、DeepSeek、OpenCode Zen
  - 认证信息存储在独立的 `auth.json` 文件中 与 `opencode.json` 分离
  - 跨平台路径支持：Windows (`%LOCALAPPDATA%/opencode`)、Unix (`~/.local/share/opencode`)

- **AuthManager 认证管理器**：
  - `read_auth()` / `write_auth()` - 读写 auth.json
  - `get_provider_auth()` / `set_provider_auth()` / `delete_provider_auth()` - Provider 认证 CRUD
  - `mask_api_key()` - API Key 遮蔽显示 (首尾 4 字符）

- **环境变量检测与导入**：
  - `EnvVarDetector` 类自动检测系统环境变量
  - 支持 `{env:VARIABLE_NAME}` 格式引用环境变量
  - 一键导入检测到的环境变量

- **NativeProviderPage 页面**：
  - 表格布局显示 Provider 列表 (名称、SDK、状态、环境变量）
  - 状态颜色区分：已配置 (绿色）/ 未配置 (灰色）
  - 工具栏：配置、测试连接、删除按钮
  - 双击行打开配置对话框

- **NativeProviderDialog 配置对话框**：
  - 动态生成认证字段 (支持 text、password、file 类型）
  - 动态生成选项字段 (支持 text、select 类型）
  - 深色主题适配 使用 SimpleCardWidget 卡片布局
  - 环境变量导入按钮

- **连接测试功能**：
  - 调用 Provider 的 models 端点验证凭证
  - 显示成功/失败状态和响应时间

- **配置同步与去重**：
  - 在 Agent 模型选择中显示已配置的原生 Provider
  - 检测原生与自定义 Provider 重复 提示用户处理

- **Skill 发现与浏览**：
  - 扫描所有 4 个路径：OpenCode 全局/项目、Claude 全局/项目
  - 显示已发现的 Skill 列表 包含来源标识 (🌐 全局 / 📁 项目）
  - 点击查看详情：名称、描述、许可证、兼容性、路径、内容预览
  - 支持编辑、删除、打开目录操作

- **完整的 SKILL.md 创建/编辑**：
  - 支持完整 frontmatter：name、description、license、compatibility
  - 4 种保存位置选择 (OpenCode/Claude × 全局/项目）
  - 名称验证 (1-64字符 小写字母数字+单连字符 符合官方规范）
  - 描述验证 (1-1024字符）

- **权限配置增强**：
  - 全局权限配置 (permission.skill）
  - Agent 级别权限覆盖 (agent.xxx.permission.skill）
  - 禁用 Skill 工具 (agent.xxx.tools.skill: false）

- **SkillDiscovery 类**：
  - `discover_all()` - 发现所有路径下的 Skill
  - `parse_skill_file()` - 解析 SKILL.md frontmatter
  - `validate_skill_name()` / `validate_description()` - 验证名称和描述

### 🔧 优化改进
- **Skill 页面重构**：采用 3 标签页布局 (浏览 Skill、创建 Skill、权限配置）
- **Claude 兼容路径支持**：完整支持 `.claude/skills/` 路径
- **DiscoveredSkill 数据类**：统一 Skill 信息结构

### 📁 文件变更
- 更新：`opencode_config_manager_fluent.py`
- 新增：`assets/512x512.ico` (从 PNG 转换）

### 📋 新增数据类
- `AuthField` - 认证字段定义
- `OptionField` - 选项字段定义
- `NativeProviderConfig` - 原生 Provider 配置结构
- `NATIVE_PROVIDERS` - 12 个原生 Provider 定义列表

---

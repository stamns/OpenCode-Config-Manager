# Release Notes / 发布说明

## v0.5.0 (2026-01-14)

### 重大更新

- **完善模型预设配置**
  - Claude 系列：支持 extended thinking 模式（budgetTokens、thinkingEnabled）
  - OpenAI/Codex 系列：支持 reasoningEffort 参数（high/medium/low）
  - Gemini 系列：支持 thinkingConfig 配置
  - 选择预设模型时自动填充完整配置（options、variants）

- **统一保存逻辑**
  - 所有"保存修改"按钮现在直接写入文件
  - 不再需要两步操作（先保存修改再点顶部保存）
  - 删除操作也会立即生效

- **备份恢复功能增强**
  - 首次启动时提示备份原配置
  - 支持多版本备份管理
  - 新增"恢复备份"对话框，可查看、恢复、删除备份
  - 备份文件带时间戳和标签（auto/manual/before_save）

- **全局 Tooltip 提示**
  - Provider 参数说明（名称、SDK、API地址、密钥）
  - Model 参数说明（options、variants、上下文限制）
  - Agent/Category 参数说明
  - SDK 兼容性提示（选择 SDK 时显示适用的模型系列）

- **外部导入功能重构**
  - 支持 Claude Code settings.json 和 providers.json
  - 支持 Codex config.toml
  - 支持 Gemini config.json
  - 支持 cc-switch config.json
  - 预览转换结果后再导入
  - 冲突检测和处理

### 界面改进

- Provider 列表新增 SDK 列
- 工具栏新增"恢复备份"按钮
- 保存按钮改为"保存全部"
- 各保存按钮旁添加"(直接保存到文件)"提示

### Bug 修复

- 修复 Provider 保存时创建新条目而非更新原条目的问题
- 修复权限管理保存后列表不同步的问题
- 修复 Model 删除后未保存到文件的问题

---

## v0.4.0 (2026-01-13)

### 新功能

- **全新现代化 UI 设计**
  - 采用 GitHub 风格配色方案
  - 侧边栏导航，分组显示功能模块
  - 卡片式布局，统一的视觉风格
  - 现代化圆角按钮，带悬停效果
  - 输入框聚焦高亮

- **预设模型快速选择**
  - Claude 系列：claude-opus-4-5、claude-sonnet-4-5、claude-haiku-3-5
  - GPT 系列：gpt-4o、gpt-4o-mini、gpt-4-turbo、o1-preview、o1-mini
  - Gemini 系列：gemini-2.0-flash、gemini-1.5-pro、gemini-1.5-flash
  - 其他：deepseek-chat、deepseek-coder、qwen-max

- **预设 Agent 模板**
  - oracle：架构设计、代码审查、策略规划专家
  - librarian：多仓库分析、文档查找专家
  - explore：快速代码库探索专家
  - frontend-ui-ux-engineer：UI/UX 设计专家
  - document-writer：技术文档写作专家
  - multimodal-looker：视觉内容分析专家
  - code-reviewer：代码质量审查专家
  - debugger：问题诊断、Bug 修复专家

- **预设 Category 模板**
  - visual (Temperature: 0.7)：前端、UI/UX、设计相关任务
  - business-logic (Temperature: 0.1)：后端逻辑、架构设计
  - documentation (Temperature: 0.3)：文档编写、技术写作
  - code-analysis (Temperature: 0.2)：代码审查、重构分析

- **帮助说明页面**
  - 配置优先级说明
  - 使用说明文档
  - 关于页面

### 界面改进

- 侧边栏导航替代顶部选项卡
- OpenCode 和 Oh My OpenCode 配置分组显示
- 顶部工具栏：保存、重新加载、备份
- 配置状态和修改状态实时显示
- Temperature 滑块实时数值显示

### 技术改进

- 自定义控件：ModernButton、ModernEntry、Card
- 统一配色方案和字体定义
- 代码结构优化

---

## v0.3.0 (2026-01-13)

### 新功能

- GUI 布局重构，区分 OpenCode 和 Oh My OpenCode
- 添加预设常用模型下拉选择
- 添加配置优先级说明界面
- 使用 clam 主题美化界面

---

## v0.2.0 (2026-01-13)

### 新功能

- Provider 管理：添加/编辑/删除 API 提供商
- Model 管理：添加/编辑/删除模型
- Agent 管理：配置 Oh My OpenCode Agent
- Category 管理：配置任务分类和 Temperature
- 权限管理：配置工具使用权限
- 外部导入：检测 Claude Code 配置
- 自动备份功能

---

## v0.1.0 (2026-01-13)

### 初始版本

- 基础框架搭建
- 配置文件读写
- 核心服务类实现

---

## 下载

| 平台 | 下载链接 | 大小 |
|------|---------|------|
| Windows | [OpenCodeConfigManager.exe](https://github.com/icysaintdx/OpenCode-Config-Manager/releases/download/v0.5.0/OpenCodeConfigManager.exe) | ~15 MB |
| macOS | [OpenCodeConfigManager.app.zip](https://github.com/icysaintdx/OpenCode-Config-Manager/releases/download/v0.5.0/OpenCodeConfigManager.app.zip) | ~20 MB |
| Linux | [OpenCodeConfigManager](https://github.com/icysaintdx/OpenCode-Config-Manager/releases/download/v0.5.0/OpenCodeConfigManager) | ~15 MB |

---

## 系统要求

- **Windows**: Windows 10/11
- **macOS**: macOS 10.14+
- **Linux**: Ubuntu 18.04+ / Debian 10+ / Fedora 30+

如果从源码运行，需要 Python 3.8+

---

## 安装说明

### Windows

1. 下载 `OpenCodeConfigManager.exe`
2. 双击运行即可

### macOS

1. 下载 `OpenCodeConfigManager.app.zip`
2. 解压后将 `.app` 拖入「应用程序」文件夹
3. 首次运行可能需要在「系统偏好设置 > 安全性与隐私」中允许

### Linux

1. 下载 `OpenCodeConfigManager`
2. 添加执行权限：`chmod +x OpenCodeConfigManager`
3. 运行：`./OpenCodeConfigManager`

---

## 已知问题

- macOS 首次运行可能提示「无法验证开发者」，需手动允许
- Linux 部分发行版可能需要安装 `python3-tk`

---

## 反馈

如有问题或建议，请提交 [Issue](https://github.com/icysaintdx/OpenCode-Config-Manager/issues)

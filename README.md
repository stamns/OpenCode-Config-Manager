# OpenCode Config Manager

<p align="center">
  <strong>可视化管理 OpenCode 和 Oh My OpenCode 配置文件的 GUI 工具</strong>
</p>

<p align="center">
  <a href="#功能特性">功能特性</a> •
  <a href="#安装使用">安装使用</a> •
  <a href="#配置说明">配置说明</a> •
  <a href="#构建指南">构建指南</a> •
  <a href="#许可证">许可证</a>
</p>

---

## 功能特性

### Provider 管理
- 添加/编辑/删除自定义 API 提供商
- 支持多种 SDK：`@ai-sdk/anthropic`、`@ai-sdk/openai`、`@ai-sdk/google`、`@ai-sdk/azure`
- API 密钥安全显示/隐藏
- **SDK 兼容性提示**：选择 SDK 时显示适用的模型系列

### Model 管理
- 在 Provider 下添加/管理模型
- **预设常用模型快速选择**：Claude、GPT-5、Gemini 系列
- **完整预设配置**：选择预设模型自动填充 options 和 variants
- **Options/Variants 区分**（符合 OpenCode 官方规范）：
  - **options**: 模型默认配置，每次调用都会使用
  - **variants**: 可切换变体，通过快捷键切换不同配置组合
- **Thinking 模式支持**：
  - Claude: `thinking.type`, `thinking.budgetTokens`
  - OpenAI: `reasoningEffort` (high/medium/low/xhigh)
  - Gemini: `thinkingConfig.thinkingBudget`

### MCP 服务器管理 (v0.6.0 新增)
- 配置本地和远程 MCP 服务器
- **Local 类型**：配置启动命令和环境变量
- **Remote 类型**：配置服务器 URL 和请求头
- 支持启用/禁用、超时设置

### OpenCode Agent 配置 (v0.6.0 新增)
- 配置 OpenCode 原生 Agent
- **模式设置**：primary（主Agent）/ subagent（子Agent）/ all
- **参数配置**：temperature、maxSteps、hidden、disable
- **工具权限**：配置 Agent 可用的工具
- **权限控制**：配置 edit/bash/webfetch 权限
- **预设模板**：build、plan、explore、code-reviewer 等

### Agent 管理 (Oh My OpenCode)
- 配置不同用途的 Agent
- 绑定已配置的 Provider/Model
- **预设 Agent 模板**：oracle、librarian、explore、code-reviewer 等

### Category 管理 (Oh My OpenCode)
- 配置任务分类
- Temperature 滑块调节 (0.0 - 2.0)
- **预设分类模板**：visual、business-logic、documentation、code-analysis

### 权限管理
- 配置工具使用权限：allow / ask / deny
- 常用工具快捷按钮

### 外部导入
- 自动检测多种配置文件：
  - Claude Code (settings.json, providers.json)
  - Codex (config.toml)
  - Gemini (config.json)
  - cc-switch (config.json)
- **预览转换结果**后再导入
- 冲突检测和处理

### 备份恢复
- **首次启动备份提示**
- 自动备份配置文件
- **多版本备份管理**
- 恢复备份对话框

### 其他特性
- 现代化 UI 设计，侧边栏导航
- **全局 Tooltip 提示**：解释各参数含义（鼠标悬停显示）
- **统一保存逻辑**：保存修改直接写入文件
- 配置优先级说明文档

---

## 安装使用

### 方式一：下载预编译版本

从 [Releases](https://github.com/icysaintdx/OpenCode-Config-Manager/releases) 下载对应平台的可执行文件：

| 平台 | 文件 |
|------|------|
| Windows | `OpenCodeConfigManager.exe` |
| macOS | `OpenCodeConfigManager.app` |
| Linux | `OpenCodeConfigManager` |

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/icysaintdx/OpenCode-Config-Manager.git
cd OpenCode-Config-Manager

# 运行（无需安装依赖，仅使用 Python 标准库）
python opencode_config_manager.py
```

**系统要求**：Python 3.8+

---

## 配置说明

### 配置文件位置

| 配置文件 | 路径 |
|---------|------|
| OpenCode | `~/.config/opencode/opencode.json` |
| Oh My OpenCode | `~/.config/opencode/oh-my-opencode.json` |
| 备份目录 | `~/.config/opencode/backups/` |

### 配置优先级（从高到低）

1. **远程配置 (Remote)** - 通过 `.well-known/opencode` 获取
2. **全局配置 (Global)** - `~/.config/opencode/opencode.json`
3. **自定义配置 (Custom)** - `OPENCODE_CONFIG` 环境变量指定
4. **项目配置 (Project)** - `<项目>/opencode.json`
5. **.opencode 目录** - `<项目>/.opencode/config.json`
6. **内联配置 (Inline)** - `OPENCODE_CONFIG_CONTENT` 环境变量

### Options vs Variants

根据 [OpenCode 官方文档](https://opencode.ai/docs/models/)：

- **options**: 模型的默认配置参数，每次调用都会使用
- **variants**: 可切换的变体配置，用户可通过 `variant_cycle` 快捷键切换

示例：
```json
{
  "provider": {
    "anthropic": {
      "models": {
        "claude-sonnet-4-5-20250929": {
          "options": {
            "thinking": {"type": "enabled", "budgetTokens": 16000}
          },
          "variants": {
            "high": {"thinking": {"type": "enabled", "budgetTokens": 32000}},
            "max": {"thinking": {"type": "enabled", "budgetTokens": 64000}}
          }
        }
      }
    }
  }
}
```

---

## 构建指南

### Windows

```batch
# 使用 spec 文件构建（推荐）
pyinstaller OpenCodeConfigManager.spec --noconfirm

# 或运行构建脚本
build_windows.bat
```

输出：`dist/OpenCodeConfigManager.exe`

### macOS / Linux

```bash
# 添加执行权限
chmod +x build_unix.sh

# 运行构建脚本
./build_unix.sh
```

输出：
- macOS: `dist/OpenCodeConfigManager.app`
- Linux: `dist/OpenCodeConfigManager`

---

## 项目结构

```
opencode-config-manager/
├── opencode_config_manager.py    # 主程序（单文件）
├── OpenCodeConfigManager.spec    # PyInstaller 构建配置
├── build_windows.bat             # Windows 构建脚本
├── build_unix.sh                 # macOS/Linux 构建脚本
├── README.md                     # 说明文档
├── RELEASE.md                    # 发布说明
├── LICENSE                       # 许可证
└── assets/
    ├── icon.ico                  # Windows 图标
    └── icon.png                  # 通用图标
```

---

## 相关项目

- [OpenCode](https://github.com/anomalyco/opencode) - AI 编程助手
- [Oh My OpenCode](https://github.com/code-yeongyu/oh-my-opencode) - OpenCode 增强插件

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

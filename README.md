# OpenCode Config Manager

<p align="center">
  <img src="assets/screenshot.png" alt="Screenshot" width="800">
</p>

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

### Model 管理
- 在 Provider 下添加/管理模型
- **预设常用模型快速选择**：Claude、GPT、Gemini 系列
- 配置模型参数：上下文限制、输出限制、附件支持

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
- 自动检测 Claude Code 配置
- 一键导入已有配置

### 其他特性
- 现代化 UI 设计，侧边栏导航
- 自动备份配置文件
- 配置优先级说明文档

---

## 安装使用

### 方式一：下载预编译版本

从 [Releases](https://github.com/yourname/opencode-config-manager/releases) 下载对应平台的可执行文件：

| 平台 | 文件 |
|------|------|
| Windows | `OpenCodeConfigManager.exe` |
| macOS | `OpenCodeConfigManager.app` |
| Linux | `OpenCodeConfigManager` |

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/yourname/opencode-config-manager.git
cd opencode-config-manager

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

1. **远程配置 (Remote)** - 通过 API 获取的配置
2. **全局配置 (Global)** - `~/.config/opencode/opencode.json`
3. **自定义配置 (Custom)** - `--config` 参数指定
4. **项目配置 (Project)** - `<项目>/opencode.json`
5. **.opencode 目录** - `<项目>/.opencode/config.json`
6. **内联配置 (Inline)** - 命令行参数

---

## 构建指南

### Windows

```batch
# 运行构建脚本
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

### 手动构建

```bash
# 安装 PyInstaller
pip install pyinstaller

# 构建
pyinstaller --onefile --windowed --name "OpenCodeConfigManager" opencode_config_manager.py
```

---

## 项目结构

```
opencode-config-manager/
├── opencode_config_manager.py  # 主程序（单文件）
├── build_windows.bat           # Windows 构建脚本
├── build_unix.sh               # macOS/Linux 构建脚本
├── README.md                   # 说明文档
├── RELEASE.md                  # 发布说明
├── LICENSE                     # 许可证
└── assets/
    ├── icon.ico                # Windows 图标
    ├── icon.icns               # macOS 图标
    └── screenshot.png          # 截图
```

---

## 相关项目

- [OpenCode](https://github.com/opencode-ai/opencode) - AI 编程助手
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

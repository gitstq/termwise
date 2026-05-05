<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License" />
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen.svg" alt="PRs Welcome" />
  <img src="https://img.shields.io/badge/Status-Beta-orange.svg" alt="Beta" />
</p>

<h1 align="center">🧠 TermWise</h1>

<p align="center">
  <strong>多LLM后端终端AI编码助手</strong> · Multi-LLM Terminal AI Coding Assistant
</p>

<p align="center">
  <a href="#简体中文">简体中文</a> ·
  <a href="#繁體中文">繁體中文</a> ·
  <a href="#english">English</a>
</p>

---

<a id="简体中文"></a>

# 🇨🇳 简体中文

## 🎉 项目介绍

**TermWise** 是一款专为开发者打造的**终端原生AI编码助手**，让你无需离开命令行即可获得强大的AI辅助编程体验。

### 为什么选择 TermWise？

在 AI 编程工具百花齐放的今天，大多数方案要么需要打开浏览器，要么依赖重量级的 IDE 插件。而作为终端重度用户，我们渴望一种更轻量、更高效的工作流——**TermWise 就是为这个需求而生的**。

### 核心价值

- **终端原生**：完全运行在终端中，与你的命令行工作流无缝融合，无需切换窗口
- **多模型自由切换**：不绑定单一 LLM 厂商，OpenAI、Anthropic、Ollama 随心切换，还支持 DeepSeek、通义千问等 OpenAI 兼容 API
- **Agent 能力**：不只是问答，而是能真正**读取文件、执行命令、搜索代码、写入文件**的智能代理
- **零门槛上手**：`pip install -e .` 一行命令搞定，配置简单直观

### 差异化亮点

| 特性 | TermWise | 传统 Web AI | IDE 插件 |
|------|----------|------------|---------|
| 运行环境 | 终端 | 浏览器 | IDE 内 |
| 模型选择 | 多模型自由切换 | 通常单一 | 通常单一 |
| 文件操作 | 原生支持 | 需手动复制 | 依赖 IDE |
| 资源占用 | 极低 | 中等 | 较高 |
| 本地模型 | 支持 Ollama | 通常不支持 | 部分支持 |

---

## ✨ 核心特性

### 🤖 多 LLM 后端支持
- **OpenAI**：GPT-4o、GPT-4o-mini 等全系列模型
- **Anthropic**：Claude 系列模型（Claude Sonnet 4 等）
- **Ollama**：本地部署模型（Llama 3、Qwen、DeepSeek 等），**数据不出本机**
- **OpenAI 兼容 API**：DeepSeek、通义千问、Moonshot 等国产大模型，只需配置 `base_url` 即可接入

### 🖥️ 交互式 TUI 界面
- 基于 **Textual** 框架构建的精美终端界面
- **分屏布局**：左侧对话区 + 右侧代码预览/任务计划面板
- **实时流式输出**：AI 回复逐字显示，响应体验流畅
- **快捷键丰富**：`Ctrl+N` 新对话、`Ctrl+T` 切换主题、`Ctrl+P` 任务计划、`Ctrl+C` 中断生成

### 🔄 ReAct 模式 Agent
采用业界领先的 **ReAct（Reasoning + Acting）** 范式：
1. **思考（Reasoning）**：分析用户意图，制定执行策略
2. **行动（Acting）**：调用工具执行具体操作
3. **观察（Observation）**：根据工具返回结果调整下一步行动
4. 循环往复，直到任务完成

### 🛠️ 强大的工具系统
- **📄 文件读取**：读取项目中的任意文件内容
- **✏️ 文件写入**：创建或修改文件，支持代码生成
- **🐚 Shell 命令**：执行终端命令，如 `git status`、`pytest` 等
- **🔍 代码搜索**：在项目中搜索代码片段和模式

### 📋 智能任务规划器
- 自动将复杂编码任务**分解为可执行的子步骤**
- 支持**依赖关系管理**：子任务按依赖顺序自动调度
- 实时显示**进度追踪**：直观了解任务完成情况
- 同时支持 **AI 驱动规划**和**基于规则的兜底规划**

### 💰 费用追踪
- **自动记录**每次 API 调用的 Token 用量和费用
- **按 Provider 分类统计**：清晰了解各模型的花费
- **按日汇总**：查看最近 N 天的费用趋势
- 支持 **CSV 导出**，方便进一步分析

### 🎨 主题切换
- 内置 **Dark / Light** 双主题
- 一键切换，即时生效
- 主题偏好自动保存

---

## 🚀 快速开始

### 环境要求

- **Python** >= 3.9
- **pip**（Python 包管理器）
- 至少一个 LLM API Key（OpenAI / Anthropic），或本地安装 [Ollama](https://ollama.ai)

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/gitstq/termwise.git
cd termwise

# 2. 安装依赖（开发模式，推荐）
pip install -e .

# 或者安装全部可选依赖
pip install -e ".[all]"
```

### 快速配置

```bash
# 启动配置向导
termwise config

# 或者手动设置 API Key
termwise config --set providers.openai.api_key "sk-your-key-here"
termwise config --set providers.anthropic.api_key "sk-ant-your-key-here"

# 设置默认 Provider
termwise config --set default_provider "openai"
```

### 启动使用

```bash
# 启动交互式 TUI 聊天界面
termwise chat

# 快速提问模式（无需进入 TUI）
termwise ask "用 Python 实现一个快速排序"

# 指定模型提问
termwise ask -p anthropic -m claude-sonnet-4-20250514 "解释这段代码的作用"
```

### 使用 Ollama 本地模型

```bash
# 确保 Ollama 已安装并运行
ollama serve

# 拉取模型
ollama pull llama3

# 配置 TermWise 使用 Ollama
termwise config --set default_provider "ollama"
termwise config --set providers.ollama.base_url "http://localhost:11434"
termwise config --set providers.ollama.model "llama3"

# 开始使用
termwise chat
```

### 接入 DeepSeek / 通义千问等兼容 API

```bash
# 以 DeepSeek 为例
termwise config --set default_provider "openai"
termwise config --set providers.openai.base_url "https://api.deepseek.com/v1"
termwise config --set providers.openai.api_key "your-deepseek-key"
termwise config --set providers.openai.model "deepseek-chat"

# 以通义千问为例
termwise config --set providers.openai.base_url "https://dashscope.aliyuncs.com/compatible-mode/v1"
termwise config --set providers.openai.api_key "your-qwen-key"
termwise config --set providers.openai.model "qwen-plus"
```

---

## 📖 详细使用指南

### CLI 命令详解

#### `termwise chat` — 交互式聊天

启动完整的 TUI 界面，支持多轮对话、工具调用、代码预览。

```bash
termwise chat                    # 使用默认 Provider 和模型
termwise chat -p anthropic       # 指定使用 Anthropic
termwise chat -m gpt-4o-mini     # 指定模型
```

**TUI 快捷键一览：**

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+N` | 新建对话 |
| `Ctrl+T` | 切换 Dark/Light 主题 |
| `Ctrl+P` | 显示/隐藏任务计划面板 |
| `Ctrl+C` | 中断当前生成 |
| `Ctrl+L` | 清空聊天记录 |
| `Ctrl+Q` | 退出程序 |

#### `termwise ask` — 快速提问

无需进入 TUI，直接在终端获取回答，适合脚本集成或快速查询。

```bash
termwise ask "什么是装饰器？"                          # 基本用法
termwise ask -v "解释 async/await"                    # 显示 Token 用量
termwise ask -p ollama "用 Rust 写个 hello world"     # 指定 Provider
```

#### `termwise config` — 配置管理

管理 API Key、默认模型、主题等所有配置项。

```bash
termwise config                    # 显示配置概览
termwise config --list             # 列出完整配置（YAML 格式）
termwise config --edit             # 用系统编辑器打开配置文件
termwise config --get default_provider           # 获取单个配置
termwise config --set settings.theme light       # 设置单个配置
```

**配置文件位置：** `~/.termwise/config.yaml`

#### `termwise list-models` — 查看可用模型

列出当前 Provider 下所有可用模型。

```bash
termwise list-models               # 列出默认 Provider 的模型
termwise list-models -p anthropic  # 列出指定 Provider 的模型
```

#### `termwise cost` — 费用统计

查看 API 调用的 Token 用量和费用明细。

```bash
termwise cost                      # 显示费用汇总
termwise cost -d 30                # 显示最近 30 天的费用
termwise cost -p openai            # 按 Provider 筛选
termwise cost --reset              # 重置费用记录
```

### 配置文件说明

完整的配置文件示例（`~/.termwise/config.yaml`）：

```yaml
default_provider: openai

providers:
  openai:
    api_key: "sk-your-openai-key"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"
  anthropic:
    api_key: "sk-ant-your-key"
    model: "claude-sonnet-4-20250514"
  ollama:
    base_url: "http://localhost:11434"
    model: "llama3"

settings:
  theme: dark                      # dark 或 light
  max_context_tokens: 128000       # 最大上下文 Token 数
  auto_save: true                  # 自动保存对话
  cost_tracking: true              # 启用费用追踪
```

### 典型使用场景

**场景一：代码审查**
```
> 帮我审查 src/utils.py 的代码质量，指出潜在问题
```
Agent 会自动读取文件、分析代码，并给出改进建议。

**场景二：Bug 修复**
```
> 运行测试发现 test_auth.py 失败了，帮我定位并修复
```
Agent 会读取测试文件、运行测试命令、定位问题、修改代码并验证。

**场景三：项目脚手架**
```
> 帮我创建一个 FastAPI 项目骨架，包含用户认证和数据库
```
Agent 会自动规划任务、创建目录结构、生成代码文件。

**场景四：代码解释**
```
> 解释一下这个项目的整体架构
```
Agent 会搜索和读取关键文件，给出架构分析。

---

## 💡 设计思路与迭代规划

### 设计理念

TermWise 的核心设计哲学是 **"终端优先，工具驱动"**：

1. **终端即 IDE**：我们认为终端是开发者最高效的工作环境，AI 助手应该融入其中，而非另起炉灶
2. **模型无关**：不与任何 LLM 厂商绑定，让用户自由选择最适合的模型
3. **Agent > Chat**：单纯的对话能力只是起点，真正的价值在于能**执行操作、完成任务**
4. **渐进复杂度**：简单问题快速回答，复杂任务自动规划分解

### 架构概览

```
termwise/
├── cli.py              # CLI 入口（Click）
├── config.py           # 配置管理（YAML）
├── agent/
│   ├── core.py         # Agent 核心（ReAct 循环）
│   ├── planner.py      # 任务规划器
│   └── conversation.py # 对话管理
├── providers/
│   ├── base.py         # Provider 基类
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── ollama_provider.py
│   └── registry.py     # Provider 注册中心
├── tools/
│   ├── base.py         # 工具基类
│   ├── file_reader.py  # 文件读取
│   ├── file_writer.py  # 文件写入
│   ├── shell.py        # Shell 命令
│   └── search.py       # 代码搜索
├── tui/
│   ├── app.py          # TUI 主应用
│   ├── themes.py       # 主题定义
│   └── widgets.py      # 自定义组件
└── utils/
    ├── cost_tracker.py # 费用追踪
    └── token_counter.py# Token 计数
```

### 迭代规划

- [x] 多 LLM Provider 支持（OpenAI / Anthropic / Ollama）
- [x] ReAct Agent 模式
- [x] 文件读写 / Shell / 搜索工具
- [x] TUI 交互界面
- [x] 费用追踪系统
- [x] 任务规划器
- [ ] **多模态支持**：图片理解与生成
- [ ] **对话持久化**：保存和恢复历史对话
- [ ] **插件系统**：支持用户自定义工具
- [ ] **MCP 协议支持**：接入 Model Context Protocol 生态
- [ ] **团队协作**：共享配置和对话模板
- [ ] **更多 Provider**：Google Gemini、Mistral 等

---

## 📦 打包与部署指南

### 本地开发安装

```bash
# 克隆项目
git clone https://github.com/gitstq/termwise.git
cd termwise

# 创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### 构建分发包

```bash
# 安装构建工具
pip install build

# 构建 sdist 和 wheel
python -m build

# 构建产物位于 dist/ 目录
ls dist/
# termwise-1.0.0-py3-none-any.whl
# termwise-1.0.0.tar.gz
```

### 安装到系统

```bash
# 从 PyPI 安装（发布后）
pip install termwise

# 从本地 wheel 安装
pip install dist/termwise-1.0.0-py3-none-any.whl

# 从源码安装
pip install .
```

### 作为库引入

TermWise 也可以作为 Python 库在其他项目中使用：

```python
from termwise.config import ConfigManager
from termwise.providers.registry import ProviderRegistry
from termwise.agent.core import AgentCore
from termwise.tools.file_reader import FileReaderTool
from termwise.tools.shell import ShellTool

# 初始化配置
config = ConfigManager()

# 获取 LLM Provider
registry = ProviderRegistry(config)
provider = registry.get_provider("openai")

# 创建 Agent
agent = AgentCore(
    provider=provider,
    tools=[FileReaderTool(), ShellTool()],
)

# 使用 Agent
import asyncio
response = asyncio.run(agent.chat("读取当前目录的文件列表"))
print(response)
```

### Docker 部署（可选）

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

# 挂载配置目录
VOLUME /root/.termwise

ENTRYPOINT ["termwise"]
CMD ["chat"]
```

```bash
docker build -t termwise .
docker run -it -v ~/.termwise:/root/.termwise termwise chat
```

---

## 🤝 贡献指南

我们欢迎并感谢所有形式的贡献！无论是提交 Bug、改进文档，还是贡献代码。

### 贡献流程

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m "feat: add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

### 开发环境

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行测试（含覆盖率）
pytest --cov=termwise

# 代码格式检查
ruff check .

# 类型检查
mypy termwise
```

### 提交规范

我们遵循 **Conventional Commits** 规范：

- `feat:` 新功能
- `fix:` Bug 修复
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具链相关

### 行为准则

- 尊重所有贡献者
- 保持友好和建设性的沟通
- 关注代码质量和可维护性
- 编写充分的测试用例

---

## 📄 开源协议

本项目基于 **[MIT License](LICENSE)** 开源。

```
MIT License

Copyright (c) 2024 gitstq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

<a id="繁體中文"></a>

# 🇹🇼 繁體中文

## 🎉 專案介紹

**TermWise** 是一款專為開發者打造的**終端原生 AI 編碼助手**，讓你無需離開命令列即可獲得強大的 AI 輔助程式設計體驗。

### 為什麼選擇 TermWise？

在 AI 程式設計工具百花齊放的今天，大多數方案要麼需要打開瀏覽器，要麼依賴重量級的 IDE 外掛。而作為終端重度使用者，我們渴望一種更輕量、更高效率的工作流程——**TermWise 就是為這個需求而生的**。

### 核心價值

- **終端原生**：完全運行在終端中，與你的命令列工作流程無縫融合，無需切換視窗
- **多模型自由切換**：不綁定單一 LLM 廠商，OpenAI、Anthropic、Ollama 隨心切換，還支援 DeepSeek、通義千問等 OpenAI 相容 API
- **Agent 能力**：不只是問答，而是能真正**讀取檔案、執行命令、搜尋程式碼、寫入檔案**的智慧代理
- **零門檻上手**：`pip install -e .` 一行命令搞定，配置簡單直觀

### 差異化亮點

| 特性 | TermWise | 傳統 Web AI | IDE 外掛 |
|------|----------|------------|---------|
| 運行環境 | 終端 | 瀏覽器 | IDE 內 |
| 模型選擇 | 多模型自由切換 | 通常單一 | 通常單一 |
| 檔案操作 | 原生支援 | 需手動複製 | 依賴 IDE |
| 資源佔用 | 極低 | 中等 | 較高 |
| 本地模型 | 支援 Ollama | 通常不支援 | 部分支援 |

---

## ✨ 核心特性

### 🤖 多 LLM 後端支援
- **OpenAI**：GPT-4o、GPT-4o-mini 等全系列模型
- **Anthropic**：Claude 系列模型（Claude Sonnet 4 等）
- **Ollama**：本地部署模型（Llama 3、Qwen、DeepSeek 等），**資料不出本機**
- **OpenAI 相容 API**：DeepSeek、通義千問、Moonshot 等國產大模型，只需配置 `base_url` 即可接入

### 🖥️ 互動式 TUI 介面
- 基於 **Textual** 框架構建的精美終端介面
- **分屏佈局**：左側對話區 + 右側程式碼預覽/任務計畫面板
- **即時串流輸出**：AI 回覆逐字顯示，回應體驗流暢
- **快捷鍵豐富**：`Ctrl+N` 新對話、`Ctrl+T` 切換主題、`Ctrl+P` 任務計畫、`Ctrl+C` 中斷生成

### 🔄 ReAct 模式 Agent
採用業界領先的 **ReAct（Reasoning + Acting）** 範式：
1. **思考（Reasoning）**：分析使用者意圖，制定執行策略
2. **行動（Acting）**：呼叫工具執行具體操作
3. **觀察（Observation）**：根據工具回傳結果調整下一步行動
4. 循環往復，直到任務完成

### 🛠️ 強大的工具系統
- **📄 檔案讀取**：讀取專案中的任意檔案內容
- **✏️ 檔案寫入**：建立或修改檔案，支援程式碼生成
- **🐚 Shell 命令**：執行終端命令，如 `git status`、`pytest` 等
- **🔍 程式碼搜尋**：在專案中搜尋程式碼片段和模式

### 📋 智慧任務規劃器
- 自動將複雜編碼任務**分解為可執行的子步驟**
- 支援**依賴關係管理**：子任務按依賴順序自動排程
- 即時顯示**進度追蹤**：直觀了解任務完成情況
- 同時支援 **AI 驅動規劃**和**基於規則的兜底規劃**

### 💰 費用追蹤
- **自動記錄**每次 API 呼叫的 Token 用量和費用
- **按 Provider 分類統計**：清晰了解各模型的花費
- **按日彙總**：查看最近 N 天的費用趨勢
- 支援 **CSV 匯出**，方便進一步分析

### 🎨 主題切換
- 內建 **Dark / Light** 雙主題
- 一鍵切換，即時生效
- 主題偏好自動儲存

---

## 🚀 快速開始

### 環境要求

- **Python** >= 3.9
- **pip**（Python 套件管理器）
- 至少一個 LLM API Key（OpenAI / Anthropic），或本地安裝 [Ollama](https://ollama.ai)

### 安裝步驟

```bash
# 1. 複製專案
git clone https://github.com/gitstq/termwise.git
cd termwise

# 2. 安裝依賴（開發模式，推薦）
pip install -e .

# 或者安裝全部可選依賴
pip install -e ".[all]"
```

### 快速配置

```bash
# 啟動配置精靈
termwise config

# 或者手動設定 API Key
termwise config --set providers.openai.api_key "sk-your-key-here"
termwise config --set providers.anthropic.api_key "sk-ant-your-key-here"

# 設定預設 Provider
termwise config --set default_provider "openai"
```

### 啟動使用

```bash
# 啟動互動式 TUI 聊天介面
termwise chat

# 快速提問模式（無需進入 TUI）
termwise ask "用 Python 實作一個快速排序"

# 指定模型提問
termwise ask -p anthropic -m claude-sonnet-4-20250514 "解釋這段程式碼的作用"
```

### 使用 Ollama 本地模型

```bash
# 確保 Ollama 已安裝並運行
ollama serve

# 拉取模型
ollama pull llama3

# 配置 TermWise 使用 Ollama
termwise config --set default_provider "ollama"
termwise config --set providers.ollama.base_url "http://localhost:11434"
termwise config --set providers.ollama.model "llama3"

# 開始使用
termwise chat
```

### 接入 DeepSeek / 通義千問等相容 API

```bash
# 以 DeepSeek 為例
termwise config --set default_provider "openai"
termwise config --set providers.openai.base_url "https://api.deepseek.com/v1"
termwise config --set providers.openai.api_key "your-deepseek-key"
termwise config --set providers.openai.model "deepseek-chat"

# 以通義千問為例
termwise config --set providers.openai.base_url "https://dashscope.aliyuncs.com/compatible-mode/v1"
termwise config --set providers.openai.api_key "your-qwen-key"
termwise config --set providers.openai.model "qwen-plus"
```

---

## 📖 詳細使用指南

### CLI 命令詳解

#### `termwise chat` — 互動式聊天

啟動完整的 TUI 介面，支援多輪對話、工具呼叫、程式碼預覽。

```bash
termwise chat                    # 使用預設 Provider 和模型
termwise chat -p anthropic       # 指定使用 Anthropic
termwise chat -m gpt-4o-mini     # 指定模型
```

**TUI 快捷鍵一覽：**

| 快捷鍵 | 功能 |
|--------|------|
| `Ctrl+N` | 新建對話 |
| `Ctrl+T` | 切換 Dark/Light 主題 |
| `Ctrl+P` | 顯示/隱藏任務計畫面板 |
| `Ctrl+C` | 中斷當前生成 |
| `Ctrl+L` | 清空聊天記錄 |
| `Ctrl+Q` | 結束程式 |

#### `termwise ask` — 快速提問

無需進入 TUI，直接在終端獲得回答，適合腳本整合或快速查詢。

```bash
termwise ask "什麼是裝飾器？"                          # 基本用法
termwise ask -v "解釋 async/await"                     # 顯示 Token 用量
termwise ask -p ollama "用 Rust 寫個 hello world"      # 指定 Provider
```

#### `termwise config` — 配置管理

管理 API Key、預設模型、主題等所有配置項。

```bash
termwise config                    # 顯示配置概覽
termwise config --list             # 列出完整配置（YAML 格式）
termwise config --edit             # 用系統編輯器開啟配置檔案
termwise config --get default_provider           # 取得單個配置
termwise config --set settings.theme light       # 設定單個配置
```

**配置檔案位置：** `~/.termwise/config.yaml`

#### `termwise list-models` — 查看可用模型

列出當前 Provider 下所有可用模型。

```bash
termwise list-models               # 列出預設 Provider 的模型
termwise list-models -p anthropic  # 列出指定 Provider 的模型
```

#### `termwise cost` — 費用統計

查看 API 呼叫的 Token 用量和費用明細。

```bash
termwise cost                      # 顯示費用彙總
termwise cost -d 30                # 顯示最近 30 天的費用
termwise cost -p openai            # 按 Provider 篩選
termwise cost --reset              # 重置費用記錄
```

### 配置檔案說明

完整的配置檔案範例（`~/.termwise/config.yaml`）：

```yaml
default_provider: openai

providers:
  openai:
    api_key: "sk-your-openai-key"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"
  anthropic:
    api_key: "sk-ant-your-key"
    model: "claude-sonnet-4-20250514"
  ollama:
    base_url: "http://localhost:11434"
    model: "llama3"

settings:
  theme: dark                      # dark 或 light
  max_context_tokens: 128000       # 最大上下文 Token 數
  auto_save: true                  # 自動儲存對話
  cost_tracking: true              # 啟用費用追蹤
```

### 典型使用場景

**場景一：程式碼審查**
```
> 幫我審查 src/utils.py 的程式碼品質，指出潛在問題
```
Agent 會自動讀取檔案、分析程式碼，並給出改進建議。

**場景二：Bug 修復**
```
> 執行測試發現 test_auth.py 失敗了，幫我定位並修復
```
Agent 會讀取測試檔案、執行測試命令、定位問題、修改程式碼並驗證。

**場景三：專案腳手架**
```
> 幫我建立一個 FastAPI 專案骨架，包含使用者認證和資料庫
```
Agent 會自動規劃任務、建立目錄結構、生成程式碼檔案。

**場景四：程式碼解釋**
```
> 解釋一下這個專案的整體架構
```
Agent 會搜尋和讀取關鍵檔案，給出架構分析。

---

## 💡 設計思路與迭代規劃

### 設計理念

TermWise 的核心設計哲學是 **「終端優先，工具驅動」**：

1. **終端即 IDE**：我們認為終端是開發者最高效的工作環境，AI 助手應該融入其中，而非另起爐灶
2. **模型無關**：不與任何 LLM 廠商綁定，讓使用者自由選擇最適合的模型
3. **Agent > Chat**：單純的對話能力只是起點，真正的價值在於能**執行操作、完成任務**
4. **漸進複雜度**：簡單問題快速回答，複雜任務自動規劃分解

### 架構概覽

```
termwise/
├── cli.py              # CLI 入口（Click）
├── config.py           # 配置管理（YAML）
├── agent/
│   ├── core.py         # Agent 核心（ReAct 迴圈）
│   ├── planner.py      # 任務規劃器
│   └── conversation.py # 對話管理
├── providers/
│   ├── base.py         # Provider 基類
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── ollama_provider.py
│   └── registry.py     # Provider 註冊中心
├── tools/
│   ├── base.py         # 工具基類
│   ├── file_reader.py  # 檔案讀取
│   ├── file_writer.py  # 檔案寫入
│   ├── shell.py        # Shell 命令
│   └── search.py       # 程式碼搜尋
├── tui/
│   ├── app.py          # TUI 主應用
│   ├── themes.py       # 主題定義
│   └── widgets.py      # 自訂元件
└── utils/
    ├── cost_tracker.py # 費用追蹤
    └── token_counter.py# Token 計數
```

### 迭代規劃

- [x] 多 LLM Provider 支援（OpenAI / Anthropic / Ollama）
- [x] ReAct Agent 模式
- [x] 檔案讀寫 / Shell / 搜尋工具
- [x] TUI 互動介面
- [x] 費用追蹤系統
- [x] 任務規劃器
- [ ] **多模態支援**：圖片理解與生成
- [ ] **對話持久化**：儲存和恢復歷史對話
- [ ] **外掛系統**：支援使用者自訂工具
- [ ] **MCP 協議支援**：接入 Model Context Protocol 生態
- [ ] **團隊協作**：共享配置和對話範本
- [ ] **更多 Provider**：Google Gemini、Mistral 等

---

## 📦 打包與部署指南

### 本地開發安裝

```bash
# 複製專案
git clone https://github.com/gitstq/termwise.git
cd termwise

# 建立虛擬環境（推薦）
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安裝開發依賴
pip install -e ".[dev]"
```

### 建構分發包

```bash
# 安裝建構工具
pip install build

# 建構 sdist 和 wheel
python -m build

# 建構產物位於 dist/ 目錄
ls dist/
# termwise-1.0.0-py3-none-any.whl
# termwise-1.0.0.tar.gz
```

### 安裝到系統

```bash
# 從 PyPI 安裝（發布後）
pip install termwise

# 從本地 wheel 安裝
pip install dist/termwise-1.0.0-py3-none-any.whl

# 從原始碼安裝
pip install .
```

### 作為函式庫引入

TermWise 也可以作為 Python 函式庫在其他專案中使用：

```python
from termwise.config import ConfigManager
from termwise.providers.registry import ProviderRegistry
from termwise.agent.core import AgentCore
from termwise.tools.file_reader import FileReaderTool
from termwise.tools.shell import ShellTool

# 初始化配置
config = ConfigManager()

# 取得 LLM Provider
registry = ProviderRegistry(config)
provider = registry.get_provider("openai")

# 建立 Agent
agent = AgentCore(
    provider=provider,
    tools=[FileReaderTool(), ShellTool()],
)

# 使用 Agent
import asyncio
response = asyncio.run(agent.chat("讀取目前目錄的檔案列表"))
print(response)
```

### Docker 部署（可選）

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

# 掛載配置目錄
VOLUME /root/.termwise

ENTRYPOINT ["termwise"]
CMD ["chat"]
```

```bash
docker build -t termwise .
docker run -it -v ~/.termwise:/root/.termwise termwise chat
```

---

## 🤝 貢獻指南

我們歡迎並感謝所有形式的貢獻！無論是提交 Bug、改進文件，還是貢獻程式碼。

### 貢獻流程

1. **Fork** 本儲存庫
2. 建立特性分支：`git checkout -b feature/your-feature`
3. 提交變更：`git commit -m "feat: add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 **Pull Request**

### 開發環境

```bash
# 安裝開發依賴
pip install -e ".[dev]"

# 執行測試
pytest

# 執行測試（含覆蓋率）
pytest --cov=termwise

# 程式碼格式檢查
ruff check .

# 類型檢查
mypy termwise
```

### 提交規範

我們遵循 **Conventional Commits** 規範：

- `feat:` 新功能
- `fix:` Bug 修復
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建構/工具鏈相關

### 行為準則

- 尊重所有貢獻者
- 保持友善和建設性的溝通
- 關注程式碼品質和可維護性
- 編寫充分的測試用例

---

## 📄 開源協議

本專案基於 **[MIT License](LICENSE)** 開源。

```
MIT License

Copyright (c) 2024 gitstq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

<a id="english"></a>

# 🇬🇧 English

## 🎉 Introduction

**TermWise** is a **terminal-native AI coding assistant** built for developers who want powerful AI-assisted programming without ever leaving the command line.

### Why TermWise?

In today's landscape of AI coding tools, most solutions require opening a browser or installing heavyweight IDE plugins. As terminal power users, we wanted something lighter and more efficient -- **TermWise was born from that need**.

### Core Value Proposition

- **Terminal-Native**: Runs entirely in your terminal, seamlessly integrating with your existing CLI workflow -- no window switching required
- **Multi-Model Freedom**: Not locked into a single LLM vendor. Switch freely between OpenAI, Anthropic, and Ollama, with support for DeepSeek, Qwen, and other OpenAI-compatible APIs
- **True Agent Capabilities**: Beyond simple Q&A -- it can **read files, execute commands, search codebases, and write files** autonomously
- **Zero-Friction Setup**: Get started with a single `pip install -e .` command. Configuration is simple and intuitive

### What Sets Us Apart

| Feature | TermWise | Web-based AI | IDE Plugins |
|---------|----------|-------------|-------------|
| Runtime | Terminal | Browser | Inside IDE |
| Model Choice | Multi-model switching | Usually single | Usually single |
| File Operations | Native support | Manual copy-paste | IDE-dependent |
| Resource Usage | Minimal | Moderate | Heavy |
| Local Models | Ollama support | Usually no | Partial |

---

## ✨ Key Features

### 🤖 Multi-LLM Backend Support
- **OpenAI**: Full model lineup including GPT-4o, GPT-4o-mini
- **Anthropic**: Claude family models (Claude Sonnet 4, etc.)
- **Ollama**: Locally deployed models (Llama 3, Qwen, DeepSeek, etc.) -- **your data stays on your machine**
- **OpenAI-Compatible APIs**: DeepSeek, Qwen, Moonshot, and other LLMs -- just configure a `base_url` to connect

### 🖥️ Interactive TUI Interface
- Beautiful terminal UI built with the **Textual** framework
- **Split-screen layout**: Chat panel on the left + Code preview / Task plan panel on the right
- **Real-time streaming output**: AI responses appear character by character for a smooth experience
- **Rich keyboard shortcuts**: `Ctrl+N` New chat, `Ctrl+T` Toggle theme, `Ctrl+P` Task plan, `Ctrl+C` Cancel generation

### 🔄 ReAct-Mode Agent
Powered by the industry-leading **ReAct (Reasoning + Acting)** paradigm:
1. **Reasoning**: Analyzes user intent and formulates an execution strategy
2. **Acting**: Invokes tools to perform specific operations
3. **Observation**: Adjusts the next action based on tool results
4. Loops until the task is complete

### 🛠️ Powerful Tool System
- **📄 File Reader**: Read the contents of any file in your project
- **✏️ File Writer**: Create or modify files with generated code
- **🐚 Shell Execution**: Run terminal commands like `git status`, `pytest`, etc.
- **🔍 Code Search**: Search for code patterns and snippets across your project

### 📋 Smart Task Planner
- Automatically **decomposes complex coding tasks into executable sub-steps**
- **Dependency management**: Sub-tasks are automatically scheduled based on their dependencies
- **Real-time progress tracking**: Visually monitor task completion status
- Supports both **AI-driven planning** and **rule-based fallback planning**

### 💰 Cost Tracking
- **Automatically records** token usage and cost for every API call
- **Breakdown by Provider**: Clear visibility into spending per model
- **Daily aggregation**: View cost trends over the past N days
- **CSV export** for further analysis

### 🎨 Theme Switching
- Built-in **Dark / Light** themes
- One-key toggle with instant effect
- Theme preference is automatically saved

---

## 🚀 Quick Start

### Prerequisites

- **Python** >= 3.9
- **pip** (Python package manager)
- At least one LLM API key (OpenAI / Anthropic), or a local [Ollama](https://ollama.ai) installation

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/gitstq/termwise.git
cd termwise

# 2. Install dependencies (editable mode, recommended)
pip install -e .

# Or install all optional dependencies
pip install -e ".[all]"
```

### Quick Configuration

```bash
# Launch the configuration wizard
termwise config

# Or set API keys manually
termwise config --set providers.openai.api_key "sk-your-key-here"
termwise config --set providers.anthropic.api_key "sk-ant-your-key-here"

# Set the default provider
termwise config --set default_provider "openai"
```

### Up and Running

```bash
# Start the interactive TUI chat interface
termwise chat

# Quick ask mode (no TUI needed)
termwise ask "implement quicksort in Python"

# Ask with a specific model
termwise ask -p anthropic -m claude-sonnet-4-20250514 "explain what this code does"
```

### Using Ollama with Local Models

```bash
# Make sure Ollama is installed and running
ollama serve

# Pull a model
ollama pull llama3

# Configure TermWise to use Ollama
termwise config --set default_provider "ollama"
termwise config --set providers.ollama.base_url "http://localhost:11434"
termwise config --set providers.ollama.model "llama3"

# Start using it
termwise chat
```

### Connecting DeepSeek / Qwen and Other Compatible APIs

```bash
# Example: DeepSeek
termwise config --set default_provider "openai"
termwise config --set providers.openai.base_url "https://api.deepseek.com/v1"
termwise config --set providers.openai.api_key "your-deepseek-key"
termwise config --set providers.openai.model "deepseek-chat"

# Example: Qwen (Tongyi Qianwen)
termwise config --set providers.openai.base_url "https://dashscope.aliyuncs.com/compatible-mode/v1"
termwise config --set providers.openai.api_key "your-qwen-key"
termwise config --set providers.openai.model "qwen-plus"
```

---

## 📖 Detailed Usage Guide

### CLI Commands Reference

#### `termwise chat` -- Interactive Chat

Launches the full TUI interface with multi-turn conversations, tool calls, and code preview.

```bash
termwise chat                    # Use default provider and model
termwise chat -p anthropic       # Use Anthropic
termwise chat -m gpt-4o-mini     # Specify a model
```

**TUI Keyboard Shortcuts:**

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New conversation |
| `Ctrl+T` | Toggle Dark/Light theme |
| `Ctrl+P` | Show/hide task plan panel |
| `Ctrl+C` | Cancel current generation |
| `Ctrl+L` | Clear chat history |
| `Ctrl+Q` | Quit |

#### `termwise ask` -- Quick Ask

Get answers directly in the terminal without entering the TUI. Ideal for scripting or quick queries.

```bash
termwise ask "what is a decorator?"                          # Basic usage
termwise ask -v "explain async/await"                        # Show token usage
termwise ask -p ollama "write hello world in Rust"           # Specify provider
```

#### `termwise config` -- Configuration Management

Manage API keys, default models, themes, and all other settings.

```bash
termwise config                    # Show configuration overview
termwise config --list             # List full configuration (YAML format)
termwise config --edit             # Open config file in system editor
termwise config --get default_provider           # Get a single setting
termwise config --set settings.theme light       # Set a single setting
```

**Config file location:** `~/.termwise/config.yaml`

#### `termwise list-models` -- List Available Models

Lists all available models for the current provider.

```bash
termwise list-models               # List models for default provider
termwise list-models -p anthropic  # List models for a specific provider
```

#### `termwise cost` -- Cost Statistics

View token usage and cost details for API calls.

```bash
termwise cost                      # Show cost summary
termwise cost -d 30                # Show costs for the last 30 days
termwise cost -p openai            # Filter by provider
termwise cost --reset              # Reset cost history
```

### Configuration File Reference

Full configuration file example (`~/.termwise/config.yaml`):

```yaml
default_provider: openai

providers:
  openai:
    api_key: "sk-your-openai-key"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o"
  anthropic:
    api_key: "sk-ant-your-key"
    model: "claude-sonnet-4-20250514"
  ollama:
    base_url: "http://localhost:11434"
    model: "llama3"

settings:
  theme: dark                      # dark or light
  max_context_tokens: 128000       # Maximum context token count
  auto_save: true                  # Auto-save conversations
  cost_tracking: true              # Enable cost tracking
```

### Common Use Cases

**Use Case 1: Code Review**
```
> Review the code quality of src/utils.py and point out potential issues
```
The agent will automatically read the file, analyze the code, and provide improvement suggestions.

**Use Case 2: Bug Fixing**
```
> Tests are failing in test_auth.py, help me locate and fix the issue
```
The agent will read the test file, run the tests, identify the problem, fix the code, and verify.

**Use Case 3: Project Scaffolding**
```
> Create a FastAPI project skeleton with user authentication and database
```
The agent will plan the task, create the directory structure, and generate code files.

**Use Case 4: Code Explanation**
```
> Explain the overall architecture of this project
```
The agent will search and read key files, then provide an architecture analysis.

---

## 💡 Design Philosophy & Roadmap

### Design Philosophy

TermWise's core design philosophy is **"Terminal-First, Tool-Driven"**:

1. **Terminal as IDE**: We believe the terminal is the developer's most productive environment. AI assistants should blend into it, not create a separate experience
2. **Model Agnostic**: Not tied to any LLM vendor. Users should freely choose the model that best fits their needs
3. **Agent > Chat**: Conversational ability is just the starting point. The real value lies in **taking actions and completing tasks**
4. **Progressive Complexity**: Quick answers for simple questions; automatic task decomposition for complex ones

### Architecture Overview

```
termwise/
├── cli.py              # CLI entry point (Click)
├── config.py           # Configuration management (YAML)
├── agent/
│   ├── core.py         # Agent core (ReAct loop)
│   ├── planner.py      # Task planner
│   └── conversation.py # Conversation management
├── providers/
│   ├── base.py         # Provider base class
│   ├── openai_provider.py
│   ├── anthropic_provider.py
│   ├── ollama_provider.py
│   └── registry.py     # Provider registry
├── tools/
│   ├── base.py         # Tool base class
│   ├── file_reader.py  # File reading
│   ├── file_writer.py  # File writing
│   ├── shell.py        # Shell execution
│   └── search.py       # Code search
├── tui/
│   ├── app.py          # TUI main application
│   ├── themes.py       # Theme definitions
│   └── widgets.py      # Custom widgets
└── utils/
    ├── cost_tracker.py # Cost tracking
    └── token_counter.py# Token counting
```

### Roadmap

- [x] Multi-LLM Provider support (OpenAI / Anthropic / Ollama)
- [x] ReAct Agent mode
- [x] File read/write / Shell / Search tools
- [x] TUI interactive interface
- [x] Cost tracking system
- [x] Task planner
- [ ] **Multimodal Support**: Image understanding and generation
- [ ] **Conversation Persistence**: Save and restore chat history
- [ ] **Plugin System**: Support user-defined tools
- [ ] **MCP Protocol Support**: Connect to the Model Context Protocol ecosystem
- [ ] **Team Collaboration**: Shared configurations and conversation templates
- [ ] **More Providers**: Google Gemini, Mistral, and more

---

## 📦 Packaging & Deployment Guide

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/gitstq/termwise.git
cd termwise

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install development dependencies
pip install -e ".[dev]"
```

### Building Distribution Packages

```bash
# Install build tools
pip install build

# Build sdist and wheel
python -m build

# Build artifacts are in the dist/ directory
ls dist/
# termwise-1.0.0-py3-none-any.whl
# termwise-1.0.0.tar.gz
```

### System Installation

```bash
# Install from PyPI (after publishing)
pip install termwise

# Install from local wheel
pip install dist/termwise-1.0.0-py3-none-any.whl

# Install from source
pip install .
```

### Using as a Library

TermWise can also be used as a Python library in other projects:

```python
from termwise.config import ConfigManager
from termwise.providers.registry import ProviderRegistry
from termwise.agent.core import AgentCore
from termwise.tools.file_reader import FileReaderTool
from termwise.tools.shell import ShellTool

# Initialize configuration
config = ConfigManager()

# Get an LLM provider
registry = ProviderRegistry(config)
provider = registry.get_provider("openai")

# Create an agent
agent = AgentCore(
    provider=provider,
    tools=[FileReaderTool(), ShellTool()],
)

# Use the agent
import asyncio
response = asyncio.run(agent.chat("list files in the current directory"))
print(response)
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

# Mount configuration directory
VOLUME /root/.termwise

ENTRYPOINT ["termwise"]
CMD ["chat"]
```

```bash
docker build -t termwise .
docker run -it -v ~/.termwise:/root/.termwise termwise chat
```

---

## 🤝 Contributing

We welcome and appreciate contributions of all kinds -- whether it's filing bugs, improving documentation, or contributing code.

### How to Contribute

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Submit a **Pull Request**

### Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=termwise

# Lint check
ruff check .

# Type check
mypy termwise
```

### Commit Convention

We follow the **Conventional Commits** specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test-related changes
- `chore:` Build/tooling changes

### Code of Conduct

- Respect all contributors
- Maintain friendly and constructive communication
- Focus on code quality and maintainability
- Write thorough test cases

---

## 📄 License

This project is licensed under the **[MIT License](LICENSE)**.

```
MIT License

Copyright (c) 2024 gitstq

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

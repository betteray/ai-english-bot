# 英语学习机器人 (AI English Bot)

一个基于 Telegram 的智能英语单词学习机器人，支持多单词表选择、自动发送、翻译缓存等功能。

## 📋 功能特性

### 🎯 核心功能
- **随机单词学习**：从选择的单词表中随机推送英语单词
- **即时翻译**：点击按钮即可获取单词的中文翻译
- **多单词表支持**：用户可以自由选择不同的单词表进行学习
- **自动发送**：可设置自动定时发送单词，支持随机间隔
- **学习统计**：详细的学习进度和统计信息

### 🗂️ 单词表管理
- **动态发现**：自动扫描 `data/wordlists/` 目录下的单词表文件
- **用户选择**：每个用户可以独立选择自己的单词表
- **实时切换**：无需重启即可切换单词表
- **扩展性强**：添加新单词表文件即可自动识别

### 📊 数据管理
- **用户管理**：自动记录用户信息和活跃状态
- **学习历史**：保存每个用户的单词学习记录
- **翻译缓存**：智能缓存翻译结果，提高响应速度
- **统计分析**：提供详细的学习数据统计

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Telegram Bot Token
- Ollama (用于翻译功能)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境

1. **设置 Telegram Bot Token**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   ```

2. **确保 Ollama 运行**
   ```bash
   # 启动 Ollama 服务
   ollama serve
   
   # 下载翻译模型
   ollama pull qwen2.5:7b
   ```

### 启动机器人

```bash
# 使用新架构（推荐）
python app.py
```

## 📖 使用指南

### 基础命令

| 命令 | 功能 | 描述 |
|------|------|------|
| `/start` | 启动机器人 | 显示欢迎信息和当前状态 |
| `/word` | 获取随机单词 | 从当前选择的单词表中获取随机单词 |
| `/wordlist` | 选择单词表 | 显示所有可用单词表供选择 |
| `/stats` | 查看统计 | 显示个人学习统计信息 |
| `/auto_start` | 开启自动发送 | 开启定时自动发送单词功能 |
| `/auto_stop` | 关闭自动发送 | 关闭自动发送功能 |

### 使用流程

1. **启动机器人**：发送 `/start` 命令
2. **选择单词表**：发送 `/wordlist` 选择适合的单词表
3. **开始学习**：发送 `/word` 获取随机单词
4. **翻译单词**：点击 "🔤 翻译" 按钮查看中文含义
5. **查看进度**：发送 `/stats` 查看学习统计

## 📁 项目结构

```
ai-english-bot/
├── app.py                    # 主程序入口
├── admin.py                  # 管理工具
├── requirements.txt          # 依赖包列表
├── README.md                 # 项目说明
├── english_bot.db            # SQLite 数据库
├── data/                     # 数据目录
│   └── wordlists/           # 单词表文件
│       ├── 4000_Essential_English_Words_Book_2nd_Edition.1.txt
│       ├── 4000_Essential_English_Words_Book_2nd_Edition.2.txt
│       ├── 4000_Essential_English_Words_Book_2nd_Edition.3.txt
│       ├── 4000_Essential_English_Words_Book_2nd_Edition.4.txt
│       ├── 4000_Essential_English_Words_Book_2nd_Edition.5.txt
│       └── 4000_Essential_English_Words_Book_2nd_Edition.6.txt
├── logs/                     # 日志文件目录
│   ├── telegram_bot.log     # 运行日志
│   └── error.log            # 错误日志
└── src/                      # 源代码目录
    └── bot/                 # 机器人核心模块
        ├── telegram_bot.py  # 机器人主类
        ├── handlers/        # 处理器模块
        │   ├── commands.py  # 命令处理器
        │   └── callbacks.py # 回调处理器
        ├── services/        # 服务层
        │   ├── word_manager.py    # 单词管理
        │   ├── word_service.py    # 单词服务
        │   ├── translation.py     # 翻译服务
        │   └── scheduler.py       # 调度服务
        ├── models/          # 数据模型
        │   └── database.py  # 数据库管理
        └── utils/           # 工具模块
            ├── config.py    # 配置管理
            └── logger.py    # 日志配置
```

## 🔧 架构特点

### 模块化设计

项目采用现代化的模块化架构：

- **处理器层** (`handlers/`)：负责处理 Telegram 命令和回调
- **服务层** (`services/`)：封装业务逻辑，如单词管理、翻译、调度等
- **数据层** (`models/`)：数据库操作和数据模型
- **工具层** (`utils/`)：配置管理、日志设置等通用工具

### 核心组件

1. **单词管理器** - 自动扫描和管理多个单词表文件
2. **翻译服务** - 集成 Ollama AI 模型提供即时翻译
3. **调度服务** - 智能的自动发送功能，支持随机间隔
4. **数据库管理** - 完整的用户数据、学习历史和统计功能

## 🗄️ 数据库结构

### 主要数据表

- **users** - 用户信息和活跃状态
- **user_settings** - 用户个性化设置（自动发送、单词表选择等）
- **word_history** - 学习历史记录
- **translation_cache** - 翻译结果缓存

## 🔧 管理工具

使用内置的管理工具查看和管理数据：

```bash
python admin.py users           # 显示所有用户
python admin.py stats [chat_id] # 显示统计信息
python admin.py popular [数量]   # 显示热门单词
python admin.py clean [天数]     # 清理旧数据
```

## 📚 添加新单词表

1. **准备单词表文件**
   - 将文件放入 `data/wordlists/` 目录
   - 文件名格式：`4000_Essential_English_Words_Book_2nd_Edition.名称.txt`
   - 内容格式：每行用逗号分隔单词

2. **示例格式**
   ```
   apple, banana, cherry, date, elderberry
   fruit, vegetable, meat, dairy, grain
   ```

3. **自动识别**
   - 机器人会自动扫描新文件
   - 用户可通过 `/wordlist` 命令选择新单词表

## 🛠️ 开发和扩展

### 本地开发

```bash
# 克隆项目
git clone <repository_url>
cd ai-english-bot

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export TELEGRAM_BOT_TOKEN="your_token"

# 启动机器人
python app.py
```

### 扩展功能

项目的模块化架构使得添加新功能变得简单：

1. **新的翻译服务** - 在 `services/translation.py` 中扩展
2. **新的命令处理** - 在 `handlers/commands.py` 中添加
3. **新的数据模型** - 在 `models/database.py` 中扩展
4. **新的工具函数** - 在 `utils/` 目录中添加

### 代码示例

```python
# 添加新的命令处理器
async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理新命令"""
    await update.message.reply_text("新功能!")

# 在 telegram_bot.py 中注册
application.add_handler(CommandHandler("new", new_command))
```

## 📋 依赖说明

- **ollama** - 本地 AI 模型服务，用于翻译功能
- **python-telegram-bot** - Telegram Bot API 库
- **loguru** - 现代化的日志记录库
- **sqlite3** - 内置数据库（Python 标准库）

## 🔍 故障排除

### 常见问题

1. **机器人无法启动**
   - 检查 `TELEGRAM_BOT_TOKEN` 环境变量是否设置
   - 确认网络连接正常

2. **翻译功能失败**
   - 确认 Ollama 服务正在运行
   - 检查 `qwen2.5:7b` 模型是否已下载

3. **单词表未找到**
   - 确认单词表文件在 `data/wordlists/` 目录中
   - 检查文件名格式是否正确

### 日志查看

```bash
# 查看运行日志
tail -f logs/telegram_bot.log

# 查看错误日志
tail -f logs/error.log
```

## 🔒 隐私说明

- 本机器人仅存储必要的用户学习数据
- 不收集用户敏感信息
- 所有数据存储在本地数据库中
- 翻译缓存仅用于提高响应速度

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进项目。

---

**开始您的英语学习之旅吧！🚀**
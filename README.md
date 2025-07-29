# AI English Bot - 英语学习机器人

## 🎯 项目简介

这是一个基于Telegram的智能英语学习机器人，集成了**ECDICT词典**和**AI翻译**功能，为用户提供高质量的英语学习体验。

## ✨ 核心功能

### 📖 智能翻译
- **ECDICT离线词典**：770,611个词条的权威英汉词典
- **AI翻译回退**：当词典中没有时使用Ollama AI翻译
- **缓存机制**：避免重复查询，提升响应速度

### 🔍 详细词汇信息
- 📚 **音标**：国际音标发音指导
- 🇨🇳 **中文释义**：准确的中文翻译
- 🇬🇧 **英文释义**：原版英文定义
- 📝 **词性标注**：名词、动词、形容词等
- ⭐ **权威评级**：柯林斯星级、牛津3000核心词汇
- 📊 **词频信息**：BNC和现代语料库词频排名
- 🎯 **考试范围**：中考、高考、四六级、雅思、托福、GRE标注
- 🔄 **词形变化**：过去式、现在分词、复数等完整变位

### 📚 词汇管理
- 单词历史记录
- 学习进度跟踪
- 个性化推送

## 🚀 快速开始

### 环境要求
```bash
Python 3.8+
Telegram Bot Token
Ollama (可选，用于AI翻译回退)
```

### 安装依赖
```bash
pip install -r requirements.txt
```

### ECDICT词典设置
```bash
# 检查词典状态
python setup_ecdict.py --status

# 转换CSV到SQLite（自动提升查询性能）
python setup_ecdict.py --convert

# 测试翻译功能
python test_ecdict.py
```

### 配置环境变量
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export OLLAMA_HOST="http://localhost:11434"  # 可选
```

### 启动机器人
```bash
python app.py
```

## 📁 项目结构

```
ai-english-bot/
├── data/
│   └── ecdict/              # ECDICT词典数据（子模块）
│       ├── ecdict.csv       # 原始CSV数据 (62.9MB)
│       ├── ecdict.db        # SQLite数据库 (182.2MB)
│       └── stardict.py      # 词典接口
├── src/
│   └── bot/
│       ├── services/
│       │   ├── ecdict_service.py    # ECDICT词典服务
│       │   ├── translation.py      # 智能翻译服务
│       │   └── ...
│       ├── handlers/        # Telegram处理器
│       └── models/         # 数据模型
├── setup_ecdict.py         # ECDICT设置工具
├── test_ecdict.py          # 翻译功能测试
└── app.py                  # 主程序入口
```

## 🔧 技术架构

### 翻译服务优先级
1. **缓存查询** - 最快响应
2. **ECDICT词典** - 权威离线词典
3. **AI翻译** - 智能回退方案

### ECDICT集成优势
- ✅ **离线查询**：无需网络，响应迅速
- ✅ **权威数据**：基于BNC语料库和各类考试大纲
- ✅ **丰富信息**：不仅是翻译，更是完整的词汇学习工具
- ✅ **高性能**：SQLite数据库，毫秒级查询
- ✅ **大容量**：77万+词条，覆盖各个水平

## 📊 数据统计

- 📚 词条总数：**770,611**
- 💾 数据库大小：**182.2 MB**
- ⚡ 平均查询时间：**< 10ms**
- 🎯 考试覆盖：中考、高考、四六级、考研、雅思、托福、GRE

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目！

### ECDICT数据更新
ECDICT作为Git子模块管理，可以通过以下命令更新：
```bash
cd data/ecdict
git pull origin master
cd ../..
python setup_ecdict.py --convert  # 重新转换数据库
```

## 📄 许可证

本项目采用MIT许可证。ECDICT词典数据遵循其原始许可证。

## 🙏 致谢

- [ECDICT](https://github.com/skywind3000/ECDICT) - 提供优秀的开源英汉词典
- [Telegram Bot API](https://core.telegram.org/bots/api) - 强大的机器人平台
- [Ollama](https://ollama.ai/) - 本地AI模型服务

---

**让英语学习更智能，让词汇掌握更高效！** 🎓✨
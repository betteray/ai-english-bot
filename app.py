#!/usr/bin/env python3
"""
英语学习机器人 - 新的主入口文件
"""
import os
import sys
from loguru import logger

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot.telegram_bot import TelegramBot
from bot.utils.config import Config
from bot.utils.logger import setup_logger


def main():
    """主函数"""
    # 设置日志
    setup_logger()
    
    logger.info("英语学习机器人启动中...")
    
    # 验证配置
    if not Config.validate_config():
        logger.error("配置验证失败")
        print("错误：未设置环境变量 TELEGRAM_BOT_TOKEN")
        print("请使用以下命令设置：")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return 1
    
    # 获取配置
    token = Config.get_telegram_token()
    
    try:
        # 创建并启动机器人
        bot = TelegramBot(token)
        bot.run()
    except KeyboardInterrupt:
        logger.info("接收到退出信号，正在关闭机器人...")
    except Exception as e:
        logger.error(f"机器人启动失败: {e}")
        return 1
    
    logger.info("机器人已退出")
    return 0


if __name__ == "__main__":
    sys.exit(main())
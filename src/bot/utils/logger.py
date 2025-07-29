"""
工具模块 - 日志配置
"""
import os
from loguru import logger


def setup_logger():
    """设置日志配置"""
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    # 配置日志
    logger.add("logs/telegram_bot.log", rotation="1 day", retention="7 days", level="INFO")
    logger.add("logs/error.log", rotation="1 day", retention="30 days", level="ERROR")
    
    return logger
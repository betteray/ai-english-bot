"""
配置管理模块
"""
import os
from typing import Optional


class Config:
    """配置管理类"""
    
    @staticmethod
    def get_telegram_token() -> Optional[str]:
        """获取 Telegram Bot Token"""
        return os.getenv("TELEGRAM_BOT_TOKEN")
    
    @staticmethod
    def validate_config() -> bool:
        """验证配置是否完整"""
        token = Config.get_telegram_token()
        if not token:
            return False
        return True
    
    @staticmethod
    def get_data_dir() -> str:
        """获取数据目录路径"""
        return os.path.join(os.path.dirname(__file__), "../../../data")
    
    @staticmethod
    def get_wordlists_dir() -> str:
        """获取单词表目录路径"""
        return os.path.join(Config.get_data_dir(), "wordlists")
    
    @staticmethod
    def get_logs_dir() -> str:
        """获取日志目录路径"""
        return os.path.join(os.path.dirname(__file__), "../../../logs")
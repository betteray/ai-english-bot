"""
Telegram Bot 主类 - 简化版
"""
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from loguru import logger

from .handlers.commands import (
    start_command, word_command, auto_start_command, 
    auto_stop_command, stats_command, wordlist_command
)
from .handlers.callbacks import translation_callback, wordlist_callback


class TelegramBot:
    """Telegram 机器人主类"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = None
        self._setup_application()
    
    def _setup_application(self):
        """设置应用程序和处理器"""
        logger.info("正在初始化 Telegram Bot Application...")
        
        # 创建应用程序
        self.application = Application.builder().token(self.token).build()
        
        # 注册命令处理器
        self.application.add_handler(CommandHandler("start", start_command))
        self.application.add_handler(CommandHandler("word", word_command))
        self.application.add_handler(CommandHandler("auto_start", auto_start_command))
        self.application.add_handler(CommandHandler("auto_stop", auto_stop_command))
        self.application.add_handler(CommandHandler("stats", stats_command))
        self.application.add_handler(CommandHandler("wordlist", wordlist_command))
        
        # 注册回调处理器
        self.application.add_handler(
            CallbackQueryHandler(translation_callback, pattern=r"translate_.*")
        )
        self.application.add_handler(
            CallbackQueryHandler(wordlist_callback, pattern=r"(select_wordlist_.*|refresh_wordlist)")
        )
        
        logger.info("机器人初始化完成")
    
    async def run_async(self):
        """异步启动机器人"""
        logger.info("英语学习机器人启动中...")
        
        try:
            # 初始化应用程序
            await self.application.initialize()
            await self.application.bot.initialize()
            
            logger.info("机器人启动完成，开始监听消息...")
            
            # 启动应用程序
            await self.application.start()
            await self.application.updater.start_polling()
            
            # 保持运行
            await asyncio.Event().wait()
            
        except Exception as e:
            logger.error(f"机器人运行时发生错误: {e}")
            raise
        finally:
            # 清理资源
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
    
    def run(self):
        """启动机器人（同步接口）"""
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭机器人...")
        except Exception as e:
            logger.error(f"机器人启动失败: {e}")
            raise
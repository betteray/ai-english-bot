"""
Telegram Bot 主类 - 简化版
"""
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from loguru import logger

from .handlers.commands import (
    start_command, word_command, auto_start_command, 
    auto_stop_command, stats_command, wordlist_command,
    upload_command, my_wordlists_command, handle_document, my_words_command
)
from .handlers.callbacks import translation_callback, wordlist_callback
from .services.word_service import WordService


class TelegramBot:
    """Telegram 机器人主类"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = None
        self._setup_application()
    
    async def handle_text_message(self, update, context):
        """处理文本消息"""
        # 尝试处理用户发送的单词
        handled = await WordService.handle_user_word_input(update)
        if not handled:
            # 如果不是单词，可以在这里添加其他处理逻辑
            pass
    
    async def handle_query_wordlist_callback(self, update, context):
        """处理查询单词表相关回调的包装函数"""
        await WordService.handle_query_wordlist_callback(update)
    
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
        self.application.add_handler(CommandHandler("upload", upload_command))
        self.application.add_handler(CommandHandler("my_wordlists", my_wordlists_command))
        self.application.add_handler(CommandHandler("my_words", my_words_command))
        
        # 注册文档处理器
        self.application.add_handler(
            MessageHandler(filters.Document.ALL, handle_document)
        )
        
        # 注册文本消息处理器（用于处理用户发送的单词）
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message)
        )
        
        # 注册回调处理器
        self.application.add_handler(
            CallbackQueryHandler(translation_callback, pattern=r"translate_.*")
        )
        self.application.add_handler(
            CallbackQueryHandler(wordlist_callback, pattern=r"(select_wordlist_.*|refresh_wordlist|my_wordlists|separator|delete_wordlist_.*|confirm_delete_.*|cancel_delete)")
        )
        # 添加查询单词表相关的回调处理器
        self.application.add_handler(
            CallbackQueryHandler(self.handle_query_wordlist_callback, 
                               pattern=r"(create_query_wordlist|view_query_words|clear_query_words|confirm_clear_query|cancel_clear_query)")
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
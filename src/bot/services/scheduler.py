"""
调度服务 - 简化版
"""
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from loguru import logger

from .word_manager import word_manager
from ..models.database import db_manager


class SchedulerService:
    """调度服务类"""
    
    @staticmethod
    async def start_auto_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """开启自动发送单词功能"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        # 更新用户信息和自动发送状态
        db_manager.add_or_update_user(
            chat_id=chat_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        db_manager.update_auto_send_status(chat_id, True)
        
        logger.info(f"用户 {user.username or user.first_name} (ID: {chat_id}) 开启了自动发送单词功能")
        
        # 获取用户设置
        settings = db_manager.get_user_settings(chat_id)
        
        # 移除已存在的任务（如果有）
        current_jobs = context.job_queue.get_jobs_by_name(f"auto_word_{chat_id}")
        for job in current_jobs:
            job.schedule_removal()
        
        # 开始第一个任务
        interval = random.randint(settings['interval_min'], settings['interval_max'])
        context.job_queue.run_once(
            SchedulerService.send_auto_word, 
            interval, 
            chat_id=chat_id,
            name=f"auto_word_{chat_id}"
        )
        
        await update.message.reply_text(
            f"自动发送单词功能已开启！\n"
            f"我会随机间隔{settings['interval_min']}-{settings['interval_max']}秒发送单词给你。"
        )
    
    @staticmethod
    async def stop_auto_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """停止自动发送单词功能"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        # 更新数据库中的自动发送状态
        db_manager.update_auto_send_status(chat_id, False)
        
        logger.info(f"用户 {user.username or user.first_name} (ID: {chat_id}) 关闭了自动发送单词功能")
        
        # 移除该用户的定时任务
        current_jobs = context.job_queue.get_jobs_by_name(f"auto_word_{chat_id}")
        for job in current_jobs:
            job.schedule_removal()
        
        await update.message.reply_text("自动发送单词功能已关闭。")
    
    @staticmethod
    async def send_auto_word(context: ContextTypes.DEFAULT_TYPE) -> None:
        """自动发送随机单词给用户，带翻译按钮"""
        chat_id = context.job.chat_id
        
        # 检查用户是否仍然启用自动发送
        settings = db_manager.get_user_settings(chat_id)
        if not settings['auto_send_enabled']:
            logger.debug(f"用户 {chat_id} 已关闭自动发送，停止任务")
            return
        
        # 确保使用用户选择的单词表
        user_wordlist = db_manager.get_user_wordlist(chat_id)
        logger.debug(f"自动发送 - 用户 (ID: {chat_id}) 的选择单词表: {user_wordlist}")
        
        # 获取当前word_manager的单词表状态
        current_wordlist_before = word_manager.get_current_wordlist_info()
        logger.debug(f"自动发送 - 切换前当前单词表: {current_wordlist_before}")
        
        word_manager.switch_wordlist(user_wordlist)
        
        # 确认切换后的状态
        current_wordlist_after = word_manager.get_current_wordlist_info()
        logger.debug(f"自动发送 - 切换后当前单词表: {current_wordlist_after}")
        
        word = word_manager.get_random_word()
        
        # 记录自动发送的单词到历史
        db_manager.add_word_to_history(chat_id, word)
        
        logger.debug(f"自动发送单词给用户 (ID: {chat_id}): {word} (来自单词表: {current_wordlist_after['name']})")
        
        # 创建翻译按钮
        keyboard = [[InlineKeyboardButton("🔤 翻译", callback_data=f"translate_{word}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"📝 学习时间到！\n\n{word}",
                reply_markup=reply_markup
            )
            
            # 安排下一次发送
            interval = random.randint(settings['interval_min'], settings['interval_max'])
            context.job_queue.run_once(
                SchedulerService.send_auto_word,
                interval,
                chat_id=chat_id,
                name=f"auto_word_{chat_id}"
            )
            logger.debug(f"下次自动发送单词将在 {interval} 秒后进行 (用户 ID: {chat_id})")
            
        except Exception as e:
            logger.error(f"自动发送单词失败 (用户 ID: {chat_id}): {e}")
            # 如果发送失败（如用户阻止了机器人），停止自动发送
            db_manager.update_auto_send_status(chat_id, False)
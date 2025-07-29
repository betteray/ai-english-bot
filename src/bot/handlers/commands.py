"""
命令处理器 - 简化版
"""
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger

from ..services.word_service import WordService
from ..services.word_manager import word_manager
from ..services.scheduler import SchedulerService
from ..models.database import db_manager


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /start 命令"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # 添加或更新用户信息到数据库
    db_manager.add_or_update_user(
        chat_id=chat_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # 获取用户当前选择的单词表并切换到该单词表
    user_wordlist = db_manager.get_user_wordlist(chat_id)
    word_manager.switch_wordlist(user_wordlist)
    
    word_count = word_manager.get_word_count()
    user_stats = db_manager.get_user_stats(chat_id)
    current_wordlist = word_manager.get_current_wordlist_info()
    
    logger.info(f"用户 {user.username or user.first_name} (ID: {chat_id}) 启动了机器人")
    
    await update.message.reply_text(
        f"欢迎使用英语学习机器人！\n"
        f"📚 当前使用单词表：{current_wordlist['name']} ({word_count} 个单词)\n"
        f"📊 您的学习统计：\n"
        f"   • 总学习单词：{user_stats['total_words']} 个\n"
        f"   • 今日学习：{user_stats['today_words']} 个\n"
        f"   • 已翻译：{user_stats['translated_words']} 个\n\n"
        "📖 发送 /word 开始学习单词\n"
        "📚 发送 /wordlist 选择单词表\n"
        "⚙️ 发送 /auto_start 开启自动发送\n"
        "⏹️ 发送 /auto_stop 关闭自动发送\n"
        "📊 发送 /stats 查看详细统计"
    )


async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /word 命令 - 发送随机单词"""
    await WordService.send_random_word(update)


async def auto_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /auto_start 命令 - 开启自动发送"""
    await SchedulerService.start_auto_send(update, context)


async def auto_stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /auto_stop 命令 - 停止自动发送"""
    await SchedulerService.stop_auto_send(update, context)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /stats 命令 - 显示统计信息"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # 更新用户活动
    db_manager.add_or_update_user(
        chat_id=chat_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    stats_data = db_manager.get_user_stats(chat_id)
    recent_count = db_manager.get_user_word_count(chat_id, days=7)
    settings = db_manager.get_user_settings(chat_id)
    
    logger.info(f"用户 {user.username or user.first_name} (ID: {chat_id}) 查看统计信息")
    
    status_text = "🟢 开启" if settings['auto_send_enabled'] else "🔴 关闭"
    
    await update.message.reply_text(
        f"📊 您的学习统计\n\n"
        f"📚 总学习单词：{stats_data['total_words']} 个\n"
        f"📅 今日学习：{stats_data['today_words']} 个\n"
        f"📝 最近7天：{recent_count} 个\n"
        f"🔤 已翻译：{stats_data['translated_words']} 个\n"
        f"⚙️ 自动发送：{status_text}\n\n"
        f"💪 继续加油学习！"
    )


async def wordlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /wordlist 命令 - 显示单词表菜单"""
    await WordService.show_wordlist_menu(update)
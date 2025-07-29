"""
单词服务 - 简化版
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

from .word_manager import word_manager
from ..models.database import db_manager


class WordService:
    """单词服务类"""
    
    @staticmethod
    async def send_random_word(update: Update) -> None:
        """发送随机单词"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        # 确保使用用户选择的单词表
        user_wordlist = db_manager.get_user_wordlist(chat_id)
        logger.debug(f"用户 {user.username or user.first_name} (ID: {chat_id}) 的选择单词表: {user_wordlist}")
        
        # 获取当前word_manager的单词表状态
        current_wordlist_before = word_manager.get_current_wordlist_info()
        logger.debug(f"切换前当前单词表: {current_wordlist_before}")
        
        word_manager.switch_wordlist(user_wordlist)
        
        # 确认切换后的状态
        current_wordlist_after = word_manager.get_current_wordlist_info()
        logger.debug(f"切换后当前单词表: {current_wordlist_after}")
        
        word = word_manager.get_random_word()
        
        # 更新用户活动并记录单词学习历史
        db_manager.add_or_update_user(
            chat_id=chat_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        db_manager.add_word_to_history(chat_id, word)
        
        logger.info(f"用户 {user.username or user.first_name} (ID: {chat_id}) 请求随机单词: {word} (来自单词表: {current_wordlist_after['name']})")
        
        # 创建翻译按钮
        keyboard = [[InlineKeyboardButton("🔤 翻译", callback_data=f"translate_{word}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(word, reply_markup=reply_markup)
    
    @staticmethod
    async def show_wordlist_menu(update: Update) -> None:
        """显示单词表选择菜单"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        # 更新用户活动
        db_manager.add_or_update_user(
            chat_id=chat_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # 获取所有可用的单词表
        available_wordlists = word_manager.get_available_wordlists()
        current_wordlist_name = db_manager.get_user_wordlist(chat_id)
        
        logger.info(f"用户 {user.username or user.first_name} (ID: {chat_id}) 查看单词表菜单")
        
        if not available_wordlists:
            await update.message.reply_text("❌ 没有找到可用的单词表文件。")
            return
        
        # 创建单词表选择按钮 - 按名称排序
        keyboard = []
        # 按单词表名称排序
        sorted_wordlists = sorted(available_wordlists.items(), key=lambda x: x[1]['display_name'])
        
        for wordlist_name, wordlist_info in sorted_wordlists:
            prefix = "✅ " if wordlist_name == current_wordlist_name else "📚 "
            button_text = f"{prefix}{wordlist_info['display_name']}"
            keyboard.append([InlineKeyboardButton(
                button_text, 
                callback_data=f"select_wordlist_{wordlist_name}"
            )])
        
        # 添加刷新按钮
        keyboard.append([InlineKeyboardButton("🔄 刷新列表", callback_data="refresh_wordlist")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📚 请选择要使用的单词表：\n\n"
            "✅ 表示当前选择的单词表\n"
            "📚 表示可选择的单词表",
            reply_markup=reply_markup
        )
    
    @staticmethod
    async def handle_wordlist_callback(update: Update) -> None:
        """处理单词表选择回调"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        user = query.from_user
        # 修复：使用聊天ID而不是用户ID，保持与其他方法一致
        chat_id = query.message.chat_id
        
        if callback_data.startswith("select_wordlist_"):
            wordlist_name = callback_data[16:]
            
            logger.info(f"用户 {user.username or user.first_name} (ID: {user.id}) 在聊天 {chat_id} 中选择单词表: {wordlist_name}")
            
            # 检查单词表是否有效
            available_wordlists = word_manager.get_available_wordlists()
            if wordlist_name not in available_wordlists:
                await query.edit_message_text("❌ 选择的单词表不存在。")
                return
            
            # 切换单词表
            success = word_manager.switch_wordlist(wordlist_name)
            if not success:
                await query.edit_message_text(f"❌ 切换到单词表 {wordlist_name} 失败。")
                return
            
            # 更新数据库中的用户选择 - 使用聊天ID
            db_manager.update_user_wordlist(chat_id, wordlist_name)
            
            # 获取新单词表信息
            current_wordlist = word_manager.get_current_wordlist_info()
            word_count = word_manager.get_word_count()
            
            await query.edit_message_text(
                f"✅ 已切换到单词表：{current_wordlist['name']}\n"
                f"📊 包含 {word_count} 个单词\n\n"
                f"现在可以使用 /word 开始学习新单词表中的单词了！"
            )
            
        elif callback_data == "refresh_wordlist":
            logger.info(f"用户 {user.username or user.first_name} (ID: {user.id}) 在聊天 {chat_id} 中刷新单词表列表")
            
            # 重新扫描单词表
            word_manager.available_wordlists = word_manager.scan_wordlists()
            
            available_wordlists = word_manager.get_available_wordlists()
            current_wordlist_name = db_manager.get_user_wordlist(chat_id)
            
            if not available_wordlists:
                await query.edit_message_text("❌ 没有找到可用的单词表文件。")
                return
            
            # 重新创建按钮 - 按名称排序
            keyboard = []
            # 按单词表名称排序
            sorted_wordlists = sorted(available_wordlists.items(), key=lambda x: x[1]['display_name'])
            
            for wordlist_name, wordlist_info in sorted_wordlists:
                prefix = "✅ " if wordlist_name == current_wordlist_name else "📚 "
                button_text = f"{prefix}{wordlist_info['display_name']}"
                keyboard.append([InlineKeyboardButton(
                    button_text, 
                    callback_data=f"select_wordlist_{wordlist_name}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔄 刷新列表", callback_data="refresh_wordlist")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📚 请选择要使用的单词表：\n\n"
                "✅ 表示当前选择的单词表\n"
                "📚 表示可选择的单词表",
                reply_markup=reply_markup
            )
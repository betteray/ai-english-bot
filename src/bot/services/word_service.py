"""
单词服务 - 简化版
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger
import os

from .word_manager import word_manager
from ..models.database import db_manager
from .translation import TranslationService


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
        
        # 创建单词表选择按钮 - 按类型和名称排序
        keyboard = []
        
        # 分别处理系统单词表和用户单词表
        system_wordlists = []
        user_wordlists = []
        
        for wordlist_name, wordlist_info in available_wordlists.items():
            if wordlist_info['type'] == 'system':
                system_wordlists.append((wordlist_name, wordlist_info))
            elif wordlist_info['type'] == 'user':
                # 只显示当前用户自己的单词表
                filename = os.path.basename(wordlist_info['full_path'])
                if filename.startswith(f"{chat_id}_"):
                    user_wordlists.append((wordlist_name, wordlist_info))
        
        # 按名称排序
        system_wordlists.sort(key=lambda x: x[1]['display_name'])
        user_wordlists.sort(key=lambda x: x[1]['display_name'])
        
        # 添加系统单词表
        for wordlist_name, wordlist_info in system_wordlists:
            prefix = "✅ " if wordlist_name == current_wordlist_name else "📚 "
            button_text = f"{prefix}{wordlist_info['display_name']} ({wordlist_info['word_count']}词)"
            keyboard.append([InlineKeyboardButton(
                button_text, 
                callback_data=f"select_wordlist_{wordlist_name}"
            )])
        
        # 添加分隔线（如果有用户单词表）
        if user_wordlists:
            keyboard.append([InlineKeyboardButton("━━━ 📁 我的单词表 ━━━", callback_data="separator")])
        
        # 添加用户单词表
        for wordlist_name, wordlist_info in user_wordlists:
            prefix = "✅ " if wordlist_name == current_wordlist_name else ""
            button_text = f"{prefix}{wordlist_info['display_name']} ({wordlist_info['word_count']}词)"
            keyboard.append([InlineKeyboardButton(
                button_text, 
                callback_data=f"select_wordlist_{wordlist_name}"
            )])
        
        # 添加功能按钮
        keyboard.append([
            InlineKeyboardButton("🔄 刷新列表", callback_data="refresh_wordlist"),
            InlineKeyboardButton("📁 我的单词表", callback_data="my_wordlists")
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = (
            "📚 <b>选择单词表</b>\n\n"
            "✅ 当前使用的单词表\n"
            "📚 系统默认单词表\n"
            "📁 用户上传的单词表\n\n"
            "💡 <b>提示：</b>\n"
            "• 发送 /upload 上传自定义单词表\n"
            "• 发送 /my_wordlists 管理我的单词表"
        )
        
        await update.message.reply_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
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
    
    @staticmethod
    async def handle_user_word_input(update: Update) -> bool:
        """处理用户发送的单词输入"""
        message_text = update.message.text.strip()
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        # 检查是否是英文单词（简单验证：只包含字母，长度合理）
        if not message_text.isalpha() or len(message_text) < 2 or len(message_text) > 30:
            return False
        
        # 检查是否包含中文字符
        if any('\u4e00' <= char <= '\u9fff' for char in message_text):
            return False
        
        word = message_text.lower()
        
        logger.info(f"用户 {user.username or user.first_name} (ID: {chat_id}) 发送单词: {word}")
        
        try:
            # 翻译单词
            translation = TranslationService.translate(word)
            
            # 更新用户活动
            db_manager.add_or_update_user(
                chat_id=chat_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            
            # 添加到用户查询单词记录
            db_manager.add_user_query_word(chat_id, word, translation)
            
            # 添加到学习历史
            db_manager.add_word_to_history(chat_id, word, translated=True, translation=translation)
            
            # 创建按钮
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            keyboard = [
                [InlineKeyboardButton("📝 创建我的单词表", callback_data="create_query_wordlist")],
                [InlineKeyboardButton("📋 查看我的查询记录", callback_data="view_query_words")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                translation,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
            return True
            
        except Exception as e:
            logger.error(f"处理用户单词输入失败: {e}")
            await update.message.reply_text(
                f"❌ 翻译单词 '{word}' 时出现错误: {str(e)}"
            )
            return True
    
    @staticmethod
    async def handle_query_wordlist_callback(update: Update) -> None:
        """处理查询单词表相关回调"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        chat_id = query.message.chat_id
        user = query.from_user
        
        if callback_data == "create_query_wordlist":
            # 创建查询单词表
            result = word_manager.create_user_query_wordlist(chat_id)
            
            if result['success']:
                # 自动切换到新创建的单词表
                wordlist_key = result['wordlist_key']
                word_manager.switch_wordlist(wordlist_key)
                db_manager.update_user_wordlist(chat_id, wordlist_key)
                
                await query.edit_message_text(
                    f"✅ <b>单词表创建成功！</b>\n\n"
                    f"📄 名称：{result['display_name']}\n"
                    f"📊 包含 {result['word_count']} 个单词\n"
                    f"🎯 已自动切换为当前学习单词表\n\n"
                    f"现在可以使用 /word 命令从您的查询单词表中学习单词了！\n\n"
                    f"💡 使用 /wordlist 可以切换其他单词表",
                    parse_mode='HTML'
                )
            else:
                await query.edit_message_text(
                    f"❌ <b>创建失败</b>\n\n{result['error']}\n\n"
                    f"💡 请先发送一些英文单词给我，然后再尝试创建单词表",
                    parse_mode='HTML'
                )
                
        elif callback_data == "view_query_words":
            # 查看查询记录
            query_words = db_manager.get_user_query_words(chat_id, limit=20)
            
            if not query_words:
                await query.edit_message_text(
                    "📋 <b>您的查询记录</b>\n\n"
                    "暂无查询记录\n\n"
                    "💡 发送英文单词给我，我会为您翻译并记录",
                    parse_mode='HTML'
                )
                return
            
            # 构建查询记录消息
            message_lines = ["📋 <b>您的查询记录</b>\n"]
            
            for i, word_data in enumerate(query_words[:10], 1):
                word = word_data['word']
                message_lines.append(f"{i}. <code>{word}</code>")
            
            if len(query_words) > 10:
                message_lines.append(f"\n... 还有 {len(query_words) - 10} 个单词")
            
            total_count = db_manager.get_user_query_words_count(chat_id)
            message_lines.append(f"\n📊 总计查询了 {total_count} 个不同的单词")
            
            # 检查是否已有查询单词表
            query_info = word_manager.get_user_query_wordlist_info(chat_id)
            
            keyboard = []
            if query_info['query_words_count'] > 0:
                if not query_info['exists']:
                    keyboard.append([InlineKeyboardButton(
                        "📝 创建我的单词表", 
                        callback_data="create_query_wordlist"
                    )])
                else:
                    wordlist_info = query_info['wordlist_info']
                    keyboard.append([InlineKeyboardButton(
                        f"📚 切换到我的单词表 ({wordlist_info['word_count']}词)", 
                        callback_data=f"select_wordlist_{query_info['wordlist_key']}"
                    )])
            
            keyboard.append([InlineKeyboardButton("🗑️ 清空记录", callback_data="clear_query_words")])
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            await query.edit_message_text(
                '\n'.join(message_lines),
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        elif callback_data == "clear_query_words":
            # 清空查询记录确认
            keyboard = [
                [
                    InlineKeyboardButton("✅ 确认清空", callback_data="confirm_clear_query"),
                    InlineKeyboardButton("❌ 取消", callback_data="cancel_clear_query")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "⚠️ <b>确认清空查询记录</b>\n\n"
                "此操作将删除您所有的单词查询记录，但不会影响已创建的单词表。\n\n"
                "🚨 <b>注意：此操作不可恢复！</b>\n\n"
                "确定要清空所有查询记录吗？",
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
        elif callback_data == "confirm_clear_query":
            # 执行清空操作
            success = db_manager.clear_user_query_words(chat_id)
            
            if success:
                await query.edit_message_text(
                    "✅ <b>查询记录已清空</b>\n\n"
                    "您的单词查询记录已全部删除。\n"
                    "已创建的单词表不受影响。\n\n"
                    "💡 继续发送英文单词给我，开始新的学习记录！",
                    parse_mode='HTML'
                )
            else:
                await query.edit_message_text(
                    "❌ <b>清空失败</b>\n\n"
                    "清空查询记录时发生错误，请稍后重试。",
                    parse_mode='HTML'
                )
                
        elif callback_data == "cancel_clear_query":
            # 取消清空，返回查询记录界面
            await WordService.handle_query_wordlist_callback(
                type('MockUpdate', (), {
                    'callback_query': type('MockQuery', (), {
                        'answer': lambda: None,
                        'data': 'view_query_words',
                        'message': query.message,
                        'from_user': query.from_user,
                        'edit_message_text': query.edit_message_text
                    })()
                })()
            )
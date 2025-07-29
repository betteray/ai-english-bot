"""
回调处理器 - 简化版
"""
from telegram import Update
from telegram.ext import ContextTypes

from ..services.translation import TranslationService
from ..services.word_service import WordService
from ..services.word_manager import word_manager


async def translation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理翻译按钮回调"""
    await TranslationService.handle_translation_callback(update)


async def wordlist_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理单词表选择回调"""
    query = update.callback_query
    callback_data = query.data
    
    if callback_data == "my_wordlists":
        # 处理"我的单词表"按钮
        await query.answer()
        chat_id = query.message.chat_id
        user_wordlists = word_manager.get_user_wordlists(chat_id)
        
        if not user_wordlists:
            await query.edit_message_text(
                "📁 您还没有上传任何单词表\n\n"
                "💡 发送 /upload 查看如何上传单词表"
            )
        else:
            message_lines = ["📁 <b>您的单词表</b>\n"]
            
            for wordlist in user_wordlists:
                # 去掉数字前缀，直接显示单词表名称
                display_name = wordlist['display_name'].replace('📁 ', '')  # 移除可能的文件夹图标
                message_lines.append(
                    f"• {display_name}\n"
                    f"  📊 单词数：{wordlist['word_count']} 个\n"
                )
            
            message_lines.append(
                "\n💡 <b>管理提示：</b>\n"
                "• 发送 /wordlist 切换使用的单词表\n"
                "• 发送 /my_wordlists 管理我的单词表\n"
                "• 发送 /upload 上传新的单词表"
            )
            
            await query.edit_message_text(
                '\n'.join(message_lines),
                parse_mode='HTML'
            )
    elif callback_data.startswith("delete_wordlist_"):
        # 处理删除单词表按钮
        await query.answer()
        chat_id = query.message.chat_id
        user_id = query.from_user.id
        wordlist_key = callback_data[16:]  # 移除 "delete_wordlist_" 前缀
        
        # 获取单词表信息用于显示
        available_wordlists = word_manager.get_available_wordlists()
        wordlist_info = available_wordlists.get(wordlist_key)
        
        if not wordlist_info:
            await query.edit_message_text(
                "❌ 单词表不存在或已被删除\n\n"
                "💡 发送 /my_wordlists 刷新列表"
            )
            return
        
        display_name = wordlist_info['display_name'].replace('📁 ', '')
        
        # 创建确认删除的按钮
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [
                InlineKeyboardButton("✅ 确认删除", callback_data=f"confirm_delete_{wordlist_key}"),
                InlineKeyboardButton("❌ 取消", callback_data="cancel_delete")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"⚠️ <b>确认删除单词表</b>\n\n"
            f"📄 名称：{display_name}\n"
            f"📊 单词数：{wordlist_info['word_count']} 个\n\n"
            f"🚨 <b>注意：此操作不可恢复！</b>\n"
            f"删除后该单词表将永久丢失。\n\n"
            f"确定要删除这个单词表吗？",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
    elif callback_data.startswith("confirm_delete_"):
        # 处理确认删除操作
        await query.answer()
        chat_id = query.message.chat_id
        user_id = query.from_user.id
        wordlist_key = callback_data[15:]  # 移除 "confirm_delete_" 前缀
        
        # 获取单词表信息用于显示
        available_wordlists = word_manager.get_available_wordlists()
        wordlist_info = available_wordlists.get(wordlist_key)
        display_name = wordlist_info['display_name'].replace('📁 ', '') if wordlist_info else "未知单词表"
        
        # 执行删除操作
        success = word_manager.delete_user_wordlist(wordlist_key, user_id)
        
        if success:
            await query.edit_message_text(
                f"✅ <b>删除成功</b>\n\n"
                f"已删除单词表：{display_name}\n\n"
                f"💡 发送 /my_wordlists 查看剩余的单词表\n"
                f"📚 发送 /wordlist 选择其他单词表",
                parse_mode='HTML'
            )
        else:
            await query.edit_message_text(
                f"❌ <b>删除失败</b>\n\n"
                f"无法删除单词表：{display_name}\n"
                f"可能的原因：\n"
                f"• 文件不存在\n"
                f"• 权限不足\n"
                f"• 不是您上传的单词表\n\n"
                f"💡 发送 /my_wordlists 查看您的单词表",
                parse_mode='HTML'
            )
        
    elif callback_data == "cancel_delete":
        # 处理取消删除操作
        await query.answer("已取消删除操作")
        chat_id = query.message.chat_id
        
        # 返回到单词表管理界面
        user_wordlists = word_manager.get_user_wordlists(chat_id)
        
        if not user_wordlists:
            await query.edit_message_text(
                "📁 您还没有上传任何单词表\n\n"
                "💡 发送 /upload 查看如何上传单词表"
            )
            return
        
        # 重新显示单词表管理界面
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = []
        message_lines = ["📁 <b>您的单词表管理</b>\n"]
        
        for i, wordlist in enumerate(user_wordlists, 1):
            display_name = wordlist['display_name'].replace('📁 ', '')
            message_lines.append(
                f"{i}. {display_name}\n"
                f"   📊 单词数：{wordlist['word_count']} 个\n"
            )
            
            keyboard.append([
                InlineKeyboardButton(
                    f"🗑️ 删除「{display_name}」", 
                    callback_data=f"delete_wordlist_{wordlist['key']}"
                )
            ])
        
        message_lines.append(
            "\n💡 <b>管理提示：</b>\n"
            "• 点击下方按钮删除对应的单词表\n"
            "• 发送 /wordlist 切换使用的单词表\n"
            "• 发送 /upload 上传新的单词表\n\n"
            "⚠️ <b>注意：删除操作不可恢复</b>"
        )
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            '\n'.join(message_lines),
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        
    elif callback_data == "separator":
        # 分隔线按钮，不做任何操作
        await query.answer("这只是分隔线", show_alert=False)
    else:
        # 其他单词表相关回调
        await WordService.handle_wordlist_callback(update)
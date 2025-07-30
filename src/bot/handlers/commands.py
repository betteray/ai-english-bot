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
        "🎯 <b>学习功能：</b>\n"
        "📖 发送 /word 开始学习单词\n"
        "💬 直接发送英文单词给我，获取翻译\n"
        "📋 发送 /my_words 查看查询记录\n\n"
        "📚 <b>单词表管理：</b>\n"
        "📚 发送 /wordlist 选择单词表\n"
        "📁 发送 /upload 上传自定义单词表\n"
        "🗂️ 发送 /my_wordlists 管理我的单词表\n\n"
        "⚙️ <b>自动功能：</b>\n"
        "▶️ 发送 /auto_start 开启自动发送\n"
        "⏹️ 发送 /auto_stop 关闭自动发送\n"
        "📊 发送 /stats 查看详细统计\n\n"
        "💡 <b>提示：</b>直接发送英文单词给我，我会翻译并记录，您可以用这些单词创建专属的学习单词表！",
        parse_mode='HTML'
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


async def upload_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /upload 命令 - 上传单词表说明"""
    await update.message.reply_text(
        "📁 <b>上传自定义单词表</b>\n\n"
        "🔸 <b>支持格式：</b>\n"
        "   • 文本文件 (.txt)\n"
        "   • 每行一个或多个单词，用逗号分隔\n"
        "   • 支持空行和标题行（会自动过滤）\n\n"
        "🔸 <b>示例格式：</b>\n"
        "<code>apple, banana, cherry\n"
        "dog, cat, bird\n"
        "hello, world, peace</code>\n\n"
        "📝 <b>文件命名重要提示：</b>\n"
        "   • 请给文件起有意义的名字，如：\n"
        "   • <code>生活用品.txt</code>\n"
        "   • <code>商务英语.txt</code>\n"
        "   • <code>旅行词汇.txt</code>\n"
        "   • <code>考研单词.txt</code>\n"
        "   • 文件名将作为单词表名称显示\n\n"
        "📎 请直接发送文件给我，我会自动处理！\n\n"
        "💡 <b>提示：</b>\n"
        "   • 文件大小限制：10MB\n"
        "   • 建议单词数量：50-5000个\n"
        "   • 重复单词会自动去重\n"
        "   • 支持中英文文件名",
        parse_mode='HTML'
    )


async def my_wordlists_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /my_wordlists 命令 - 显示用户的单词表"""
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    chat_id = update.effective_chat.id
    user_wordlists = word_manager.get_user_wordlists(chat_id)
    
    if not user_wordlists:
        await update.message.reply_text(
            "📁 您还没有上传任何单词表\n\n"
            "💡 发送 /upload 查看如何上传单词表"
        )
        return
    
    # 创建带删除按钮的键盘
    keyboard = []
    message_lines = ["📁 <b>您的单词表管理</b>\n"]
    
    for i, wordlist in enumerate(user_wordlists, 1):
        # 去掉数字前缀，直接显示单词表名称
        display_name = wordlist['display_name'].replace('📁 ', '')  # 移除可能的文件夹图标
        message_lines.append(
            f"{i}. {display_name}\n"
            f"   📊 单词数：{wordlist['word_count']} 个\n"
        )
        
        # 为每个单词表添加删除按钮
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
    
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    await update.message.reply_text(
        '\n'.join(message_lines),
        parse_mode='HTML',
        reply_markup=reply_markup
    )


async def my_words_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理 /my_words 命令 - 显示用户查询的单词记录"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    # 更新用户活动
    db_manager.add_or_update_user(
        chat_id=chat_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # 获取用户查询的单词
    query_words = db_manager.get_user_query_words(chat_id, limit=20)
    
    if not query_words:
        await update.message.reply_text(
            "📋 <b>您的查询记录</b>\n\n"
            "暂无查询记录\n\n"
            "💡 发送英文单词给我，我会为您翻译并记录\n"
            "💡 发送 /help 查看更多使用方法",
            parse_mode='HTML'
        )
        return
    
    # 构建查询记录消息
    message_lines = ["📋 <b>您的查询记录</b>\n"]
    
    for i, word_data in enumerate(query_words[:15], 1):
        word = word_data['word']
        message_lines.append(f"{i}. <code>{word}</code>")
    
    if len(query_words) > 15:
        message_lines.append(f"\n... 还有 {len(query_words) - 15} 个单词")
    
    total_count = db_manager.get_user_query_words_count(chat_id)
    message_lines.append(f"\n📊 总计查询了 {total_count} 个不同的单词")
    
    # 检查是否已有查询单词表
    query_info = word_manager.get_user_query_wordlist_info(chat_id)
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
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
    
    await update.message.reply_text(
        '\n'.join(message_lines),
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理文档上传"""
    if not update.message.document:
        return
    
    document = update.message.document
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    logger.info(f"用户 {user.username or user.first_name} (ID: {chat_id}) 上传文件: {document.file_name}")
    
    # 检查文件类型
    if not document.file_name.lower().endswith('.txt'):
        await update.message.reply_text(
            "❌ 只支持 .txt 格式的文本文件\n"
            "💡 发送 /upload 查看支持的格式"
        )
        return
    
    # 检查文件大小 (10MB = 10 * 1024 * 1024 bytes)
    if document.file_size > 10 * 1024 * 1024:
        await update.message.reply_text(
            "❌ 文件太大！最大支持 10MB\n"
            "💡 请压缩文件或分割成较小的文件"
        )
        return
    
    try:
        # 下载文件
        processing_msg = await update.message.reply_text("📥 正在处理文件...")
        
        file = await context.bot.get_file(document.file_id)
        file_content = await file.download_as_bytearray()
        
        # 尝试用不同编码读取文件内容
        content = None
        for encoding in ['utf-8', 'gbk', 'gb2312', 'ascii']:
            try:
                content = file_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            await processing_msg.edit_text(
                "❌ 文件编码不支持\n"
                "💡 请确保文件是UTF-8或GBK编码的文本文件"
            )
            return
        
        # 保存用户单词表
        result = word_manager.save_user_wordlist(
            user_id=chat_id,
            filename=document.file_name,
            content=content
        )
        
        if result['success']:
            await processing_msg.edit_text(
                f"✅ <b>单词表上传成功！</b>\n\n"
                f"📄 显示名称：{result['display_name']}\n"
                f"📁 文件名：{result['filename']}\n"
                f"📊 单词数量：{result['word_count']} 个\n\n"
                f"💡 发送 /wordlist 切换到新的单词表\n"
                f"📚 发送 /my_wordlists 查看所有单词表",
                parse_mode='HTML'
            )
            
            logger.info(f"用户 {chat_id} 单词表上传成功: {result['filename']}")
        else:
            await processing_msg.edit_text(
                f"❌ <b>上传失败</b>\n\n"
                f"错误信息：{result['error']}\n\n"
                f"💡 发送 /upload 查看正确的文件格式",
                parse_mode='HTML'
            )
            
            logger.error(f"用户 {chat_id} 单词表上传失败: {result['error']}")
            
    except Exception as e:
        logger.error(f"处理文件上传失败: {e}")
        await update.message.reply_text(
            f"❌ 处理文件时发生错误\n"
            f"错误信息：{str(e)}\n\n"
            f"💡 请稍后重试或联系管理员"
        )
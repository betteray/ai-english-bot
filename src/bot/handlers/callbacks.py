"""
回调处理器 - 简化版
"""
from telegram import Update
from telegram.ext import ContextTypes

from ..services.translation import TranslationService
from ..services.word_service import WordService


async def translation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理翻译按钮回调"""
    await TranslationService.handle_translation_callback(update)


async def wordlist_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理单词表选择回调"""
    await WordService.handle_wordlist_callback(update)
"""
翻译服务 - 集成 ECDICT 词典
"""
from telegram import Update
from loguru import logger
from ollama import chat
from ollama import ChatResponse

from ..models.database import db_manager
from .ecdict_service import ecdict_service


class TranslationService:
    """翻译服务类"""
    
    @staticmethod
    def translate(word: str) -> str:
        """翻译单词"""
        logger.debug(f"开始翻译单词: {word}")
        
        # 首先尝试从缓存获取翻译
        cached_translation = db_manager.get_cached_translation(word)
        if cached_translation:
            logger.debug(f"使用缓存翻译 - {word}: {cached_translation}")
            return cached_translation
        
        # 优先使用 ECDICT 词典
        if ecdict_service.is_available():
            try:
                ecdict_result = ecdict_service.translate(word)
                logger.debug(f"ECDICT 翻译成功 - {word}")
                
                # 缓存翻译结果
                db_manager.cache_translation(word, ecdict_result)
                return ecdict_result
            except Exception as e:
                logger.warning(f"ECDICT 翻译失败，回退到 AI 翻译 - {word}: {e}")
        
        # 回退到 AI 翻译
        try:
            response: ChatResponse = chat(model='qwen2.5:7b', messages=[
                {
                    'role': 'user',
                    'content': f'请翻译英文单词 "{word}"，包括音标、词性、中文释义和例句。',
                },
            ])
            
            translation = response.message.content
            logger.debug(f"AI 翻译完成 - {word}: {translation}")
            
            # 缓存翻译结果
            db_manager.cache_translation(word, translation)
            
            return translation
            
        except Exception as e:
            logger.error(f"翻译API调用失败 - {word}: {str(e)}")
            raise
    
    @staticmethod
    async def handle_translation_callback(update: Update) -> None:
        """处理翻译按钮点击事件"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        if callback_data.startswith("translate_"):
            word = callback_data[10:]
            user = query.from_user
            chat_id = user.id
            
            logger.info(f"用户 {user.username or user.first_name} (ID: {chat_id}) 请求翻译单词: {word}")
            
            try:
                translation = TranslationService.translate(word)
                logger.debug(f"翻译成功 - {word}")
                
                # 更新数据库，标记该单词已被翻译
                db_manager.add_word_to_history(chat_id, word, translated=True, translation=translation)
                
                # 更新消息，显示翻译结果
                await query.edit_message_text(
                    text=translation,
                    parse_mode='HTML'
                )
            except Exception as e:
                logger.error(f"翻译失败 - {word}: {str(e)}")
                await query.edit_message_text(
                    text=f"📖 单词: {word}\n❌ 翻译失败: {str(e)}"
                )
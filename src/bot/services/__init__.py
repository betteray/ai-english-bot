"""
服务模块 - 集成所有业务服务
"""

from .translation import TranslationService
from .ecdict_service import ECDictService, ecdict_service
from .word_service import WordService
from .word_manager import WordManager
from .scheduler import SchedulerService

__all__ = [
    'TranslationService',
    'ECDictService', 
    'ecdict_service',
    'WordService',
    'WordManager',
    'SchedulerService'
]
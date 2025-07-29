"""
ECDICT 词典服务
基于 ECDICT 词典数据库提供英汉翻译服务
"""
import os
import sys
from typing import Optional, Dict, Any
from loguru import logger

# 将 ECDICT 路径添加到 Python 路径
ECDICT_PATH = os.path.join(os.path.dirname(__file__), '../../../data/ecdict')
sys.path.insert(0, ECDICT_PATH)

try:
    import stardict
except ImportError as e:
    logger.error(f"无法导入 ECDICT 模块: {e}")
    stardict = None


class ECDictService:
    """ECDICT 词典服务类"""
    
    def __init__(self):
        self.dict_db = None
        self.csv_db = None
        self._initialize_dict()
    
    def _initialize_dict(self):
        """初始化词典数据库"""
        if not stardict:
            logger.error("ECDICT 模块未正确导入")
            return
        
        try:
            # 优先使用 SQLite 数据库（如果存在）
            sqlite_path = os.path.join(ECDICT_PATH, 'ecdict.db')
            if os.path.exists(sqlite_path):
                self.dict_db = stardict.StarDict(sqlite_path)
                logger.info(f"成功加载 SQLite 词典数据库: {sqlite_path}")
            else:
                # 回退到 CSV 文件
                csv_path = os.path.join(ECDICT_PATH, 'ecdict.csv')
                if os.path.exists(csv_path):
                    self.csv_db = stardict.DictCsv(csv_path)
                    logger.info(f"成功加载 CSV 词典数据库: {csv_path}")
                else:
                    logger.warning("未找到 ECDICT 数据文件")
        except Exception as e:
            logger.error(f"初始化 ECDICT 失败: {e}")
    
    def is_available(self) -> bool:
        """检查 ECDICT 服务是否可用"""
        return self.dict_db is not None or self.csv_db is not None
    
    def query_word(self, word: str) -> Optional[Dict[str, Any]]:
        """查询单词"""
        if not self.is_available():
            return None
        
        try:
            # 清理输入的单词
            word = word.strip().lower()
            
            # 优先使用 SQLite 数据库
            if self.dict_db:
                result = self.dict_db.query(word)
            elif self.csv_db:
                result = self.csv_db.query(word)
            else:
                return None
            
            return result
        except Exception as e:
            logger.error(f"查询单词 '{word}' 失败: {e}")
            return None
    
    def format_translation(self, word_data: Dict[str, Any]) -> str:
        """格式化翻译结果"""
        if not word_data:
            return ""
        
        lines = []
        
        # 单词
        word = word_data.get('word', '')
        lines.append(f"📖 **{word}**")
        
        # 音标
        phonetic = word_data.get('phonetic', '')
        if phonetic:
            lines.append(f"🔊 /{phonetic}/")
        
        # 中文释义
        translation = word_data.get('translation', '')
        if translation:
            lines.append(f"🇨🇳 {translation}")
        
        # 英文释义
        definition = word_data.get('definition', '')
        if definition:
            lines.append(f"🇬🇧 {definition}")
        
        # 词性
        pos = word_data.get('pos', '')
        if pos:
            lines.append(f"📝 词性: {pos}")
        
        # 词频和等级信息
        collins = word_data.get('collins', 0)
        oxford = word_data.get('oxford', 0)
        bnc = word_data.get('bnc', '')
        frq = word_data.get('frq', '')
        
        level_info = []
        if collins and collins > 0:
            level_info.append(f"柯林斯: {collins}星")
        if oxford and oxford > 0:
            level_info.append("牛津3000")
        if bnc and str(bnc) != '0':
            level_info.append(f"BNC词频: {bnc}")
        if frq and str(frq) != '0':
            level_info.append(f"现代词频: {frq}")
        
        if level_info:
            lines.append(f"⭐ {' | '.join(level_info)}")
        
        # 考试标签
        tag = word_data.get('tag', '')
        if tag:
            tag_mapping = {
                'zk': '中考', 'gk': '高考', 'ky': '考研',
                'cet4': '四级', 'cet6': '六级',
                'toefl': '托福', 'ielts': '雅思', 'gre': 'GRE'
            }
            tags = []
            for t in tag.split():
                if t in tag_mapping:
                    tags.append(tag_mapping[t])
            if tags:
                lines.append(f"🎯 考试范围: {' | '.join(tags)}")
        
        # 词形变化
        exchange = word_data.get('exchange', '')
        if exchange:
            exchange_info = self._format_exchange(exchange)
            if exchange_info:
                lines.append(f"🔄 {exchange_info}")
        
        return '\n'.join(lines)
    
    def _format_exchange(self, exchange: str) -> str:
        """格式化词形变化信息"""
        if not exchange:
            return ""
        
        try:
            # 解析 exchange 字段
            exchanges = {}
            for item in exchange.split('/'):
                if ':' in item:
                    key, value = item.split(':', 1)
                    exchanges[key] = value
            
            exchange_names = {
                'p': '过去式', 'd': '过去分词', 'i': '现在分词', 
                '3': '第三人称单数', 'r': '比较级', 't': '最高级', 
                's': '复数', '0': '原型'
            }
            
            formatted = []
            for key in ['p', 'd', 'i', '3', 'r', 't', 's', '0']:
                if key in exchanges:
                    name = exchange_names.get(key, key)
                    formatted.append(f"{name}: {exchanges[key]}")
            
            return ', '.join(formatted) if formatted else ""
        except Exception as e:
            logger.error(f"格式化词形变化失败: {e}")
            return ""
    
    def search_similar_words(self, word: str, limit: int = 5) -> list:
        """搜索相似单词"""
        if not self.is_available():
            return []
        
        try:
            word = word.strip().lower()
            
            if self.dict_db:
                matches = self.dict_db.match(word, limit, strip=True)
            elif self.csv_db:
                matches = self.csv_db.match(word, limit, strip=True)
            else:
                return []
            
            # 返回单词列表
            return [match[1] for match in matches] if matches else []
        except Exception as e:
            logger.error(f"搜索相似单词失败: {e}")
            return []
    
    def translate(self, word: str) -> str:
        """翻译单词（主要接口）"""
        # 首先精确查询
        word_data = self.query_word(word)
        if word_data:
            return self.format_translation(word_data)
        
        # 如果没找到，尝试搜索相似单词
        similar_words = self.search_similar_words(word)
        if similar_words:
            suggestions = ', '.join(similar_words[:3])
            return f"❌ 未找到单词 '{word}'\n💡 你是否要查找: {suggestions}"
        
        return f"❌ 词典中未找到单词 '{word}'"


# 创建全局实例
ecdict_service = ECDictService()
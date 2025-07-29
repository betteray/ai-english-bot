"""
单词管理模块 - 简化版
"""
import random
import os
import glob
from loguru import logger


class WordManager:
    """单词管理器"""
    
    def __init__(self):
        # 修复路径计算，确保正确指向项目根目录的 data/wordlists
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        self.wordlists_dir = os.path.join(project_root, "data", "wordlists")
        logger.debug(f"单词表目录: {self.wordlists_dir}")
        self.available_wordlists = self.scan_wordlists()
        self.current_wordlist = "3"
        self.words = []
        if self.available_wordlists:
            self.load_wordlist(self.current_wordlist)
        else:
            logger.warning("未找到任何单词表文件，使用默认单词")
            self.words = ["apple", "banana", "cherry"]
    
    def scan_wordlists(self):
        """扫描可用的单词表"""
        pattern = os.path.join(self.wordlists_dir, "4000_Essential_English_Words_Book_2nd_Edition.*.txt")
        wordlist_files = glob.glob(pattern)
        
        wordlists = {}
        for file_path in wordlist_files:
            filename = os.path.basename(file_path)
            if filename.startswith("4000_Essential_English_Words_Book_2nd_Edition.") and filename.endswith(".txt"):
                name = filename[46:-4]  # 提取册数
                wordlists[name] = {
                    'file_path': filename,
                    'full_path': file_path,
                    'display_name': f"4000核心英语单词 第{name}册"
                }
        
        logger.debug(f"发现单词表: {list(wordlists.keys())}")
        return wordlists
    
    def load_wordlist(self, wordlist_name: str) -> bool:
        """加载指定的单词表"""
        if wordlist_name not in self.available_wordlists:
            logger.error(f"单词表 {wordlist_name} 不存在")
            return False
        
        file_path = self.available_wordlists[wordlist_name]['full_path']
        logger.info(f"加载单词表: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            words = []
            lines = content.strip().split('\n')
            
            for line in lines:
                if line.strip() and not (line.isupper() or 'The Real Saint Nick' in line):
                    line_words = [word.strip() for word in line.split(',') if word.strip()]
                    words.extend(line_words)
            
            self.words = sorted(list(set(words)))
            self.current_wordlist = wordlist_name
            logger.success(f"成功加载 {len(self.words)} 个单词")
            return True
            
        except Exception as e:
            logger.error(f"加载单词表失败: {e}")
            self.words = ["apple", "banana", "cherry"]
            return False
    
    def get_random_word(self) -> str:
        """获取随机单词"""
        if not self.words:
            return "apple"
        return random.choice(self.words)
    
    def get_word_count(self) -> int:
        """获取单词数量"""
        return len(self.words)
    
    def get_available_wordlists(self) -> dict:
        """获取可用单词表"""
        return self.available_wordlists.copy()
    
    def get_current_wordlist_info(self) -> dict:
        """获取当前单词表信息"""
        return {
            'name': self.current_wordlist,
            'word_count': len(self.words)
        }
    
    def switch_wordlist(self, wordlist_name: str) -> bool:
        """切换单词表"""
        return self.load_wordlist(wordlist_name)


# 创建全局实例
word_manager = WordManager()
"""
单词管理模块 - 简化版
"""
import random
import os
import glob
from datetime import datetime
from loguru import logger


class WordManager:
    """单词管理器"""
    
    def __init__(self):
        # 修复路径计算，确保正确指向项目根目录的 data/wordlists
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
        self.wordlists_dir = os.path.join(project_root, "data", "wordlists")
        # 创建用户上传的单词表目录
        self.user_wordlists_dir = os.path.join(self.wordlists_dir, "user_uploads")
        os.makedirs(self.user_wordlists_dir, exist_ok=True)
        logger.debug(f"单词表目录: {self.wordlists_dir}")
        logger.debug(f"用户单词表目录: {self.user_wordlists_dir}")
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
        # 扫描系统默认单词表
        pattern = os.path.join(self.wordlists_dir, "4000_Essential_English_Words_Book_2nd_Edition.*.txt")
        wordlist_files = glob.glob(pattern)
        
        wordlists = {}
        
        # 处理系统默认单词表
        for file_path in wordlist_files:
            filename = os.path.basename(file_path)
            if filename.startswith("4000_Essential_English_Words_Book_2nd_Edition.") and filename.endswith(".txt"):
                name = filename[46:-4]  # 提取册数
                wordlists[name] = {
                    'file_path': filename,
                    'full_path': file_path,
                    'display_name': f"4000核心英语单词 第{name}册",
                    'type': 'system',
                    'word_count': 0  # 稍后计算
                }
        
        # 扫描用户上传的单词表
        user_pattern = os.path.join(self.user_wordlists_dir, "*.txt")
        user_wordlist_files = glob.glob(user_pattern)
        
        for file_path in user_wordlist_files:
            filename = os.path.basename(file_path)
            name = f"user_{filename[:-4]}"  # 添加 user_ 前缀避免冲突
            
            # 从文件名中提取原始文件名
            # 格式：{user_id}_{timestamp}_{original_filename}.txt
            parts = filename[:-4].split('_', 2)  # 分割成最多3部分
            if len(parts) >= 3:
                original_filename = parts[2]  # 第三部分是原始文件名
                # 特殊处理查询单词表
                if original_filename == "query":
                    display_name = "我的查询单词表"
                else:
                    display_name = self._generate_display_name_from_filename(original_filename + '.txt')
            else:
                # 如果格式不符合预期，使用完整文件名
                display_name = self._generate_display_name_from_filename(filename)
            
            wordlists[name] = {
                'file_path': filename,
                'full_path': file_path,
                'display_name': f"📁 {display_name}",
                'type': 'user',
                'word_count': 0  # 稍后计算
            }
        
        # 计算每个单词表的单词数量
        for name, info in wordlists.items():
            try:
                word_count = self._count_words_in_file(info['full_path'])
                wordlists[name]['word_count'] = word_count
            except Exception as e:
                logger.error(f"计算单词表 {name} 的单词数量失败: {e}")
                wordlists[name]['word_count'] = 0
        
        logger.debug(f"发现单词表: {list(wordlists.keys())}")
        return wordlists
    
    def _count_words_in_file(self, file_path: str) -> int:
        """计算文件中的单词数量"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            words = []
            lines = content.strip().split('\n')
            
            for line in lines:
                if line.strip() and not (line.isupper() or 'The Real Saint Nick' in line):
                    line_words = [word.strip() for word in line.split(',') if word.strip()]
                    words.extend(line_words)
            
            return len(set(words))  # 去重后的单词数量
        except Exception as e:
            logger.error(f"读取文件 {file_path} 失败: {e}")
            return 0
    
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
    
    def _generate_display_name_from_filename(self, original_filename: str) -> str:
        """根据原始文件名生成显示名称"""
        if not original_filename:
            return "自定义单词表"
        
        # 移除扩展名
        name = original_filename
        if name.lower().endswith('.txt'):
            name = name[:-4]
        
        # 如果是用户上传的文件，可能包含数字前缀，需要处理
        # 检查是否以数字开头，如果是则移除数字前缀
        parts = name.split()
        if parts and parts[0].isdigit():
            # 移除第一个数字部分
            name = ' '.join(parts[1:])
        
        # 如果名称为空或只有数字，使用默认名称
        if not name or name.isdigit():
            return "自定义单词表"
        
        # 替换下划线和连字符为空格，让名称更美观
        display_name = name.replace('_', ' ').replace('-', ' ')
        
        # 移除开头的数字（如果存在）
        # 处理类似 "123456 浴室单词" 的情况
        import re
        display_name = re.sub(r'^\d+\s*', '', display_name)
        
        # 如果处理后名称为空，使用默认名称
        if not display_name.strip():
            return "自定义单词表"
        
        # 首字母大写
        display_name = ' '.join(word.capitalize() for word in display_name.split())
        
        return display_name

    def save_user_wordlist(self, user_id: int, filename: str, content: str) -> dict:
        """保存用户上传的单词表"""
        try:
            # 直接使用用户的文件名生成显示名称
            display_name = self._generate_display_name_from_filename(filename)
            
            # 清理文件名，移除非法字符
            safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            if not safe_filename.endswith('.txt'):
                safe_filename += '.txt'
            
            # 添加时间戳和用户ID避免文件名冲突
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_filename = f"{user_id}_{timestamp}_{safe_filename}"
            file_path = os.path.join(self.user_wordlists_dir, final_filename)
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            # 验证文件内容并计算单词数量
            word_count = self._count_words_in_file(file_path)
            
            if word_count == 0:
                # 如果没有找到有效单词，删除文件
                os.remove(file_path)
                return {
                    'success': False,
                    'error': '文件中没有找到有效的单词，请检查文件格式'
                }
            
            # 重新扫描单词表
            self.available_wordlists = self.scan_wordlists()
            
            logger.info(f"用户 {user_id} 上传单词表成功: {final_filename} -> {display_name} ({word_count} 个单词)")
            
            return {
                'success': True,
                'filename': final_filename,
                'display_name': display_name,
                'word_count': word_count,
                'wordlist_key': f"user_{final_filename[:-4]}"
            }
            
        except Exception as e:
            logger.error(f"保存用户单词表失败: {e}")
            return {
                'success': False,
                'error': f'保存文件失败: {str(e)}'
            }
    
    def delete_user_wordlist(self, wordlist_key: str, user_id: int) -> bool:
        """删除用户上传的单词表"""
        try:
            if not wordlist_key.startswith('user_'):
                logger.error(f"尝试删除非用户单词表: {wordlist_key}")
                return False
            
            if wordlist_key not in self.available_wordlists:
                logger.error(f"单词表不存在: {wordlist_key}")
                return False
            
            wordlist_info = self.available_wordlists[wordlist_key]
            if wordlist_info['type'] != 'user':
                logger.error(f"尝试删除非用户单词表: {wordlist_key}")
                return False
            
            file_path = wordlist_info['full_path']
            filename = os.path.basename(file_path)
            
            # 验证文件是否属于该用户（文件名以用户ID开头）
            if not filename.startswith(f"{user_id}_"):
                logger.error(f"用户 {user_id} 尝试删除不属于自己的单词表: {filename}")
                return False
            
            # 删除文件
            os.remove(file_path)
            
            # 重新扫描单词表
            self.available_wordlists = self.scan_wordlists()
            
            # 如果当前使用的就是被删除的单词表，切换到默认单词表
            if self.current_wordlist == wordlist_key:
                default_wordlist = "3" if "3" in self.available_wordlists else list(self.available_wordlists.keys())[0]
                self.load_wordlist(default_wordlist)
            
            logger.info(f"用户 {user_id} 删除单词表成功: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"删除用户单词表失败: {e}")
            return False
    
    def get_user_wordlists(self, user_id: int) -> list:
        """获取用户上传的单词表列表"""
        user_wordlists = []
        for key, info in self.available_wordlists.items():
            if info['type'] == 'user':
                filename = os.path.basename(info['full_path'])
                if filename.startswith(f"{user_id}_"):
                    user_wordlists.append({
                        'key': key,
                        'display_name': info['display_name'],
                        'word_count': info['word_count'],
                        'filename': filename
                    })
        return user_wordlists

    def create_user_query_wordlist(self, chat_id: int) -> dict:
        """创建用户查询单词表"""
        from ..models.database import db_manager
        
        # 获取用户查询的单词
        query_words = db_manager.get_user_query_words(chat_id)
        
        if not query_words:
            return {
                'success': False,
                'error': '您还没有查询过任何单词，请先发送一些英文单词给我'
            }
        
        try:
            # 创建单词表内容
            words_content = []
            for word_data in query_words:
                words_content.append(word_data['word'])
            
            # 去重并排序
            unique_words = sorted(list(set(words_content)))
            content = ', '.join(unique_words)
            
            # 生成文件名 - 使用更短的名称避免callback_data过长
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"query_{timestamp}.txt"  # 简化文件名
            final_filename = f"{chat_id}_{timestamp}_query.txt"
            file_path = os.path.join(self.user_wordlists_dir, final_filename)
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            # 验证文件内容并计算单词数量
            word_count = len(unique_words)
            
            # 重新扫描单词表
            self.available_wordlists = self.scan_wordlists()
            
            logger.info(f"用户 {chat_id} 创建查询单词表成功: {final_filename} ({word_count} 个单词)")
            
            return {
                'success': True,
                'filename': final_filename,
                'display_name': f"📝 我的查询单词表",
                'word_count': word_count,
                'wordlist_key': f"user_{final_filename[:-4]}"
            }
            
        except Exception as e:
            logger.error(f"创建用户查询单词表失败: {e}")
            return {
                'success': False,
                'error': f'创建单词表失败: {str(e)}'
            }

    def get_user_query_wordlist_info(self, chat_id: int) -> dict:
        """获取用户查询单词表信息"""
        from ..models.database import db_manager
        
        # 查找是否已存在查询单词表（新格式：{chat_id}_{timestamp}_query.txt）
        query_wordlist_key = None
        for key, info in self.available_wordlists.items():
            if info['type'] == 'user':
                filename = os.path.basename(info['full_path'])
                if filename.startswith(f"{chat_id}_") and filename.endswith("_query.txt"):
                    query_wordlist_key = key
                    break
        
        # 获取用户查询单词数量
        query_words_count = db_manager.get_user_query_words_count(chat_id)
        
        return {
            'exists': query_wordlist_key is not None,
            'wordlist_key': query_wordlist_key,
            'query_words_count': query_words_count,
            'wordlist_info': self.available_wordlists.get(query_wordlist_key) if query_wordlist_key else None
        }


# 创建全局实例
word_manager = WordManager()
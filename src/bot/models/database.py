"""
数据库管理模块 - 简化版
"""
import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, List
from loguru import logger


class DatabaseManager:
    def __init__(self, db_path: str = "english_bot.db"):
        """初始化数据库管理器"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库表"""
        logger.info("正在初始化数据库...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # 创建用户设置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    chat_id INTEGER PRIMARY KEY,
                    auto_send_enabled BOOLEAN DEFAULT 0,
                    auto_send_interval_min INTEGER DEFAULT 30,
                    auto_send_interval_max INTEGER DEFAULT 120,
                    selected_wordlist TEXT DEFAULT '3',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES users (chat_id)
                )
            ''')
            
            # 创建单词学习历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS word_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER,
                    word TEXT NOT NULL,
                    translated BOOLEAN DEFAULT 0,
                    translation TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (chat_id) REFERENCES users (chat_id)
                )
            ''')
            
            # 创建翻译缓存表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS translation_cache (
                    word TEXT PRIMARY KEY,
                    translation TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 1
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_word_history_chat_id ON word_history(chat_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_word_history_created_at ON word_history(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity)')
            
            conn.commit()
            logger.success("数据库初始化完成")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def add_or_update_user(self, chat_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """添加或更新用户信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT chat_id FROM users WHERE chat_id = ?', (chat_id,))
            user_exists = cursor.fetchone() is not None
            
            if user_exists:
                cursor.execute('''
                    UPDATE users 
                    SET username = ?, first_name = ?, last_name = ?, last_activity = CURRENT_TIMESTAMP, is_active = 1
                    WHERE chat_id = ?
                ''', (username, first_name, last_name, chat_id))
            else:
                cursor.execute('''
                    INSERT INTO users (chat_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (chat_id, username, first_name, last_name))
                
                cursor.execute('''
                    INSERT INTO user_settings (chat_id)
                    VALUES (?)
                ''', (chat_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"添加/更新用户失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_user_settings(self, chat_id: int) -> dict:
        """获取用户设置"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT auto_send_enabled, auto_send_interval_min, auto_send_interval_max, selected_wordlist
                FROM user_settings WHERE chat_id = ?
            ''', (chat_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'auto_send_enabled': bool(result[0]),
                    'interval_min': result[1],
                    'interval_max': result[2],
                    'selected_wordlist': result[3] or '3'
                }
            else:
                cursor.execute('INSERT INTO user_settings (chat_id) VALUES (?)', (chat_id,))
                conn.commit()
                return {
                    'auto_send_enabled': False,
                    'interval_min': 30,
                    'interval_max': 120,
                    'selected_wordlist': '3'
                }
                
        except Exception as e:
            logger.error(f"获取用户设置失败: {e}")
            return {
                'auto_send_enabled': False,
                'interval_min': 30,
                'interval_max': 120,
                'selected_wordlist': '3'
            }
        finally:
            conn.close()
    
    def update_auto_send_status(self, chat_id: int, enabled: bool) -> bool:
        """更新用户自动发送状态"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE user_settings 
                SET auto_send_enabled = ?, updated_at = CURRENT_TIMESTAMP
                WHERE chat_id = ?
            ''', (enabled, chat_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"更新自动发送状态失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def add_word_to_history(self, chat_id: int, word: str, translated: bool = False, translation: str = None):
        """添加单词到学习历史"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO word_history (chat_id, word, translated, translation)
                VALUES (?, ?, ?, ?)
            ''', (chat_id, word, translated, translation))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"添加单词历史失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_user_word_count(self, chat_id: int, days: int = 7) -> int:
        """获取用户最近几天学习的单词数量"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            since_date = datetime.now() - timedelta(days=days)
            cursor.execute('''
                SELECT COUNT(*) FROM word_history 
                WHERE chat_id = ? AND created_at >= ?
            ''', (chat_id, since_date))
            
            result = cursor.fetchone()
            return result[0] if result else 0
            
        except Exception as e:
            logger.error(f"获取用户单词数量失败: {e}")
            return 0
        finally:
            conn.close()
    
    def get_cached_translation(self, word: str) -> Optional[str]:
        """从缓存获取翻译"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT translation FROM translation_cache WHERE word = ?', (word.lower(),))
            result = cursor.fetchone()
            
            if result:
                cursor.execute('''
                    UPDATE translation_cache 
                    SET usage_count = usage_count + 1
                    WHERE word = ?
                ''', (word.lower(),))
                conn.commit()
                return result[0]
            
            return None
            
        except Exception as e:
            logger.error(f"获取缓存翻译失败: {e}")
            return None
        finally:
            conn.close()
    
    def cache_translation(self, word: str, translation: str):
        """缓存翻译结果"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO translation_cache (word, translation)
                VALUES (?, ?)
            ''', (word.lower(), translation))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"缓存翻译失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_user_stats(self, chat_id: int) -> dict:
        """获取用户统计信息"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 总学习单词数
            cursor.execute('SELECT COUNT(*) FROM word_history WHERE chat_id = ?', (chat_id,))
            total_words = cursor.fetchone()[0]
            
            # 今天学习的单词数
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(*) FROM word_history 
                WHERE chat_id = ? AND DATE(created_at) = ?
            ''', (chat_id, today))
            today_words = cursor.fetchone()[0]
            
            # 翻译过的单词数
            cursor.execute('''
                SELECT COUNT(*) FROM word_history 
                WHERE chat_id = ? AND translated = 1
            ''', (chat_id,))
            translated_words = cursor.fetchone()[0]
            
            return {
                'total_words': total_words,
                'today_words': today_words,
                'translated_words': translated_words
            }
            
        except Exception as e:
            logger.error(f"获取用户统计失败: {e}")
            return {
                'total_words': 0,
                'today_words': 0,
                'translated_words': 0
            }
        finally:
            conn.close()
    
    def update_user_wordlist(self, chat_id: int, wordlist_name: str) -> bool:
        """更新用户选择的单词表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE user_settings 
                SET selected_wordlist = ?, updated_at = CURRENT_TIMESTAMP
                WHERE chat_id = ?
            ''', (wordlist_name, chat_id))
            
            if cursor.rowcount == 0:
                cursor.execute('''
                    INSERT INTO user_settings (chat_id, selected_wordlist)
                    VALUES (?, ?)
                ''', (chat_id, wordlist_name))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"更新用户单词表失败: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_user_wordlist(self, chat_id: int) -> str:
        """获取用户选择的单词表"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT selected_wordlist FROM user_settings WHERE chat_id = ?
            ''', (chat_id,))
            
            result = cursor.fetchone()
            return result[0] if result and result[0] else '3'
            
        except Exception as e:
            logger.error(f"获取用户单词表失败: {e}")
            return '3'
        finally:
            conn.close()


# 创建全局数据库管理器实例
db_manager = DatabaseManager()
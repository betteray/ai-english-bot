#!/usr/bin/env python3
"""
英语学习机器人数据库管理工具 - 简化版
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot.models.database import db_manager
from loguru import logger

def show_user_list():
    """显示所有用户列表"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT u.chat_id, u.username, u.first_name, u.created_at, u.last_activity, s.auto_send_enabled
            FROM users u
            LEFT JOIN user_settings s ON u.chat_id = s.chat_id
            ORDER BY u.last_activity DESC
        ''')
        
        users = cursor.fetchall()
        
        print("\n📊 用户列表:")
        print("-" * 80)
        print(f"{'Chat ID':<12} {'用户名':<15} {'姓名':<15} {'注册时间':<12} {'最后活动':<12} {'自动发送'}")
        print("-" * 80)
        
        for user in users:
            chat_id, username, first_name, created_at, last_activity, auto_send = user
            username = username or "无"
            first_name = first_name or "无"
            auto_status = "🟢" if auto_send else "🔴"
            
            # 格式化日期
            created_date = created_at.split()[0] if created_at else "无"
            activity_date = last_activity.split()[0] if last_activity else "无"
            
            print(f"{chat_id:<12} {username:<15} {first_name:<15} {created_date:<12} {activity_date:<12} {auto_status}")
        
        print(f"\n总用户数: {len(users)}")
        
    except Exception as e:
        print(f"查询用户列表失败: {e}")
    finally:
        conn.close()

def show_user_stats(chat_id=None):
    """显示用户统计信息"""
    if chat_id:
        # 显示特定用户的详细统计
        stats = db_manager.get_user_stats(int(chat_id))
        settings = db_manager.get_user_settings(int(chat_id))
        recent_count = db_manager.get_user_word_count(int(chat_id), days=7)
        
        print(f"\n📊 用户 {chat_id} 的详细统计:")
        print("-" * 40)
        print(f"总学习单词: {stats['total_words']} 个")
        print(f"今日学习: {stats['today_words']} 个")
        print(f"最近7天: {recent_count} 个")
        print(f"已翻译: {stats['translated_words']} 个")
        print(f"自动发送: {'开启' if settings['auto_send_enabled'] else '关闭'}")
        print(f"发送间隔: {settings['interval_min']}-{settings['interval_max']} 秒")
    else:
        # 显示全体用户统计
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # 总用户数
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # 活跃用户数（最近7天有活动）
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('SELECT COUNT(*) FROM users WHERE last_activity >= ?', (week_ago,))
            active_users = cursor.fetchone()[0]
            
            # 开启自动发送的用户数
            cursor.execute('SELECT COUNT(*) FROM user_settings WHERE auto_send_enabled = 1')
            auto_users = cursor.fetchone()[0]
            
            # 总学习单词数
            cursor.execute('SELECT COUNT(*) FROM word_history')
            total_words = cursor.fetchone()[0]
            
            # 今日学习单词数
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('SELECT COUNT(*) FROM word_history WHERE DATE(created_at) = ?', (today,))
            today_words = cursor.fetchone()[0]
            
            # 翻译缓存数量
            cursor.execute('SELECT COUNT(*) FROM translation_cache')
            cached_translations = cursor.fetchone()[0]
            
            print("\n📊 全体用户统计:")
            print("-" * 40)
            print(f"总用户数: {total_users}")
            print(f"活跃用户 (7天): {active_users}")
            print(f"自动发送用户: {auto_users}")
            print(f"总学习单词数: {total_words}")
            print(f"今日学习单词: {today_words}")
            print(f"翻译缓存: {cached_translations} 个")
            
        except Exception as e:
            print(f"查询统计信息失败: {e}")
        finally:
            conn.close()

def show_popular_words(limit=10):
    """显示最受欢迎的单词"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT word, COUNT(*) as count
            FROM word_history
            GROUP BY word
            ORDER BY count DESC
            LIMIT ?
        ''', (limit,))
        
        words = cursor.fetchall()
        
        print(f"\n📚 最受欢迎的 {limit} 个单词:")
        print("-" * 30)
        print(f"{'单词':<15} {'学习次数'}")
        print("-" * 30)
        
        for word, count in words:
            print(f"{word:<15} {count}")
            
    except Exception as e:
        print(f"查询热门单词失败: {e}")
    finally:
        conn.close()

def clean_old_data(days=30):
    """清理旧数据"""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 清理旧的单词历史记录
        cursor.execute('DELETE FROM word_history WHERE created_at < ?', (cutoff_date,))
        deleted_words = cursor.rowcount
        
        # 清理使用次数少的翻译缓存
        cursor.execute('DELETE FROM translation_cache WHERE usage_count = 1 AND created_at < ?', (cutoff_date,))
        deleted_cache = cursor.rowcount
        
        conn.commit()
        print(f"\n🧹 数据清理完成:")
        print(f"删除 {days} 天前的单词记录: {deleted_words} 条")
        print(f"删除低使用率的缓存: {deleted_cache} 条")
        
    except Exception as e:
        print(f"数据清理失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python admin.py users          - 显示用户列表")
        print("  python admin.py stats [chat_id] - 显示统计信息")
        print("  python admin.py popular [数量]   - 显示热门单词")
        print("  python admin.py clean [天数]     - 清理旧数据")
        return
    
    command = sys.argv[1]
    
    if command == "users":
        show_user_list()
    elif command == "stats":
        chat_id = sys.argv[2] if len(sys.argv) > 2 else None
        show_user_stats(chat_id)
    elif command == "popular":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        show_popular_words(limit)
    elif command == "clean":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        clean_old_data(days)
    else:
        print(f"未知命令: {command}")

if __name__ == "__main__":
    main()
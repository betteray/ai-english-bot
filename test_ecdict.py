#!/usr/bin/env python3
"""
ECDICT 翻译服务测试工具
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot.services.ecdict_service import ecdict_service

def test_translation():
    """测试翻译功能"""
    print("=== ECDICT 翻译服务测试 ===\n")
    
    # 检查服务是否可用
    if not ecdict_service.is_available():
        print("❌ ECDICT 服务不可用")
        return
    
    print("✅ ECDICT 服务已启动\n")
    
    # 测试单词列表
    test_words = ['hello', 'world', 'python', 'computer', 'love', 'study', 'beautiful']
    
    for word in test_words:
        print(f"🔍 查询单词: {word}")
        print("-" * 50)
        result = ecdict_service.translate(word)
        print(result)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_translation()
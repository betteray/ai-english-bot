#!/usr/bin/env python3
"""
ECDICT 数据库转换工具
将 ECDICT CSV 数据转换为 SQLite 数据库以提高查询性能
"""
import os
import sys
from loguru import logger

# 添加 ECDICT 路径
ECDICT_PATH = os.path.join(os.path.dirname(__file__), 'data/ecdict')
sys.path.insert(0, ECDICT_PATH)

try:
    import stardict
except ImportError as e:
    logger.error(f"无法导入 ECDICT 模块: {e}")
    sys.exit(1)


def convert_csv_to_sqlite():
    """将 CSV 数据转换为 SQLite 数据库"""
    csv_path = os.path.join(ECDICT_PATH, 'ecdict.csv')
    sqlite_path = os.path.join(ECDICT_PATH, 'ecdict.db')
    
    if not os.path.exists(csv_path):
        logger.error(f"CSV 文件不存在: {csv_path}")
        return False
    
    logger.info(f"开始转换 {csv_path} -> {sqlite_path}")
    
    try:
        # 使用 ECDICT 提供的转换函数
        stardict.convert_dict(sqlite_path, csv_path)
        logger.info("转换完成！")
        return True
    except Exception as e:
        logger.error(f"转换失败: {e}")
        return False


def check_database_status():
    """检查数据库状态"""
    csv_path = os.path.join(ECDICT_PATH, 'ecdict.csv')
    sqlite_path = os.path.join(ECDICT_PATH, 'ecdict.db')
    
    logger.info("=== ECDICT 数据库状态 ===")
    
    if os.path.exists(csv_path):
        size_mb = os.path.getsize(csv_path) / (1024 * 1024)
        logger.info(f"✅ CSV 文件: {csv_path} ({size_mb:.1f} MB)")
    else:
        logger.warning(f"❌ CSV 文件不存在: {csv_path}")
    
    if os.path.exists(sqlite_path):
        size_mb = os.path.getsize(sqlite_path) / (1024 * 1024)
        logger.info(f"✅ SQLite 文件: {sqlite_path} ({size_mb:.1f} MB)")
        
        # 测试查询
        try:
            db = stardict.StarDict(sqlite_path)
            count = db.count()
            logger.info(f"📊 词条数量: {count:,}")
            
            # 测试查询一个单词
            test_word = db.query('hello')
            if test_word:
                logger.info(f"🔍 测试查询 'hello': ✅")
            else:
                logger.warning(f"🔍 测试查询 'hello': ❌")
        except Exception as e:
            logger.error(f"数据库测试失败: {e}")
    else:
        logger.warning(f"❌ SQLite 文件不存在: {sqlite_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ECDICT 数据库管理工具')
    parser.add_argument('--convert', action='store_true', help='转换 CSV 到 SQLite')
    parser.add_argument('--status', action='store_true', help='检查数据库状态')
    
    args = parser.parse_args()
    
    if args.convert:
        convert_csv_to_sqlite()
    elif args.status:
        check_database_status()
    else:
        # 默认检查状态，如果没有 SQLite 文件则自动转换
        check_database_status()
        
        sqlite_path = os.path.join(ECDICT_PATH, 'ecdict.db')
        csv_path = os.path.join(ECDICT_PATH, 'ecdict.csv')
        
        if not os.path.exists(sqlite_path) and os.path.exists(csv_path):
            logger.info("SQLite 数据库不存在，开始自动转换...")
            convert_csv_to_sqlite()
            check_database_status()
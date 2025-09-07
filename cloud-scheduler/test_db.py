#!/usr/bin/env python3
"""
测试数据库连接和表结构
"""

import sqlite3
import os

def test_sqlite_database():
    """测试SQLite数据库连接"""
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect('generated_apps.db')
        print("✅ SQLite数据库连接成功")
        
        # 创建游标
        cursor = conn.cursor()
        
        # 查询所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        print(f"📊 数据库中的表: {table_names}")
        
        # 检查generated_apps表是否存在
        if 'generated_apps' in table_names:
            print("✅ generated_apps表存在")
            
            # 查询表结构
            cursor.execute("PRAGMA table_info(generated_apps)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            print(f"📋 generated_apps表结构: {column_names}")
            
            # 查询数据
            cursor.execute("SELECT COUNT(*) FROM generated_apps")
            count = cursor.fetchone()[0]
            print(f"📈 generated_apps表中有 {count} 条记录")
            
            # 显示前几条记录
            if count > 0:
                cursor.execute("SELECT project_id, name, status FROM generated_apps LIMIT 3")
                records = cursor.fetchall()
                print("📋 前几条记录:")
                for record in records:
                    print(f"  - ID: {record[0]}, 名称: {record[1]}, 状态: {record[2]}")
        else:
            print("❌ generated_apps表不存在")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

if __name__ == "__main__":
    test_sqlite_database()
#!/usr/bin/env python3
"""
修复"no such table: apps"错误的脚本
"""

import sqlite3
import json
from datetime import datetime
import traceback

def check_sqlite_database():
    """检查SQLite数据库中的表"""
    try:
        conn = sqlite3.connect('generated_apps.db')
        cursor = conn.cursor()
        
        print("✅ 连接到SQLite数据库")
        
        # 检查所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("📋 数据库中的所有表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查是否有'apps'表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='apps';")
        apps_table = cursor.fetchone()
        if apps_table:
            print("✅ 发现'apps'表")
        else:
            print("❌ 未发现'apps'表")
        
        # 检查是否有'generated_apps'表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='generated_apps';")
        generated_apps_table = cursor.fetchone()
        if generated_apps_table:
            print("✅ 发现'generated_apps'表")
        else:
            print("❌ 未发现'generated_apps'表")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查数据库时出错: {e}")
        traceback.print_exc()
        return False

def create_apps_table_if_needed():
    """如果需要，创建apps表（作为generated_apps表的别名）"""
    try:
        conn = sqlite3.connect('generated_apps.db')
        cursor = conn.cursor()
        
        # 检查是否已有apps表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='apps';")
        if not cursor.fetchone():
            print("➕ 创建apps表作为generated_apps表的视图...")
            
            # 创建视图而不是表，这样可以避免数据重复
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS apps AS 
                SELECT * FROM generated_apps
            """)
            conn.commit()
            print("✅ apps视图创建成功")
        else:
            print("✅ apps表已存在")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建apps表时出错: {e}")
        traceback.print_exc()
        return False

def check_generated_apps_table():
    """检查generated_apps表的完整性"""
    try:
        conn = sqlite3.connect('generated_apps.db')
        cursor = conn.cursor()
        
        # 检查generated_apps表结构
        cursor.execute("PRAGMA table_info(generated_apps);")
        columns = cursor.fetchall()
        print("📋 generated_apps表结构:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        # 检查是否有数据
        cursor.execute("SELECT COUNT(*) FROM generated_apps")
        count = cursor.fetchone()[0]
        print(f"📊 generated_apps表中有 {count} 条记录")
        
        if count > 0:
            cursor.execute("SELECT project_id, name, status FROM generated_apps LIMIT 3")
            records = cursor.fetchall()
            print("📋 部分记录预览:")
            for record in records:
                print(f"  - ID: {record[0]}, 名称: {record[1]}, 状态: {record[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查generated_apps表时出错: {e}")
        traceback.print_exc()
        return False

def fix_database_issues():
    """修复数据库问题"""
    print("🔧 开始修复数据库问题...")
    
    # 1. 检查数据库中的表
    print("\n1. 检查SQLite数据库...")
    check_sqlite_database()
    
    # 2. 检查generated_apps表
    print("\n2. 检查generated_apps表...")
    check_generated_apps_table()
    
    # 3. 创建apps表（如果需要）
    print("\n3. 创建apps表（如果需要）...")
    create_apps_table_if_needed()
    
    print("\n✅ 数据库修复完成")

if __name__ == "__main__":
    fix_database_issues()
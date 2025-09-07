#!/usr/bin/env python3
"""
修复generated_apps表问题的脚本
"""

import sqlite3
import json
from datetime import datetime

def check_and_fix_sqlite_db():
    """检查并修复SQLite数据库"""
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect('generated_apps.db')
        cursor = conn.cursor()
        
        print("✅ SQLite数据库连接成功")
        
        # 检查所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("📋 数据库中的所有表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查generated_apps表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='generated_apps';")
        if cursor.fetchone():
            print("✅ generated_apps表存在")
            
            # 检查表结构
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
        else:
            print("❌ generated_apps表不存在，正在创建...")
            
            # 创建generated_apps表
            cursor.execute('''CREATE TABLE IF NOT EXISTS generated_apps
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  project_id TEXT UNIQUE,
                  name TEXT,
                  app_type TEXT,
                  requirement TEXT,
                  tech_stack TEXT,
                  files_count INTEGER,
                  generated_files TEXT,
                  features TEXT,
                  complexity TEXT,
                  cloud_resources TEXT,
                  deployment_config TEXT,
                  deployment_url TEXT,
                  status TEXT,
                  cost_estimate TEXT,
                  created_at TIMESTAMP,
                  updated_at TIMESTAMP)''')
            conn.commit()
            print("✅ generated_apps表创建成功")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ SQLite数据库检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_mysql_db():
    """检查MySQL数据库"""
    try:
        # 尝试导入MySQL相关模块
        import pymysql
        from sqlalchemy import create_engine
        from app.core.config import settings
        
        print("🔍 检查MySQL数据库连接...")
        
        # 创建数据库引擎
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        connection = engine.connect()
        print("✅ MySQL数据库连接成功")
        
        # 检查所有表
        result = connection.execute("SHOW TABLES")
        tables = result.fetchall()
        print("📋 MySQL数据库中的所有表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查generated_apps表是否存在
        result = connection.execute("SHOW TABLES LIKE 'generated_apps'")
        if result.fetchone():
            print("✅ MySQL中generated_apps表存在")
            
            # 检查表结构
            result = connection.execute("DESCRIBE generated_apps")
            columns = result.fetchall()
            print("📋 MySQL generated_apps表结构:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
        else:
            print("⚠️  MySQL中generated_apps表不存在")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"⚠️  MySQL数据库检查失败: {e}")
        return False

def create_test_record():
    """创建测试记录"""
    try:
        conn = sqlite3.connect('generated_apps.db')
        cursor = conn.cursor()
        
        # 检查是否已有记录
        cursor.execute("SELECT COUNT(*) FROM generated_apps")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("➕ 创建测试记录...")
            test_project_id = "test_12345"
            cursor.execute('''INSERT OR REPLACE INTO generated_apps 
                             (project_id, name, app_type, requirement, tech_stack, files_count,
                              generated_files, features, complexity, cloud_resources, deployment_config,
                              deployment_url, status, cost_estimate, created_at, updated_at)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (test_project_id, "测试应用", "电商", "测试需求", 
                           json.dumps(["React", "FastAPI"]), 5,
                           json.dumps(["app.py", "index.html"]), 
                           json.dumps(["用户管理", "商品展示"]), 
                           "中等", json.dumps(["ECS", "RDS"]), 
                           json.dumps({"docker": True}),
                           None, "completed", "￥1,200",
                           datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
            print("✅ 测试记录创建成功")
        else:
            print("ℹ️  已有记录，无需创建测试记录")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建测试记录失败: {e}")
        return False

if __name__ == "__main__":
    print("🔧 开始修复generated_apps表问题...")
    
    print("\n1. 检查SQLite数据库...")
    check_and_fix_sqlite_db()
    
    print("\n2. 检查MySQL数据库...")
    check_mysql_db()
    
    print("\n3. 创建测试记录...")
    create_test_record()
    
    print("\n✅ 修复完成")
#!/usr/bin/env python3
"""
修复数据库错误的脚本
"""

import sqlite3
import json
from datetime import datetime

def fix_database_error():
    """修复数据库错误"""
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect('generated_apps.db')
        print("✅ SQLite数据库连接成功")
        
        # 创建游标
        cursor = conn.cursor()
        
        # 检查generated_apps表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='generated_apps';")
        if not cursor.fetchone():
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
        else:
            print("✅ generated_apps表已存在")
            
        # 检查是否有任何记录
        cursor.execute("SELECT COUNT(*) FROM generated_apps")
        count = cursor.fetchone()[0]
        print(f"📋 generated_apps表中有 {count} 条记录")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_mysql_connection():
    """检查MySQL连接配置"""
    try:
        # 导入MySQL连接相关模块
        import pymysql
        from sqlalchemy import create_engine
        
        # 从配置文件读取数据库连接信息
        # 注意：这里应该从实际的配置文件中读取
        database_url = "mysql+pymysql://scheduler:schedulerpass@localhost:3306/cloud_scheduler"
        
        # 尝试创建数据库引擎
        engine = create_engine(database_url)
        connection = engine.connect()
        print("✅ MySQL数据库连接成功")
        
        # 检查generated_apps表是否存在
        result = connection.execute("SHOW TABLES LIKE 'generated_apps'")
        if result.fetchone():
            print("✅ MySQL中generated_apps表存在")
        else:
            print("⚠️  MySQL中generated_apps表不存在")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"⚠️  MySQL连接检查失败: {e}")
        return False

if __name__ == "__main__":
    print("🔧 开始修复数据库错误...")
    fix_database_error()
    
    print("\n🔍 检查MySQL连接...")
    check_mysql_connection()
    
    print("\n✅ 修复完成")
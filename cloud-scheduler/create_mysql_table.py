#!/usr/bin/env python3
"""
在MySQL数据库中创建generated_apps表
"""

import pymysql
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def create_mysql_table():
    """在MySQL数据库中创建generated_apps表"""
    try:
        # 数据库配置
        DATABASE_CONFIG = {
            "host": "localhost",
            "port": 3306,
            "user": "scheduler",
            "password": "schedulerpass",
            "database": "cloud_scheduler"
        }
        
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=DATABASE_CONFIG["host"],
            port=DATABASE_CONFIG["port"],
            user=DATABASE_CONFIG["user"],
            password=DATABASE_CONFIG["password"]
        )
        
        cursor = connection.cursor()
        
        # 创建数据库（如果不存在）
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_CONFIG['database']}")
            print(f"✅ 数据库 {DATABASE_CONFIG['database']} 已创建或已存在")
        except Exception as e:
            print(f"⚠️  创建数据库时出错: {e}")
        
        # 选择数据库
        cursor.execute(f"USE {DATABASE_CONFIG['database']}")
        
        # 检查generated_apps表是否存在
        cursor.execute("SHOW TABLES LIKE 'generated_apps'")
        if cursor.fetchone():
            print("✅ MySQL中generated_apps表已存在")
        else:
            print("❌ MySQL中generated_apps表不存在，正在创建...")
            
            # 创建generated_apps表
            create_table_sql = """
            CREATE TABLE generated_apps (
                id INT AUTO_INCREMENT PRIMARY KEY,
                project_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(200) NOT NULL,
                app_type VARCHAR(50) NOT NULL,
                requirement TEXT NOT NULL,
                tech_stack JSON,
                files_count INT,
                generated_files JSON,
                features JSON,
                complexity VARCHAR(20),
                cloud_resources JSON,
                deployment_config JSON,
                deployment_url VARCHAR(500),
                status VARCHAR(20) DEFAULT 'completed',
                cost_estimate VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_project_id (project_id),
                INDEX idx_app_type (app_type),
                INDEX idx_created_at (created_at)
            )
            """
            
            cursor.execute(create_table_sql)
            connection.commit()
            print("✅ MySQL中generated_apps表创建成功")
        
        # 检查表结构
        cursor.execute("DESCRIBE generated_apps")
        columns = cursor.fetchall()
        print("📋 MySQL generated_apps表结构:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ MySQL数据库操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 开始在MySQL数据库中创建generated_apps表...")
    create_mysql_table()
    print("✅ 操作完成")
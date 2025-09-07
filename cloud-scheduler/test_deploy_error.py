#!/usr/bin/env python3
"""
测试部署功能并尝试重现错误
"""

import sqlite3
import json
from datetime import datetime

def test_deploy_with_error_check():
    """测试部署功能并检查错误"""
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect('generated_apps.db')
        print("✅ SQLite数据库连接成功")
        
        # 创建游标
        cursor = conn.cursor()
        
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
            
            # 查询所有记录
            cursor.execute("SELECT project_id, name, status, deployment_url FROM generated_apps")
            records = cursor.fetchall()
            
            if records:
                print(f"📋 找到 {len(records)} 条记录:")
                for record in records:
                    print(f"  - ID: {record[0]}, 名称: {record[1]}, 状态: {record[2]}, URL: {record[3]}")
                
                # 尝试更新第一条记录（模拟部署过程）
                project_id = records[0][0]
                print(f"\n🔄 尝试部署应用 {project_id}...")
                
                deployment_url = f"http://36.138.182.96:8000/projects/{project_id}"
                
                # 更新应用的部署状态和URL
                cursor.execute('''UPDATE generated_apps 
                                 SET deployment_url = ?, status = ?
                                 WHERE project_id = ?''',
                              (deployment_url, "已部署", project_id))
                conn.commit()
                
                print("✅ 部署更新成功")
                
                # 验证更新
                cursor.execute("SELECT status, deployment_url FROM generated_apps WHERE project_id = ?", (project_id,))
                updated_record = cursor.fetchone()
                if updated_record:
                    print(f"📋 更新后的状态: {updated_record[0]}, URL: {updated_record[1]}")
            else:
                print("⚠️  generated_apps表中没有记录")
                
                # 创建一条测试记录
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
                
                # 再次尝试部署
                print(f"\n🔄 尝试部署测试应用 {test_project_id}...")
                deployment_url = f"http://36.138.182.96:8000/projects/{test_project_id}"
                cursor.execute('''UPDATE generated_apps 
                                 SET deployment_url = ?, status = ?
                                 WHERE project_id = ?''',
                              (deployment_url, "已部署", test_project_id))
                conn.commit()
                print("✅ 测试应用部署更新成功")
        else:
            print("❌ generated_apps表不存在")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_deploy_with_error_check()
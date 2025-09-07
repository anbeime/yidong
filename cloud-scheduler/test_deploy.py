#!/usr/bin/env python3
"""
测试部署功能
"""

import sqlite3
import json
from datetime import datetime

def test_deploy_function():
    """测试部署功能"""
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect('generated_apps.db')
        print("✅ SQLite数据库连接成功")
        
        # 创建游标
        cursor = conn.cursor()
        
        # 检查generated_apps表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='generated_apps';")
        if cursor.fetchone():
            print("✅ generated_apps表存在")
            
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
    test_deploy_function()
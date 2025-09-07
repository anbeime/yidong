#!/usr/bin/env python3
"""
测试生成应用的历史记录功能
"""

import requests
import time
import json

# 测试数据
test_requirements = [
    "我需要一个电商网站，支持用户注册登录、商品展示、购物车、订单管理",
    "我要开发一个在线教育平台，支持课程管理、在线支付、直播授课",
    "我需要一个CRM客户管理系统，支持客户信息管理、销售跟进、数据分析"
]

def test_app_generation():
    """测试应用生成和历史记录功能"""
    base_url = "http://36.138.182.96:8000"
    
    print("🚀 开始测试生成应用的历史记录功能")
    
    # 1. 测试生成多个应用
    project_ids = []
    for i, requirement in enumerate(test_requirements):
        print(f"\n📝 测试生成第{i+1}个应用...")
        
        # 提交生成请求
        response = requests.post(
            f"{base_url}/cloudcoder/api/generate",
            json={"requirement": requirement}
        )
        
        if response.status_code == 200:
            data = response.json()
            project_id = data["project_id"]
            project_ids.append(project_id)
            print(f"✅ 成功提交生成请求，项目ID: {project_id}")
            
            # 轮询生成状态
            while True:
                status_response = requests.get(
                    f"{base_url}/cloudcoder/api/projects/{project_id}/status"
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"📊 进度: {status_data['progress']}% - {status_data['message']}")
                    
                    if status_data['status'] == 'completed':
                        print(f"🎉 应用生成完成！部署URL: {status_data.get('deployment_url', 'N/A')}")
                        break
                    elif status_data['status'] == 'error':
                        print(f"❌ 应用生成失败: {status_data['message']}")
                        break
                else:
                    print(f"⚠️ 获取状态失败: {status_response.status_code}")
                
                time.sleep(2)
        else:
            print(f"❌ 提交生成请求失败: {response.status_code}")
    
    # 2. 测试查询历史记录
    print("\n🔍 测试查询历史记录...")
    
    # 查询所有生成的应用
    response = requests.get(f"{base_url}/api/v1/generated-apps")
    if response.status_code == 200:
        apps = response.json()
        print(f"✅ 成功获取到 {len(apps)} 个历史记录")
        
        for app in apps:
            print(f"  - {app['name']} ({app['type']}) - {app['created_at']}")
            print(f"    URL: {app['url']}")
    else:
        print(f"❌ 查询历史记录失败: {response.status_code}")
    
    # 查询特定应用详情
    if project_ids:
        print(f"\n📄 测试查询特定应用详情...")
        project_id = project_ids[0]
        response = requests.get(f"{base_url}/api/v1/generated-apps/{project_id}")
        if response.status_code == 200:
            app = response.json()
            print(f"✅ 成功获取应用详情:")
            print(f"  名称: {app['name']}")
            print(f"  类型: {app['type']}")
            print(f"  URL: {app['url']}")
            print(f"  技术栈: {', '.join(app['tech_stack'])}")
        else:
            print(f"❌ 查询应用详情失败: {response.status_code}")

if __name__ == "__main__":
    test_app_generation()
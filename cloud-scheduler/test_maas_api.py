#!/usr/bin/env python3
"""
测试MaaS API调用
"""

import requests
from typing import Any, Dict

# API 配置常量
user_api_key = 'lRe8U_TZdIZFxfuBio-dJtsBIXwuMBMMumRA3ybMfzE'
user_agent_id = 'agent_1414239986664374272'
base_url = "https://zhenze-huhehaote.cmecloud.cn"

def test_maas_api() -> None:
    """测试MaaS API调用"""
    print("开始测试MaaS API调用...")
    
    # 构建请求URL
    api_endpoint = f"{base_url}/api/maas/agent/{user_agent_id}"
    
    # 请求头配置
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',  # 非流式为application/json
        'Authorization': f'Bearer {user_api_key}'
    }
    
    payload: Dict[str, Any] = {
        "query": "你好,你是谁？",
        "stream": False,  # 非流式为False
    }
    
    try:
        response = requests.post(
            api_endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # 检查HTTP状态码
        if response.status_code != 200:
            print(f"HTTP错误: {response.status_code} {response.reason}")
            
            # 打印原始响应内容
            content = response.content.decode('utf-8')
            print(f"原始响应内容: \n{content}")
            return
        
        # 处理成功的响应
        print("API调用成功!")
        print(f"响应状态码: {response.status_code}")
        
        # 尝试解析JSON响应
        try:
            result = response.json()
            print(f"响应内容: {result}")
        except Exception as e:
            print(f"响应不是JSON格式: {e}")
            print(f"响应文本: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_maas_api()
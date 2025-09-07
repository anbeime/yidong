#!/usr/bin/env python3
"""
测试移动云配置是否正确
"""

import os
from backend.app.core.config import settings

def test_ecloud_config():
    """测试移动云配置"""
    print("🔍 测试移动云配置...")
    
    # 从环境变量获取
    access_key_env = os.getenv('ECLOUD_ACCESS_KEY')
    secret_key_env = os.getenv('ECLOUD_SECRET_KEY')
    
    # 从配置文件获取
    access_key_config = settings.ECLOUD_ACCESS_KEY
    secret_key_config = settings.ECLOUD_SECRET_KEY
    region_config = settings.ECLOUD_REGION
    
    print(f"环境变量中的认证信息:")
    print(f"  ECLOUD_ACCESS_KEY: {access_key_env}")
    print(f"  ECLOUD_SECRET_KEY: {secret_key_env[:6] if secret_key_env else None}...{secret_key_env[-4:] if secret_key_env else None}")
    
    print(f"\n配置文件中的认证信息:")
    print(f"  ECLOUD_ACCESS_KEY: {access_key_config}")
    print(f"  ECLOUD_SECRET_KEY: {secret_key_config[:6] if secret_key_config else None}...{secret_key_config[-4:] if secret_key_config else None}")
    print(f"  ECLOUD_REGION: {region_config}")
    
    # 验证配置是否一致
    if access_key_env == access_key_config and secret_key_env == secret_key_config:
        print("\n✅ 环境变量和配置文件中的认证信息一致")
    else:
        print("\n⚠️  环境变量和配置文件中的认证信息不一致")
    
    # 验证是否为实际的认证信息
    if access_key_config == "ed7bbd03fad34980834cae597a02cbfc" and secret_key_config == "9ae0582e1e9e4f40ab5c68b744829c61":
        print("✅ 使用了正确的移动云认证信息")
    else:
        print("⚠️  未使用预期的移动云认证信息")
        
    if region_config == "cn-north-1":
        print("✅ 使用了正确的区域配置")
    else:
        print("⚠️  区域配置可能不正确")

# 添加移动云API Key使用示例
import requests
from typing import Any, Dict

def test_maas_api():
    """测试移动云MaaS API"""
    # 使用您创建的API Key
    user_api_key = 'lRe8U_TZdIZFxfuBio-dJtsBIXwuMBMMumRA3ybMfzE'
    user_agent_id = '<YOUR_AGENT_ID>'  # 请替换为您的Agent ID
    base_url = "https://zhenze-huhehaote.cmecloud.cn"

    def stream_agent_response() -> None:
        """流式请求Agent API并处理响应"""
        # 构建请求URL
        api_endpoint = f"{base_url}/api/maas/agent/{user_agent_id}"

        # 请求头配置
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
            'Authorization': f'Bearer {user_api_key}'
        }

        # 请求体参数
        payload: Dict[str, Any] = {
            "chatId": "",  # 首次对话可不传此参数
            "query": "你好",  # 用户输入内容
            "stream": True,  # 强制使用流式传输
        }

        try:
            # 发送流式POST请求
            with requests.post(
                    api_endpoint,
                    headers=headers,
                    json=payload,
                    stream=True
            ) as response:
                response.raise_for_status()  # 检查HTTP错误
                print(f"响应状态码: {response.status_code}")
                
                # 处理流式响应
                for raw_line in response.iter_lines():
                    # 过滤保持连接的空行
                    if raw_line:
                        decoded_line = raw_line.decode('utf-8')
                        print(f"收到事件: {decoded_line}")

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP错误: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"请求异常: {req_err}")
        except UnicodeDecodeError as decode_err:
            print(f"响应解码失败: {decode_err}")
        except Exception as unexpected_err:
            print(f"未预期错误: {unexpected_err}")

    # 调用函数
    stream_agent_response()

if __name__ == "__main__":
    test_ecloud_config()
    print("\n" + "="*50)
    print("测试移动云MaaS API:")
    test_maas_api()
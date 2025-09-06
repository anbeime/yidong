#!/usr/bin/env python3
"""
简单测试移动云配置
"""

import os

def test_ecloud_config():
    """测试移动云配置"""
    print("🔍 测试移动云配置...")
    
    # 从环境变量获取
    access_key_env = os.getenv('ECLOUD_ACCESS_KEY')
    secret_key_env = os.getenv('ECLOUD_SECRET_KEY')
    region_env = os.getenv('ECLOUD_REGION')
    
    print(f"环境变量中的认证信息:")
    print(f"  ECLOUD_ACCESS_KEY: {access_key_env}")
    print(f"  ECLOUD_SECRET_KEY: {secret_key_env[:6] if secret_key_env else None}...{secret_key_env[-4:] if secret_key_env else None}")
    print(f"  ECLOUD_REGION: {region_env}")
    
    # 验证是否为实际的认证信息
    if access_key_env == "ed7bbd03fad34980834cae597a02cbfc" and secret_key_env == "9ae0582e1e9e4f40ab5c68b744829c61":
        print("\n✅ 环境变量中的移动云认证信息配置正确")
    else:
        print("\n⚠️  环境变量中的移动云认证信息配置不正确")
        
    if region_env == "cn-north-1":
        print("✅ 区域配置正确")
    else:
        print("⚠️  区域配置可能不正确")

if __name__ == "__main__":
    test_ecloud_config()
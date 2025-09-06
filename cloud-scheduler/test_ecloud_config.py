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

if __name__ == "__main__":
    test_ecloud_config()
#!/usr/bin/env python3
"""
增强版演示脚本 - 展示移动云集成功能
"""

import os
import asyncio
from real_ecloud_api import CloudCoderEcloudIntegration
from ecloud_orchestrator import EcloudOrchestrator

async def demo_ecloud_integration():
    """演示移动云集成功能"""
    print("🚀 启动移动云集成演示...")
    
    # 从环境变量获取认证信息
    access_key = os.getenv('ECLOUD_ACCESS_KEY', 'ed7bbd03fad34980834cae597a02cbfc')
    secret_key = os.getenv('ECLOUD_SECRET_KEY', '9ae0582e1e9e4f40ab5c68b744829c61')
    
    print(f"🔑 使用的认证信息:")
    print(f"   Access Key: {access_key}")
    print(f"   Secret Key: {secret_key[:6]}...{secret_key[-4:]}")
    
    # 初始化移动云集成
    ecloud_integration = CloudCoderEcloudIntegration(access_key, secret_key)
    
    # 示例云配置
    cloud_config = {
        'vpc_config': {
            'name': 'demo-vpc',
            'cidr': '10.0.0.0/16',
            'subnets': [
                {'name': 'public', 'cidr': '10.0.1.0/24'},
                {'name': 'private', 'cidr': '10.0.2.0/24'}
            ]
        },
        'ecs_instances': [
            {
                'name': 'web-server',
                'type': 'ecs.c6.large',
                'cpu': 2,
                'memory': 4,
                'purpose': 'Web服务器'
            },
            {
                'name': 'api-server',
                'type': 'ecs.c6.xlarge',
                'cpu': 4,
                'memory': 8,
                'purpose': 'API服务器'
            }
        ],
        'rds_instance': {
            'name': 'mysql-db',
            'engine': 'MySQL',
            'version': '8.0',
            'cpu': 2,
            'memory': 4,
            'storage': 100
        },
        'redis_instance': {
            'name': 'redis-cache',
            'memory': 2,
            'purpose': '缓存'
        },
        'oss_bucket': {
            'name': 'demo-storage',
            'purpose': '静态文件存储'
        }
    }
    
    print("\n📋 云资源配置:")
    print(f"   VPC网络: {cloud_config['vpc_config']['name']}")
    print(f"   ECS实例: {len(cloud_config['ecs_instances'])}个")
    print(f"   RDS数据库: {cloud_config['rds_instance']['name']}")
    print(f"   Redis缓存: {cloud_config['redis_instance']['name']}")
    print(f"   OSS存储: {cloud_config['oss_bucket']['name']}")
    
    # 创建项目基础设施
    print("\n🏗️ 正在创建云基础设施...")
    result = await ecloud_integration.create_project_infrastructure('demo_project', cloud_config)
    
    if result['success']:
        print("✅ 云基础设施创建成功!")
        print(f"   项目ID: {result['project_id']}")
        print(f"   创建资源数: {len(result['resources'])}")
        print(f"   总成本估算: ¥{result['total_cost']:.2f}/月")
        
        # 显示创建的资源
        print("\n📊 创建的资源:")
        for resource in result['resources']:
            print(f"   - {resource['type']}: {resource['id']} (状态: {resource['status']}, 成本: ¥{resource['cost']:.2f}/月)")
    else:
        print(f"❌ 创建失败: {result['error']}")
    
    # 成本估算
    print("\n💰 成本估算:")
    cost_estimate = ecloud_integration.estimate_project_cost(cloud_config)
    print(f"   月度总成本: ¥{cost_estimate['total_monthly_cost']:.2f}")
    print("   成本明细:")
    for resource_type, cost in cost_estimate['cost_breakdown'].items():
        print(f"     - {resource_type}: ¥{cost:.2f}/月")
    
    # 优化建议
    print("\n💡 成本优化建议:")
    for suggestion in cost_estimate['optimization_suggestions']:
        print(f"   - {suggestion}")

async def demo_resource_orchestration():
    """演示资源编排功能"""
    print("\n\n🤖 启动资源编排演示...")
    
    # 初始化编排器
    orchestrator = EcloudOrchestrator()
    
    # 云配置
    cloud_config = {
        "vpc_config": {
            "name": "orchestration-vpc",
            "cidr": "10.0.0.0/16",
            "subnets": [
                {"name": "public", "cidr": "10.0.1.0/24"},
                {"name": "private", "cidr": "10.0.2.0/24"}
            ]
        },
        "ecs_instances": [
            {
                "name": "web-server",
                "type": "ecs.c6.large",
                "cpu": 2,
                "memory": 4,
                "purpose": "Web服务器"
            }
        ],
        "rds_instance": {
            "name": "app-db",
            "engine": "MySQL",
            "version": "8.0",
            "cpu": 2,
            "memory": 4,
            "storage": 100
        }
    }
    
    print("📋 规划基础设施...")
    infrastructure = await orchestrator.plan_infrastructure(cloud_config, "orchestration_demo")
    print(f"✅ 基础设施规划完成，预估月成本: ¥{infrastructure.total_cost_estimate:.2f}")
    
    print("\n🏗️ 部署基础设施...")
    deployment_result = await orchestrator.deploy_infrastructure(infrastructure)
    
    if deployment_result['status'] == 'completed':
        print("✅ 基础设施部署完成!")
        print(f"   部署进度: {deployment_result['progress']}%")
        print(f"   创建资源数: {len(deployment_result['resources'])}")
        
        # 显示部署的资源
        print("\n📊 部署的资源:")
        for resource_type, resource in deployment_result['resources'].items():
            if isinstance(resource, dict) and 'VpcId' in resource:
                print(f"   - VPC: {resource['VpcId']} (状态: {resource['Status']})")
            elif isinstance(resource, dict) and 'InstanceId' in resource:
                print(f"   - ECS: {resource['InstanceId']} (状态: {resource['Status']})")
            elif isinstance(resource, dict) and 'DBInstanceId' in resource:
                print(f"   - RDS: {resource['DBInstanceId']} (状态: {resource['Status']})")
    else:
        print(f"❌ 部署失败: {deployment_result.get('error', '未知错误')}")

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    required_vars = ['ECLOUD_ACCESS_KEY', 'ECLOUD_SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # 显示变量值（部分隐藏敏感信息）
            if var == 'ECLOUD_ACCESS_KEY':
                print(f"   ✅ {var}: {value}")
            elif var == 'ECLOUD_SECRET_KEY':
                print(f"   ✅ {var}: {value[:6]}...{value[-4:]}")
    
    if missing_vars:
        print(f"   ❌ 缺少环境变量: {', '.join(missing_vars)}")
        return False
    else:
        print("   ✅ 所有必需的环境变量已配置")
        return True

async def main():
    """主函数"""
    print("🌟 CloudCoder 移动云集成演示")
    print("=" * 50)
    
    # 检查环境配置
    if not check_environment():
        print("\n⚠️  请先配置环境变量:")
        print("   export ECLOUD_ACCESS_KEY=ed7bbd03fad34980834cae597a02cbfc")
        print("   export ECLOUD_SECRET_KEY=9ae0582e1e9e4f40ab5c68b744829c61")
        return
    
    # 运行演示
    await demo_ecloud_integration()
    await demo_resource_orchestration()
    
    print("\n🎉 演示完成!")

if __name__ == "__main__":
    asyncio.run(main())
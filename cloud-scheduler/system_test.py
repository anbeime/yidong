#!/usr/bin/env python3
"""
CloudCoder 系统测试和验证模块（简化版）
全面测试所有功能的完整性和稳定性
"""

import os
import json
import time
import asyncio
import tempfile
import shutil
from typing import Dict, List, Optional
from datetime import datetime

class CloudCoderTester:
    """CloudCoder系统测试器"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir: Optional[str] = None
    
    def setup_test_env(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp(prefix='cloudcoder_test_')
        print(f"✅ 测试环境设置完成: {self.temp_dir}")
    
    def cleanup_test_env(self):
        """清理测试环境"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
        print("✅ 测试环境清理完成")
    
    def run_test(self, test_name: str, test_func):
        """运行单个测试"""
        try:
            start_time = time.time()
            test_func()
            execution_time = time.time() - start_time
            
            self.test_results.append({
                'name': test_name,
                'status': 'PASSED',
                'time': execution_time,
                'details': '测试通过'
            })
            print(f"✅ {test_name} - 通过 ({execution_time:.2f}s)")
            
        except Exception as e:
            self.test_results.append({
                'name': test_name,
                'status': 'FAILED',
                'time': 0,
                'details': str(e)
            })
            print(f"❌ {test_name} - 失败: {str(e)}")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始CloudCoder系统测试...\n")
        
        self.setup_test_env()
        
        try:
            # 基础功能测试
            self.run_test("代码生成器基础功能", self.test_code_generator)
            self.run_test("移动云API集成", self.test_ecloud_api)
            self.run_test("用户认证系统", self.test_user_auth)
            self.run_test("项目存储功能", self.test_project_storage)
            self.run_test("版本管理功能", self.test_version_management)
            self.run_test("资源管理功能", self.test_resource_management)
            
            # 集成测试
            await self.run_async_test("端到端集成测试", self.test_e2e_integration)
            
        finally:
            self.cleanup_test_env()
        
        self.print_summary()
    
    async def run_async_test(self, test_name: str, test_func):
        """运行异步测试"""
        try:
            start_time = time.time()
            await test_func()
            execution_time = time.time() - start_time
            
            self.test_results.append({
                'name': test_name,
                'status': 'PASSED',
                'time': execution_time,
                'details': '异步测试通过'
            })
            print(f"✅ {test_name} - 通过 ({execution_time:.2f}s)")
            
        except Exception as e:
            self.test_results.append({
                'name': test_name,
                'status': 'FAILED',
                'time': 0,
                'details': str(e)
            })
            print(f"❌ {test_name} - 失败: {str(e)}")
    
    def test_code_generator(self):
        """测试代码生成器"""
        # 模拟代码生成测试
        from enhanced_code_generator import EnhancedCodeGenerator
        
        if not self.temp_dir:
            raise ValueError("测试环境未初始化")
        
        generator = EnhancedCodeGenerator(os.path.join(self.temp_dir, 'projects'))
        project = generator.generate_complete_application(
            "电商平台，支持用户注册、商品管理",
            "ecommerce"
        )
        
        assert project is not None, "项目生成失败"
        assert len(project.files) > 0, "没有生成文件"
        assert 'frontend/src/App.tsx' in project.files, "缺少React文件"
        assert 'backend/main.py' in project.files, "缺少后端文件"
    
    def test_ecloud_api(self):
        """测试移动云API"""
        from real_ecloud_api import CloudCoderEcloudIntegration
        
        integration = CloudCoderEcloudIntegration()
        
        # 测试成本估算
        config = {
            'ecs_instances': [{'name': 'web', 'type': 'ecs.c6.large'}],
            'rds_instance': {'name': 'db', 'engine': 'MySQL', 'cpu': 2, 'memory': 4, 'storage': 100}
        }
        
        cost = integration.estimate_project_cost(config)
        assert 'total_monthly_cost' in cost, "缺少成本信息"
        assert cost['total_monthly_cost'] > 0, "成本应该大于0"
    
    def test_user_auth(self):
        """测试用户认证"""
        from user_auth_storage import DatabaseManager, UserAuthManager
        
        if not self.temp_dir:
            raise ValueError("测试环境未初始化")
        
        db_path = os.path.join(self.temp_dir, 'test.db')
        db = DatabaseManager(db_path)
        auth = UserAuthManager(db)
        
        # 测试注册
        result = auth.register_user("testuser", "test@example.com", "password123")
        assert result['success'], f"注册失败: {result.get('error')}"
        
        # 测试登录
        login = auth.login_user("testuser", "password123")
        assert login['success'], f"登录失败: {login.get('error')}"
        
        # 测试会话验证
        session_id = login['session']['session_id']
        session = auth.verify_session(session_id)
        assert session is not None, "会话验证失败"
    
    def test_project_storage(self):
        """测试项目存储"""
        from user_auth_storage import DatabaseManager, ProjectStorageManager
        
        if not self.temp_dir:
            raise ValueError("测试环境未初始化")
        
        db_path = os.path.join(self.temp_dir, 'test.db')
        db = DatabaseManager(db_path)
        storage = ProjectStorageManager(db)
        
        # 测试项目保存
        project_data = {
            'name': '测试项目',
            'app_type': 'ecommerce',
            'requirement': '电商网站',
            'files': {'main.py': 'print("test")'},
            'metadata': {'version': '1.0.0'}
        }
        
        result = storage.save_project('test_user', project_data)
        assert result['success'], f"保存失败: {result.get('error')}"
        
        # 测试获取项目
        projects = storage.get_user_projects('test_user')
        assert len(projects) > 0, "没有找到项目"
        assert projects[0]['name'] == '测试项目', "项目名称不匹配"
    
    def test_version_management(self):
        """测试版本管理"""
        from project_version_manager import ProjectVersionManager
        
        if not self.temp_dir:
            raise ValueError("测试环境未初始化")
        
        version_dir = os.path.join(self.temp_dir, 'versions')
        vm = ProjectVersionManager(version_dir)
        
        # 测试创建初始版本
        project_data = {
            'app_type': 'ecommerce',
            'files': {'main.py': 'print("v1")'},
            'requirement': '电商网站'
        }
        
        version = vm.create_initial_version('test_project', project_data)
        assert version.version_number == "1.0.0", "版本号不正确"
        
        # 测试获取历史
        history = vm.get_project_history('test_project')
        assert history['total_versions'] == 1, "版本数量不正确"
    
    def test_resource_management(self):
        """测试资源管理"""
        from user_auth_storage import DatabaseManager
        from cloud_resource_manager import CloudResourceManager
        
        if not self.temp_dir:
            raise ValueError("测试环境未初始化")
        
        db_path = os.path.join(self.temp_dir, 'test.db')
        db = DatabaseManager(db_path)
        rm = CloudResourceManager(db)
        
        # 验证管理器初始化成功
        assert rm.db is not None, "数据库连接失败"
        assert rm.ecloud_integration is not None, "移动云集成失败"
    
    async def test_e2e_integration(self):
        """端到端集成测试"""
        # 完整流程：注册用户 -> 生成项目 -> 保存 -> 估算成本
        from user_auth_storage import DatabaseManager, UserAuthManager, ProjectStorageManager
        from enhanced_code_generator import EnhancedCodeGenerator
        from real_ecloud_api import CloudCoderEcloudIntegration
        
        if not self.temp_dir:
            raise ValueError("测试环境未初始化")
        
        # 初始化组件
        db_path = os.path.join(self.temp_dir, 'e2e_test.db')
        db = DatabaseManager(db_path)
        auth = UserAuthManager(db)
        storage = ProjectStorageManager(db)
        generator = EnhancedCodeGenerator(os.path.join(self.temp_dir, 'e2e_projects'))
        integration = CloudCoderEcloudIntegration()
        
        # 1. 用户注册
        register_result = auth.register_user("e2euser", "e2e@test.com", "password123")
        assert register_result['success'], "E2E用户注册失败"
        user_id = register_result['user_id']
        
        # 2. 生成项目
        project = generator.generate_complete_application(
            "在线教育平台，支持课程管理",
            "education"
        )
        assert project is not None, "E2E项目生成失败"
        
        # 3. 保存项目
        project_data = {
            'name': project.name,
            'app_type': project.app_type,
            'requirement': project.description,
            'files': project.files,
            'metadata': {'tech_stack': project.tech_stack}
        }
        save_result = storage.save_project(user_id, project_data)
        assert save_result['success'], "E2E项目保存失败"
        
        # 4. 成本估算
        cost = integration.estimate_project_cost(project.cloud_config)
        assert 'total_monthly_cost' in cost, "E2E成本估算失败"
        
        print(f"E2E测试完成: 用户{user_id}, 项目{save_result['project_id']}, 成本¥{cost['total_monthly_cost']}")
    
    def print_summary(self):
        """打印测试摘要"""
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASSED'])
        failed = len([r for r in self.test_results if r['status'] == 'FAILED'])
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*50)
        print("📊 CloudCoder 测试报告")
        print("="*50)
        print(f"总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"成功率: {success_rate:.1f}%")
        
        if failed > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if result['status'] == 'FAILED':
                    print(f"  - {result['name']}: {result['details']}")
        
        print("\n" + "="*50)
        
        if success_rate >= 90:
            print("🎉 测试结果：优秀！系统已准备就绪。")
        elif success_rate >= 80:
            print("✅ 测试结果：良好！")
        elif success_rate >= 70:
            print("⚠️ 测试结果：尚可，需要改进。")
        else:
            print("❌ 测试结果：需要重大改进！")
        
        # 保存测试报告
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total': total,
                    'passed': passed,
                    'failed': failed,
                    'success_rate': success_rate
                },
                'details': self.test_results,
                'timestamp': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        print(f"📄 测试报告已保存: {report_file}")

# 主函数
async def main():
    """运行完整测试"""
    tester = CloudCoderTester()
    await tester.run_all_tests()
    
    # 返回测试成功状态
    passed = len([r for r in tester.test_results if r['status'] == 'PASSED'])
    total = len(tester.test_results)
    return (passed / total) >= 0.8 if total > 0 else False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
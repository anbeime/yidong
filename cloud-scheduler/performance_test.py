#!/usr/bin/env python3
"""
CloudCoder 性能测试和负载测试模块
测试系统在高负载下的稳定性和性能表现
"""

import asyncio
import concurrent.futures
import json
import time
import psutil
import threading
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import statistics
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {
            "cpu_usage": [],
            "memory_usage": [],
            "response_times": [],
            "error_count": 0,
            "success_count": 0,
            "concurrent_users": 0
        }
        self.monitoring = False
    
    def start_monitoring(self):
        """开始监控系统性能"""
        self.monitoring = True
        thread = threading.Thread(target=self._monitor_system)
        thread.daemon = True
        thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
    
    def _monitor_system(self):
        """监控系统资源使用情况"""
        while self.monitoring:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics["cpu_usage"].append({
                "timestamp": datetime.now().isoformat(),
                "value": cpu_percent
            })
            
            # 内存使用率
            memory = psutil.virtual_memory()
            self.metrics["memory_usage"].append({
                "timestamp": datetime.now().isoformat(),
                "value": memory.percent
            })
            
            time.sleep(1)
    
    def record_response_time(self, response_time: float):
        """记录响应时间"""
        self.metrics["response_times"].append({
            "timestamp": datetime.now().isoformat(),
            "value": response_time
        })
    
    def record_success(self):
        """记录成功请求"""
        self.metrics["success_count"] += 1
    
    def record_error(self):
        """记录失败请求"""
        self.metrics["error_count"] += 1
    
    def set_concurrent_users(self, count: int):
        """设置并发用户数"""
        self.metrics["concurrent_users"] = count
    
    def get_summary_report(self) -> Dict[str, Any]:
        """生成性能摘要报告"""
        response_times = [rt["value"] for rt in self.metrics["response_times"]]
        cpu_usage = [cpu["value"] for cpu in self.metrics["cpu_usage"]]
        memory_usage = [mem["value"] for mem in self.metrics["memory_usage"]]
        
        total_requests = self.metrics["success_count"] + self.metrics["error_count"]
        success_rate = (self.metrics["success_count"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "summary": {
                "total_requests": total_requests,
                "successful_requests": self.metrics["success_count"],
                "failed_requests": self.metrics["error_count"],
                "success_rate": f"{success_rate:.2f}%",
                "max_concurrent_users": self.metrics["concurrent_users"]
            },
            "response_time_stats": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "average": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "p95": statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else 0,
                "p99": statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else 0
            },
            "system_resource_stats": {
                "cpu_usage": {
                    "min": min(cpu_usage) if cpu_usage else 0,
                    "max": max(cpu_usage) if cpu_usage else 0,
                    "average": statistics.mean(cpu_usage) if cpu_usage else 0
                },
                "memory_usage": {
                    "min": min(memory_usage) if memory_usage else 0,
                    "max": max(memory_usage) if memory_usage else 0,
                    "average": statistics.mean(memory_usage) if memory_usage else 0
                }
            }
        }

class LoadTester:
    """负载测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8084"):
        self.base_url = base_url
        self.monitor = PerformanceMonitor()
    
    async def single_request_test(self, endpoint: str, method: str = "GET", 
                                 data: Optional[Dict] = None) -> Dict[str, Any]:
        """单个请求测试"""
        start_time = time.time()
        
        try:
            if method.upper() == "POST":
                response = requests.post(f"{self.base_url}{endpoint}", 
                                       json=data, timeout=30)
            else:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=30)
            
            response_time = time.time() - start_time
            self.monitor.record_response_time(response_time)
            
            if response.status_code == 200:
                self.monitor.record_success()
                return {
                    "success": True,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "response_size": len(response.content)
                }
            else:
                self.monitor.record_error()
                return {
                    "success": False,
                    "response_time": response_time,
                    "status_code": response.status_code,
                    "error": "HTTP Error"
                }
        
        except Exception as e:
            response_time = time.time() - start_time
            self.monitor.record_response_time(response_time)
            self.monitor.record_error()
            return {
                "success": False,
                "response_time": response_time,
                "error": str(e)
            }
    
    async def concurrent_user_test(self, concurrent_users: int, 
                                  requests_per_user: int,
                                  endpoint: str = "/") -> Dict[str, Any]:
        """并发用户测试"""
        logger.info(f"开始并发测试: {concurrent_users}个用户，每用户{requests_per_user}个请求")
        
        self.monitor.set_concurrent_users(concurrent_users)
        self.monitor.start_monitoring()
        
        async def user_session():
            """模拟单个用户会话"""
            for _ in range(requests_per_user):
                await self.single_request_test(endpoint)
                await asyncio.sleep(0.1)  # 用户思考时间
        
        # 创建并发任务
        tasks = [user_session() for _ in range(concurrent_users)]
        
        start_time = time.time()
        await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        self.monitor.stop_monitoring()
        
        # 生成报告
        report = self.monitor.get_summary_report()
        report["test_info"] = {
            "concurrent_users": concurrent_users,
            "requests_per_user": requests_per_user,
            "total_time": total_time,
            "requests_per_second": report["summary"]["total_requests"] / total_time
        }
        
        return report
    
    async def stress_test(self, max_users: int = 100, step: int = 10, 
                         duration_per_step: int = 30) -> Dict[str, Any]:
        """压力测试 - 逐步增加负载"""
        logger.info(f"开始压力测试: 最大{max_users}用户，步长{step}，每步{duration_per_step}秒")
        
        stress_results = []
        
        for user_count in range(step, max_users + 1, step):
            logger.info(f"测试负载: {user_count}个并发用户")
            
            # 运行负载测试
            result = await self.concurrent_user_test(
                concurrent_users=user_count,
                requests_per_user=duration_per_step // 2  # 每2秒一个请求
            )
            
            stress_results.append({
                "concurrent_users": user_count,
                "response_time_avg": result["response_time_stats"]["average"],
                "success_rate": result["summary"]["success_rate"],
                "cpu_usage_avg": result["system_resource_stats"]["cpu_usage"]["average"],
                "memory_usage_avg": result["system_resource_stats"]["memory_usage"]["average"]
            })
            
            # 检查是否达到性能瓶颈
            if float(result["summary"]["success_rate"].replace('%', '')) < 95:
                logger.warning(f"成功率低于95%，停止压力测试")
                break
            
            # 等待系统恢复
            await asyncio.sleep(5)
        
        return {
            "stress_test_results": stress_results,
            "performance_bottleneck": self._analyze_bottleneck(stress_results)
        }
    
    def _analyze_bottleneck(self, results: List[Dict]) -> Dict[str, Any]:
        """分析性能瓶颈"""
        if not results:
            return {"analysis": "无足够数据分析"}
        
        # 寻找性能拐点
        response_times = [r["response_time_avg"] for r in results]
        cpu_usage = [r["cpu_usage_avg"] for r in results]
        memory_usage = [r["memory_usage_avg"] for r in results]
        
        analysis = {
            "max_stable_users": 0,
            "bottleneck_type": "unknown",
            "recommendations": []
        }
        
        # 查找响应时间急剧增加的点
        for i in range(1, len(response_times)):
            if response_times[i] > response_times[i-1] * 2:  # 响应时间翻倍
                analysis["max_stable_users"] = results[i-1]["concurrent_users"]
                break
        
        # 分析瓶颈类型
        if max(cpu_usage) > 80:
            analysis["bottleneck_type"] = "CPU密集型"
            analysis["recommendations"].append("考虑增加CPU核心数或优化算法")
        
        if max(memory_usage) > 80:
            analysis["bottleneck_type"] = "内存密集型"
            analysis["recommendations"].append("考虑增加内存或优化内存使用")
        
        if analysis["bottleneck_type"] == "unknown":
            analysis["bottleneck_type"] = "I/O或网络瓶颈"
            analysis["recommendations"].append("检查数据库连接池和网络配置")
        
        return analysis

class CloudCoderPerformanceTester:
    """CloudCoder专用性能测试器"""
    
    def __init__(self):
        self.load_tester = LoadTester()
    
    async def test_code_generation_performance(self) -> Dict[str, Any]:
        """测试代码生成功能的性能"""
        logger.info("开始测试代码生成性能...")
        
        test_data = {
            "requirement": "创建一个简单的博客系统，包含文章管理和用户评论功能",
            "app_type": "default"
        }
        
        # 单用户性能测试
        single_result = await self.load_tester.single_request_test(
            "/generate", "POST", test_data
        )
        
        # 并发测试
        concurrent_result = await self.load_tester.concurrent_user_test(
            concurrent_users=5,
            requests_per_user=2,
            endpoint="/generate"
        )
        
        return {
            "single_user_performance": single_result,
            "concurrent_performance": concurrent_result,
            "test_type": "code_generation"
        }
    
    async def test_cloud_api_performance(self) -> Dict[str, Any]:
        """测试移动云API调用性能"""
        logger.info("开始测试移动云API性能...")
        
        test_data = {
            "app_type": "ecommerce",
            "expected_users": 1000
        }
        
        # API调用性能测试
        result = await self.load_tester.concurrent_user_test(
            concurrent_users=10,
            requests_per_user=3,
            endpoint="/api/cloud/estimate"
        )
        
        return {
            "cloud_api_performance": result,
            "test_type": "cloud_api"
        }
    
    async def run_full_performance_suite(self) -> Dict[str, Any]:
        """运行完整的性能测试套件"""
        logger.info("开始运行完整性能测试套件...")
        
        results = {
            "test_start_time": datetime.now().isoformat(),
            "test_results": {}
        }
        
        try:
            # 1. 基础负载测试
            logger.info("1. 执行基础负载测试...")
            basic_load = await self.load_tester.concurrent_user_test(
                concurrent_users=20,
                requests_per_user=5
            )
            results["test_results"]["basic_load_test"] = basic_load
            
            # 2. 代码生成性能测试
            logger.info("2. 执行代码生成性能测试...")
            code_gen_perf = await self.test_code_generation_performance()
            results["test_results"]["code_generation_performance"] = code_gen_perf
            
            # 3. 云API性能测试
            logger.info("3. 执行云API性能测试...")
            cloud_api_perf = await self.test_cloud_api_performance()
            results["test_results"]["cloud_api_performance"] = cloud_api_perf
            
            # 4. 压力测试
            logger.info("4. 执行压力测试...")
            stress_test = await self.load_tester.stress_test(
                max_users=50,
                step=10,
                duration_per_step=20
            )
            results["test_results"]["stress_test"] = stress_test
            
            results["test_end_time"] = datetime.now().isoformat()
            results["test_status"] = "completed"
            
            # 生成性能评估报告
            results["performance_assessment"] = self._generate_assessment(results["test_results"])
            
        except Exception as e:
            results["test_end_time"] = datetime.now().isoformat()
            results["test_status"] = "failed"
            results["error"] = str(e)
            logger.error(f"性能测试失败: {e}")
        
        return results
    
    def _generate_assessment(self, test_results: Dict) -> Dict[str, Any]:
        """生成性能评估报告"""
        assessment = {
            "overall_score": 0,
            "performance_grade": "未知",
            "key_metrics": {},
            "recommendations": []
        }
        
        try:
            # 基础负载测试评估
            basic_load = test_results.get("basic_load_test", {})
            success_rate = float(basic_load.get("summary", {}).get("success_rate", "0%").replace('%', ''))
            avg_response_time = basic_load.get("response_time_stats", {}).get("average", 999)
            
            # 计算分数
            score = 0
            if success_rate >= 99:
                score += 30
            elif success_rate >= 95:
                score += 20
            elif success_rate >= 90:
                score += 10
            
            if avg_response_time <= 1.0:
                score += 30
            elif avg_response_time <= 3.0:
                score += 20
            elif avg_response_time <= 5.0:
                score += 10
            
            # 压力测试评估
            stress_test = test_results.get("stress_test", {})
            max_users = stress_test.get("performance_bottleneck", {}).get("max_stable_users", 0)
            
            if max_users >= 40:
                score += 30
            elif max_users >= 20:
                score += 20
            elif max_users >= 10:
                score += 10
            
            # 系统资源评估
            cpu_avg = basic_load.get("system_resource_stats", {}).get("cpu_usage", {}).get("average", 100)
            memory_avg = basic_load.get("system_resource_stats", {}).get("memory_usage", {}).get("average", 100)
            
            if cpu_avg <= 60 and memory_avg <= 70:
                score += 10
            elif cpu_avg <= 80 and memory_avg <= 85:
                score += 5
            
            assessment["overall_score"] = min(score, 100)
            
            # 性能等级
            if score >= 90:
                assessment["performance_grade"] = "优秀"
            elif score >= 70:
                assessment["performance_grade"] = "良好"
            elif score >= 50:
                assessment["performance_grade"] = "一般"
            else:
                assessment["performance_grade"] = "需要优化"
            
            # 关键指标
            assessment["key_metrics"] = {
                "success_rate": f"{success_rate}%",
                "average_response_time": f"{avg_response_time:.2f}s",
                "max_concurrent_users": max_users,
                "cpu_usage_avg": f"{cpu_avg:.1f}%",
                "memory_usage_avg": f"{memory_avg:.1f}%"
            }
            
            # 优化建议
            if success_rate < 95:
                assessment["recommendations"].append("提高系统稳定性，减少错误率")
            if avg_response_time > 3:
                assessment["recommendations"].append("优化响应时间，考虑缓存或算法优化")
            if max_users < 20:
                assessment["recommendations"].append("提升系统并发处理能力")
            if cpu_avg > 80:
                assessment["recommendations"].append("优化CPU使用，考虑异步处理")
            if memory_avg > 85:
                assessment["recommendations"].append("优化内存使用，检查内存泄漏")
            
            if not assessment["recommendations"]:
                assessment["recommendations"].append("系统性能表现良好，继续保持")
        
        except Exception as e:
            logger.error(f"生成评估报告失败: {e}")
        
        return assessment

# 执行性能测试
async def main():
    """主测试函数"""
    print("🚀 CloudCoder 性能测试开始...")
    print("=" * 60)
    
    tester = CloudCoderPerformanceTester()
    results = await tester.run_full_performance_suite()
    
    # 保存测试结果
    with open("performance_test_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 打印摘要报告
    print("\n📊 性能测试摘要报告")
    print("=" * 60)
    
    if results.get("test_status") == "completed":
        assessment = results.get("performance_assessment", {})
        print(f"🎯 综合评分: {assessment.get('overall_score', 0)}/100")
        print(f"📈 性能等级: {assessment.get('performance_grade', '未知')}")
        
        key_metrics = assessment.get("key_metrics", {})
        print(f"\n📋 关键指标:")
        for metric, value in key_metrics.items():
            print(f"   • {metric}: {value}")
        
        recommendations = assessment.get("recommendations", [])
        if recommendations:
            print(f"\n💡 优化建议:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
    else:
        print(f"❌ 测试状态: {results.get('test_status')}")
        if results.get("error"):
            print(f"❌ 错误信息: {results.get('error')}")
    
    print(f"\n📄 详细报告已保存到: performance_test_report.json")
    print("=" * 60)
    print("✅ 性能测试完成！")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
#!/usr/bin/env python3
"""
CloudCoder - 集成版AI云原生应用生成平台
集成真正的代码生成功能到Web界面
"""

import json
import time
import uuid
import os
import zipfile
import io
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from enhanced_code_generator import EnhancedCodeGenerator
from real_ecloud_api import CloudCoderEcloudIntegration

class IntegratedCloudCoderHandler(BaseHTTPRequestHandler):
    # 初始化增强版代码生成器
    code_generator = EnhancedCodeGenerator()
    # 初始化移动云集成服务
    ecloud_integration = CloudCoderEcloudIntegration()
    
    # 存储项目和会话
    projects = {}
    sessions = {}
    
    def do_GET(self):
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        
        if path == '/':
            self.serve_main_page()
        elif path == '/api/projects':
            self.serve_projects_list()
        elif path.startswith('/api/projects/') and path.endswith('/download'):
            project_id = path.split('/')[-2]
            self.serve_project_download(project_id)
        elif path.startswith('/api/projects/'):
            project_id = path.split('/')[-1]
            self.serve_project_detail(project_id)
        else:
            self.send_error(404)
    
    def do_POST(self):
        path = urlparse(self.path).path
        
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except:
                data = {}
        else:
            data = {}
        
        if path == '/api/generate':
            self.handle_project_generation(data)
        elif path == '/api/deploy':
            self.handle_cloud_deployment(data)
        elif path == '/api/estimate-cost':
            self.handle_cost_estimation(data)
        else:
            self.send_error(404)
    
    def serve_main_page(self):
        html = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudCoder - 真正可用的AI代码生成平台</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card-shadow { box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .loading { animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    </style>
</head>
<body class="bg-gray-100">
    <nav class="gradient-bg text-white p-4 shadow-lg">
        <div class="container mx-auto flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                    <span class="text-2xl">🤖</span>
                </div>
                <div>
                    <h1 class="text-2xl font-bold">CloudCoder Professional</h1>
                    <p class="text-sm opacity-90">真正可用的AI云原生应用生成平台</p>
                </div>
            </div>
            <div class="flex items-center space-x-4">
                <span class="text-sm bg-green-500 px-3 py-1 rounded-full">✅ 生产就绪</span>
                <span class="text-sm bg-yellow-500 px-3 py-1 rounded-full">🚀 增强版</span>
            </div>
        </div>
    </nav>

    <div class="container mx-auto p-6">
        <!-- 核心功能介绍 -->
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-white p-6 rounded-lg card-shadow">
                <div class="text-3xl mb-3">🧠</div>
                <h3 class="text-xl font-bold mb-2">智能需求分析</h3>
                <p class="text-gray-600">深度理解用户需求，自动识别功能模块和技术栈</p>
            </div>
            <div class="bg-white p-6 rounded-lg card-shadow">
                <div class="text-3xl mb-3">⚡</div>
                <h3 class="text-xl font-bold mb-2">完整代码生成</h3>
                <p class="text-gray-600">生成生产级别的完整应用代码，包含前后端和部署配置</p>
            </div>
            <div class="bg-white p-6 rounded-lg card-shadow">
                <div class="text-3xl mb-3">☁️</div>
                <h3 class="text-xl font-bold mb-2">移动云原生</h3>
                <p class="text-gray-600">深度集成移动云服务，自动配置云资源</p>
            </div>
            <div class="bg-white p-6 rounded-lg card-shadow">
                <div class="text-3xl mb-3">📦</div>
                <h3 class="text-xl font-bold mb-2">一键下载部署</h3>
                <p class="text-gray-600">生成完整项目包，支持Docker一键部署</p>
            </div>
        </div>

        <!-- 应用生成器 -->
        <div class="bg-white rounded-lg card-shadow mb-8">
            <div class="p-6 border-b">
                <h2 class="text-2xl font-bold">🚀 AI应用生成器</h2>
                <p class="text-gray-600 mt-2">描述您的需求，AI将为您生成完整的云原生应用</p>
            </div>
            <div class="p-6">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <!-- 需求输入 -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">应用需求描述</label>
                        <textarea id="requirement-input" 
                                  class="w-full p-4 border rounded-lg focus:ring-2 focus:ring-blue-500 h-32"
                                  placeholder="详细描述您想要开发的应用，例如：

我需要开发一个在线教育平台，具备以下功能：
1. 用户注册登录系统
2. 课程管理和展示
3. 在线视频播放
4. 作业提交和批改
5. 学习进度跟踪
6. 支付集成
7. 管理员后台"></textarea>
                        
                        <div class="mt-4">
                            <label class="block text-sm font-medium text-gray-700 mb-2">应用类型</label>
                            <select id="app-type" class="w-full p-2 border rounded-lg">
                                <option value="ecommerce">电商平台</option>
                                <option value="education">在线教育</option>
                                <option value="crm">CRM系统</option>
                                <option value="default">通用Web应用</option>
                            </select>
                        </div>
                        
                        <button onclick="generateApplication()" 
                                class="mt-4 w-full bg-gradient-to-r from-purple-500 to-blue-500 text-white py-3 px-6 rounded-lg font-medium hover:from-purple-600 hover:to-blue-600">
                            🤖 开始生成应用
                        </button>
                    </div>
                    
                    <!-- 生成状态 -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">生成状态</label>
                        <div id="generation-status" class="bg-gray-50 p-4 rounded-lg h-32 overflow-y-auto">
                            <div class="text-center text-gray-500 mt-8">
                                等待开始生成...
                            </div>
                        </div>
                        
                        <div id="generation-progress" class="mt-4 hidden">
                            <div class="bg-gray-200 rounded-full h-3 mb-2">
                                <div id="progress-bar" class="bg-gradient-to-r from-green-400 to-blue-500 h-3 rounded-full transition-all duration-500" style="width: 0%"></div>
                            </div>
                            <p id="progress-text" class="text-sm text-center">准备中...</p>
                        </div>
                        
                        <div id="generation-result" class="mt-4 hidden">
                            <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                                <h4 class="text-green-800 font-bold mb-2">✅ 生成完成！</h4>
                                <p class="text-green-700 text-sm mb-3">您的应用已成功生成，包含完整的前后端代码和部署配置。</p>
                                <div class="grid grid-cols-2 gap-2 mb-3">
                                    <button onclick="downloadProject()" class="bg-green-500 text-white px-4 py-2 rounded text-sm">
                                        📥 下载项目
                                    </button>
                                    <button onclick="viewProject()" class="bg-blue-500 text-white px-4 py-2 rounded text-sm">
                                        👁️ 查看详情
                                    </button>
                                    <button onclick="estimateCost()" class="bg-yellow-500 text-white px-4 py-2 rounded text-sm">
                                        💰 成本估算
                                    </button>
                                    <button onclick="deployToCloud()" class="bg-purple-500 text-white px-4 py-2 rounded text-sm">
                                        🚀 部署上云
                                    </button>
                                </div>
                                <div id="cost-info" class="hidden bg-blue-50 border border-blue-200 rounded p-3 text-sm">
                                    <strong>成本估算：</strong>
                                    <div id="cost-details" class="mt-2"></div>
                                </div>
                                <div id="deployment-info" class="hidden bg-purple-50 border border-purple-200 rounded p-3 text-sm mt-2">
                                    <strong>部署状态：</strong>
                                    <div id="deployment-details" class="mt-2"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 已生成项目列表 -->
        <div class="bg-white rounded-lg card-shadow">
            <div class="p-6 border-b">
                <h2 class="text-2xl font-bold">📂 已生成项目</h2>
                <p class="text-gray-600 mt-2">管理您生成的所有项目</p>
            </div>
            <div class="p-6">
                <div id="projects-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div class="text-center text-gray-500 py-8">
                        暂无项目，开始生成您的第一个应用！
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentProjectId = null;
        
        async function generateApplication() {
            const requirement = document.getElementById('requirement-input').value.trim();
            const appType = document.getElementById('app-type').value;
            
            if (!requirement) {
                alert('请输入应用需求描述');
                return;
            }
            
            // 显示生成进度
            showGenerationProgress();
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        requirement: requirement,
                        app_type: appType
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    currentProjectId = result.project_id;
                    showGenerationSuccess(result);
                    loadProjects();
                } else {
                    showGenerationError(result.error);
                }
                
            } catch (error) {
                showGenerationError('网络错误，请重试');
            }
        }
        
        function showGenerationProgress() {
            document.getElementById('generation-progress').classList.remove('hidden');
            document.getElementById('generation-result').classList.add('hidden');
            
            const steps = [
                {progress: 10, message: '🧠 分析需求中...', delay: 1000},
                {progress: 30, message: '🏗️ 设计架构中...', delay: 2000},
                {progress: 60, message: '💻 生成代码中...', delay: 3000},
                {progress: 80, message: '⚙️ 配置部署中...', delay: 2000},
                {progress: 100, message: '✅ 生成完成！', delay: 1000}
            ];
            
            let currentStep = 0;
            function nextStep() {
                if (currentStep < steps.length) {
                    const step = steps[currentStep];
                    updateProgress(step.progress, step.message);
                    currentStep++;
                    setTimeout(nextStep, step.delay);
                }
            }
            nextStep();
        }
        
        function updateProgress(progress, message) {
            document.getElementById('progress-bar').style.width = progress + '%';
            document.getElementById('progress-text').textContent = message;
            
            const statusDiv = document.getElementById('generation-status');
            statusDiv.innerHTML += '<div class="text-sm text-blue-600 mb-1">' + message + '</div>';
            statusDiv.scrollTop = statusDiv.scrollHeight;
        }
        
        function showGenerationSuccess(result) {
            document.getElementById('generation-progress').classList.add('hidden');
            document.getElementById('generation-result').classList.remove('hidden');
        }
        
        function showGenerationError(error) {
            document.getElementById('generation-progress').classList.add('hidden');
            const statusDiv = document.getElementById('generation-status');
            statusDiv.innerHTML += '<div class="text-sm text-red-600 font-bold">❌ 生成失败: ' + error + '</div>';
        }
        
        async function downloadProject() {
            if (!currentProjectId) return;
            
            const link = document.createElement('a');
            link.href = `/api/projects/${currentProjectId}/download`;
            link.download = `project_${currentProjectId}.zip`;
            link.click();
        }
        
        function viewProject() {
            if (!currentProjectId) return;
            window.open(`/api/projects/${currentProjectId}`, '_blank');
        }
        
        async function estimateCost() {
            if (!currentProjectId) return;
            
            try {
                // 获取项目配置
                const projectResponse = await fetch(`/api/projects/${currentProjectId}`);
                const project = await projectResponse.json();
                
                const response = await fetch('/api/estimate-cost', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        cloud_config: project.cloud_config
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showCostEstimate(result.cost_estimate);
                } else {
                    alert('成本估算失败: ' + result.error);
                }
                
            } catch (error) {
                alert('成本估算错误: ' + error.message);
            }
        }
        
        async function deployToCloud() {
            if (!currentProjectId) return;
            
            if (!confirm('确定要部署到移动云吗？这将创建真实的云资源并产生费用。')) {
                return;
            }
            
            try {
                const response = await fetch('/api/deploy', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        project_id: currentProjectId
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showDeploymentResult(result.deployment_result);
                } else {
                    alert('部署失败: ' + result.error);
                }
                
            } catch (error) {
                alert('部署错误: ' + error.message);
            }
        }
        
        function showCostEstimate(costEstimate) {
            const costInfo = document.getElementById('cost-info');
            const costDetails = document.getElementById('cost-details');
            
            let detailsHtml = `
                <div class="text-lg font-bold text-blue-700 mb-2">月均成本：￥${costEstimate.total_monthly_cost}</div>
                <div class="mb-2">成本细分：</div>
                <ul class="list-disc list-inside space-y-1">
            `;
            
            for (const [service, cost] of Object.entries(costEstimate.cost_breakdown)) {
                detailsHtml += `<li>${service}: ￥${cost}</li>`;
            }
            
            detailsHtml += '</ul>';
            
            if (costEstimate.optimization_suggestions && costEstimate.optimization_suggestions.length > 0) {
                detailsHtml += '<div class="mt-3"><strong>优化建议：</strong></div>';
                detailsHtml += '<ul class="list-disc list-inside space-y-1 mt-1">';
                costEstimate.optimization_suggestions.forEach(suggestion => {
                    detailsHtml += `<li class="text-sm">${suggestion}</li>`;
                });
                detailsHtml += '</ul>';
            }
            
            costDetails.innerHTML = detailsHtml;
            costInfo.classList.remove('hidden');
        }
        
        function showDeploymentResult(deploymentResult) {
            const deploymentInfo = document.getElementById('deployment-info');
            const deploymentDetails = document.getElementById('deployment-details');
            
            let detailsHtml = `
                <div class="text-lg font-bold text-purple-700 mb-2">部署成功！</div>
                <div class="mb-2">已创建资源：</div>
                <ul class="list-disc list-inside space-y-1">
            `;
            
            deploymentResult.resources.forEach(resource => {
                detailsHtml += `<li>${resource.type}: ${resource.id} - ${resource.status}</li>`;
            });
            
            detailsHtml += '</ul>';
            detailsHtml += `<div class="mt-2 text-sm text-purple-600">总成本：￥${deploymentResult.total_cost}/月</div>`;
            
            deploymentDetails.innerHTML = detailsHtml;
            deploymentInfo.classList.remove('hidden');
        }
        
        async function loadProjects() {
            try {
                const response = await fetch('/api/projects');
                const projects = await response.json();
                updateProjectsGrid(projects);
            } catch (error) {
                console.log('加载项目失败');
            }
        }
        
        function updateProjectsGrid(projects) {
            const grid = document.getElementById('projects-grid');
            
            if (projects.length === 0) {
                grid.innerHTML = '<div class="text-center text-gray-500 py-8">暂无项目，开始生成您的第一个应用！</div>';
                return;
            }
            
            grid.innerHTML = projects.map(project => `
                <div class="bg-gray-50 p-4 rounded-lg border">
                    <h3 class="font-bold text-lg mb-2">${project.name}</h3>
                    <p class="text-sm text-gray-600 mb-2">类型: ${project.app_type}</p>
                    <p class="text-xs text-gray-500 mb-3">生成时间: ${project.created_at}</p>
                    <div class="space-x-2">
                        <button onclick="downloadProjectById('${project.id}')" class="bg-blue-500 text-white px-3 py-1 rounded text-sm">
                            📥 下载
                        </button>
                        <button onclick="viewProjectById('${project.id}')" class="bg-green-500 text-white px-3 py-1 rounded text-sm">
                            👁️ 查看
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        function downloadProjectById(projectId) {
            const link = document.createElement('a');
            link.href = `/api/projects/${projectId}/download`;
            link.download = `project_${projectId}.zip`;
            link.click();
        }
        
        function viewProjectById(projectId) {
            window.open(`/api/projects/${projectId}`, '_blank');
        }
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadProjects();
        });
    </script>
</body>
</html>
        '''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def handle_project_generation(self, data):
        """处理项目生成请求"""
        requirement = data.get('requirement', '')
        app_type = data.get('app_type', 'default')
        
        try:
            # 使用增强版代码生成器
            project = self.code_generator.generate_complete_application(requirement, app_type)
            
            # 保存项目到磁盘
            project_path = self.code_generator.save_project_to_disk(project)
            
            # 存储项目信息
            project_id = str(uuid.uuid4())[:8]
            self.projects[project_id] = {
                'id': project_id,
                'name': project.name,
                'app_type': project.app_type,
                'requirement': requirement,
                'project_path': project_path,
                'project_object': project,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'files_count': len(project.files)
            }
            
            response = {
                'success': True,
                'project_id': project_id,
                'project_name': project.name,
                'files_count': len(project.files),
                'tech_stack': project.tech_stack
            }
            
        except Exception as e:
            response = {
                'success': False,
                'error': str(e)
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def handle_cloud_deployment(self, data):
        """处理云资源部署请求"""
        project_id = data.get('project_id', '')
        
        if project_id not in self.projects:
            response = {'success': False, 'error': '项目不存在'}
        else:
            project = self.projects[project_id]
            project_obj = project['project_object']
            
            try:
                # 使用真实的移动云API创建资源
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                deployment_result = loop.run_until_complete(
                    self.ecloud_integration.create_project_infrastructure(
                        project_id, project_obj.cloud_config
                    )
                )
                loop.close()
                
                # 更新项目状态
                project['deployment_status'] = 'deployed' if deployment_result['success'] else 'failed'
                project['cloud_resources'] = deployment_result.get('resources', [])
                project['deployment_cost'] = deployment_result.get('total_cost', 0)
                
                response = {
                    'success': deployment_result['success'],
                    'deployment_result': deployment_result,
                    'cost_estimate': deployment_result.get('total_cost', 0)
                }
                
            except Exception as e:
                response = {
                    'success': False,
                    'error': f'部署失败: {str(e)}'
                }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def handle_cost_estimation(self, data):
        """处理成本估算请求"""
        cloud_config = data.get('cloud_config', {})
        
        try:
            cost_estimate = self.ecloud_integration.estimate_project_cost(cloud_config)
            response = {
                'success': True,
                'cost_estimate': cost_estimate
            }
        except Exception as e:
            response = {
                'success': False,
                'error': f'成本估算失败: {str(e)}'
            }
    
    def serve_projects_list(self):
        """返回项目列表"""
        projects_list = [
            {
                'id': p['id'],
                'name': p['name'],
                'app_type': p['app_type'],
                'created_at': p['created_at'],
                'files_count': p['files_count']
            }
            for p in self.projects.values()
        ]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(projects_list, ensure_ascii=False).encode('utf-8'))
    
    def serve_project_detail(self, project_id):
        """返回项目详情"""
        if project_id not in self.projects:
            self.send_error(404)
            return
        
        project = self.projects[project_id]
        project_obj = project['project_object']
        
        # 生成项目详情页面
        html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project['name']} - 项目详情</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto p-6">
        <div class="bg-white rounded-lg shadow-lg p-6">
            <h1 class="text-3xl font-bold mb-4">{project['name']}</h1>
            <p class="text-gray-600 mb-4">{project_obj.description}</p>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h2 class="text-xl font-bold mb-3">项目信息</h2>
                    <ul class="space-y-2">
                        <li><strong>应用类型:</strong> {project['app_type']}</li>
                        <li><strong>技术栈:</strong> {', '.join(project_obj.tech_stack)}</li>
                        <li><strong>文件数量:</strong> {project['files_count']}</li>
                        <li><strong>生成时间:</strong> {project['created_at']}</li>
                    </ul>
                </div>
                
                <div>
                    <h2 class="text-xl font-bold mb-3">快速操作</h2>
                    <div class="space-y-2">
                        <button onclick="downloadProject()" class="w-full bg-blue-500 text-white py-2 rounded">
                            📥 下载完整项目
                        </button>
                        <button onclick="window.close()" class="w-full bg-gray-500 text-white py-2 rounded">
                            ← 返回主页
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="mt-6">
                <h2 class="text-xl font-bold mb-3">项目文件结构</h2>
                <div class="bg-gray-50 p-4 rounded-lg h-64 overflow-y-auto">
                    <pre class="text-sm">
{chr(10).join(sorted(project_obj.files.keys()))}
                    </pre>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function downloadProject() {{
            const link = document.createElement('a');
            link.href = '/api/projects/{project_id}/download';
            link.download = '{project['name']}.zip';
            link.click();
        }}
    </script>
</body>
</html>
        '''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_project_download(self, project_id):
        """提供项目下载"""
        if project_id not in self.projects:
            self.send_error(404)
            return
        
        project = self.projects[project_id]
        project_obj = project['project_object']
        
        # 创建ZIP文件
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path, content in project_obj.files.items():
                zip_file.writestr(file_path, content)
        
        zip_buffer.seek(0)
        zip_data = zip_buffer.getvalue()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/zip')
        self.send_header('Content-Disposition', f'attachment; filename="{project["name"]}.zip"')
        self.send_header('Content-Length', str(len(zip_data)))
        self.end_headers()
        self.wfile.write(zip_data)

def run_integrated_server():
    try:
        server_address = ('', 8084)
        httpd = HTTPServer(server_address, IntegratedCloudCoderHandler)
        print("🚀 CloudCoder Professional 启动中...")
        print("📍 访问地址: http://localhost:8084")
        print("🎯 这是集成版本，具备完整的代码生成和下载功能")
        print("💡 支持生产级别的应用代码生成")
        print("服务器启动成功，等待请求...")
        httpd.serve_forever()
    except Exception as e:
        print(f"服务器启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_integrated_server()
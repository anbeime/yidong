# CloudCoder 开发者文档

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16.0+
- Docker 20.0+

### 安装步骤
```bash
# 1. 克隆项目
git clone https://github.com/cloudcoder/platform.git
cd cloudcoder-platform

# 2. 后端环境
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# 3. 前端环境
cd frontend
npm install && npm start
```

### 环境配置
```env
DATABASE_URL=sqlite:///./cloudcoder.db
SECRET_KEY=your-secret-key
ECLOUD_ACCESS_KEY=your-access-key
ECLOUD_SECRET_KEY=your-secret-key
```

---

## 系统架构

### 核心模块
```
┌─────────────────────────────────────┐
│         前端层 (React)              │
├─────────────────────────────────────┤
│         API层 (FastAPI)             │
├─────────────────────────────────────┤
│    业务逻辑层 (Python Services)     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│  │AI代码生成│ │项目管理 │ │云资源管理│ │
│  └─────────┘ └─────────┘ └─────────┘ │
├─────────────────────────────────────┤
│       数据层 (SQLite/MySQL)         │
└─────────────────────────────────────┘
```

### 关键设计模式
- **工厂模式**: 代码生成器创建
- **策略模式**: 部署策略选择
- **观察者模式**: 状态变更通知

---

## 核心API

### 认证接口
```python
@app.post("/api/auth/login")
async def login(credentials: LoginRequest) -> TokenResponse:
    """用户登录"""
    
@app.post("/api/auth/register")
async def register(user_data: RegisterRequest) -> UserResponse:
    """用户注册"""
```

### 代码生成接口
```python
@app.post("/api/generate")
async def generate_code(request: GenerateRequest) -> GenerateResponse:
    """生成应用代码"""
    
@app.get("/api/generate/status/{project_id}")
async def get_generation_status(project_id: str) -> StatusResponse:
    """获取生成状态"""
```

### 项目管理接口
```python
@app.get("/api/projects")
async def get_projects(page: int = 1, size: int = 10) -> ProjectListResponse:
    """获取项目列表"""
    
@app.post("/api/projects")
async def create_project(project: ProjectCreateRequest) -> ProjectResponse:
    """创建新项目"""
```

---

## 数据库设计

### 核心表结构
```sql
-- 用户表
CREATE TABLE users (
    user_id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 项目表
CREATE TABLE projects (
    project_id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    app_type ENUM('ecommerce', 'education', 'crm', 'default'),
    status ENUM('draft', 'generating', 'completed', 'failed'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 项目文件表
CREATE TABLE project_files (
    file_id VARCHAR(36) PRIMARY KEY,
    project_id VARCHAR(36) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    content LONGTEXT NOT NULL,
    file_size INT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(project_id)
);
```

---

## 代码生成核心

### 需求分析器
```python
class RequirementAnalyzer:
    def analyze(self, requirement: str) -> AnalysisResult:
        """分析用户需求"""
        # 1. 提取关键词
        keywords = self.extract_keywords(requirement)
        
        # 2. 识别应用类型
        app_type = self.detect_app_type(keywords)
        
        # 3. 提取功能模块
        features = self.extract_features(requirement)
        
        return AnalysisResult(
            app_type=app_type,
            features=features,
            complexity=self.calculate_complexity(features)
        )
```

### 代码生成器
```python
class CodeGenerator:
    def generate(self, analysis: AnalysisResult) -> List[CodeFile]:
        """生成项目代码"""
        files = []
        
        # 生成前端代码
        files.extend(self.generate_frontend(analysis.features))
        
        # 生成后端代码
        files.extend(self.generate_backend(analysis.features))
        
        # 生成部署配置
        files.extend(self.generate_deployment_config())
        
        return files
```

### 模板系统
```python
# React组件模板示例
REACT_COMPONENT_TEMPLATE = """
import React, { useState, useEffect } from 'react';
import { {{ imports }} } from 'antd';

const {{ component_name }}: React.FC = () => {
  const [{{ state_name }}, set{{ state_name|title }}] = useState<{{ state_type }}>([]);

  useEffect(() => {
    // 初始化数据
    load{{ state_name|title }}();
  }, []);

  const load{{ state_name|title }} = async () => {
    // API调用逻辑
  };

  return (
    <div className="{{ component_name|lower }}-container">
      {{ component_content }}
    </div>
  );
};

export default {{ component_name }};
"""
```

---

## 移动云集成

### API客户端
```python
class EcloudAPIClient:
    def __init__(self, access_key: str, secret_key: str):
        self.access_key = access_key
        self.secret_key = secret_key
        
    async def create_ecs_instance(self, config: ECSConfig) -> str:
        """创建ECS实例"""
        payload = {
            'InstanceType': config.instance_type,
            'ImageId': config.image_id,
            'SecurityGroupId': config.security_group_id
        }
        
        response = await self._make_request('CreateInstance', payload)
        return response['InstanceId']
        
    async def estimate_cost(self, resources: List[Resource]) -> float:
        """估算成本"""
        total_cost = 0
        for resource in resources:
            cost = await self._get_resource_cost(resource)
            total_cost += cost
        return total_cost
```

### 资源编排器
```python
class ResourceOrchestrator:
    async def deploy_project(self, project_id: str, config: DeploymentConfig):
        """部署项目到云端"""
        deployment = CloudDeployment(project_id=project_id)
        
        try:
            # 1. 创建VPC网络
            vpc_id = await self.create_vpc(config.vpc_config)
            
            # 2. 创建ECS实例
            instance_id = await self.create_ecs_instance(config.ecs_config)
            
            # 3. 创建RDS数据库
            db_instance_id = await self.create_rds_instance(config.rds_config)
            
            # 4. 部署应用
            await self.deploy_application(instance_id, project_id)
            
            deployment.status = 'deployed'
            return deployment
            
        except Exception as e:
            deployment.status = 'failed'
            deployment.error_message = str(e)
            raise
```

---

## 部署指南

### Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://user:pass@db:3306/cloudcoder
    depends_on:
      - db
      
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: cloudcoder
      MYSQL_USER: user
      MYSQL_PASSWORD: pass
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

### Kubernetes部署
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloudcoder-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cloudcoder
  template:
    metadata:
      labels:
        app: cloudcoder
    spec:
      containers:
      - name: cloudcoder
        image: cloudcoder/app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "mysql://user:pass@mysql:3306/cloudcoder"
---
apiVersion: v1
kind: Service
metadata:
  name: cloudcoder-service
spec:
  selector:
    app: cloudcoder
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## 扩展开发

### 添加新的应用类型
```python
# 1. 定义新的生成器
class BlogGenerator(CodeGenerator):
    def generate_frontend(self, features: List[Feature]) -> List[CodeFile]:
        # 博客前端生成逻辑
        pass
        
    def generate_backend(self, features: List[Feature]) -> List[CodeFile]:
        # 博客后端生成逻辑
        pass

# 2. 注册到工厂
class CodeGeneratorFactory:
    generators = {
        'ecommerce': EcommerceGenerator,
        'education': EducationGenerator,
        'crm': CRMGenerator,
        'blog': BlogGenerator,  # 新增
        'default': DefaultGenerator
    }
```

### 添加新的模板
```python
# 在templates/目录下添加新模板文件
# templates/blog/
#   ├── frontend/
#   │   ├── PostList.tsx.j2
#   │   └── PostDetail.tsx.j2
#   └── backend/
#       ├── post_model.py.j2
#       └── post_api.py.j2
```

### 添加新的云服务集成
```python
class EcloudAPIClient:
    async def create_redis_instance(self, config: RedisConfig) -> str:
        """创建Redis实例"""
        payload = {
            'InstanceClass': config.instance_class,
            'MemorySize': config.memory_size,
            'VpcId': config.vpc_id
        }
        
        response = await self._make_request('CreateRedisInstance', payload)
        return response['InstanceId']
```

---

## 监控和日志

### 日志配置
```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/cloudcoder.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 性能监控
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {str(e)}")
            raise
    return wrapper
```

---

## 测试指南

### 单元测试
```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def code_generator():
    return CodeGenerator()

@pytest.fixture
def sample_analysis():
    return AnalysisResult(
        app_type=AppType.ECOMMERCE,
        features=[Feature.USER_MANAGEMENT, Feature.PRODUCT_CATALOG],
        complexity=Complexity.MEDIUM
    )

def test_generate_frontend_files(code_generator, sample_analysis):
    files = code_generator.generate_frontend(sample_analysis.features)
    assert len(files) > 0
    assert any('App.tsx' in f.path for f in files)
```

### 集成测试
```python
@pytest.mark.asyncio
async def test_full_project_generation():
    # 创建项目
    project = await project_service.create_project(
        user_id='test-user',
        project_data=ProjectCreateData(
            name='测试项目',
            app_type=AppType.ECOMMERCE
        )
    )
    
    # 生成代码
    result = await code_generation_service.generate(
        project.project_id,
        '创建一个电商平台'
    )
    
    assert result.success is True
    assert len(result.files) > 0
```

---

## 贡献指南

### 开发流程
1. Fork项目仓库
2. 创建功能分支: `git checkout -b feature/new-feature`
3. 提交代码: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 创建Pull Request

### 代码规范
- 使用Black格式化Python代码
- 使用Prettier格式化前端代码
- 遵循PEP 8编码规范
- 添加必要的类型注解

### 提交信息规范
```
feat: 添加新功能
fix: 修复bug
docs: 更新文档
style: 代码格式化
refactor: 重构代码
test: 添加测试
chore: 构建或工具变动
```

---

**版本**: v1.0.0  
**更新时间**: 2025年8月25日  
**联系方式**: dev@cloudcoder.com
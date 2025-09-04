#!/usr/bin/env python3
"""
CloudCoder - AI代码生成引擎
基于模板和AI生成完整的微服务应用代码
"""

import os
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class CodeTemplate:
    """代码模板类"""
    name: str
    description: str
    tech_stack: str
    files: Dict[str, str]  # 文件路径 -> 模板内容
    variables: List[str]   # 模板变量
    dependencies: List[str] # 依赖包

@dataclass
class GeneratedProject:
    """生成的项目类"""
    project_id: str
    name: str
    app_type: str
    tech_stack: str
    files: Dict[str, str]  # 文件路径 -> 生成的代码
    cloud_config: Dict     # 云资源配置
    deployment_config: Dict # 部署配置

class CodeGenerator:
    """AI代码生成器"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.ai_patterns = self._load_ai_patterns()
    
    def _load_templates(self) -> Dict[str, CodeTemplate]:
        """加载代码模板"""
        templates = {}
        
        # 电商应用模板
        ecommerce_template = CodeTemplate(
            name="ecommerce",
            description="完整的电商平台应用",
            tech_stack="React + FastAPI + MySQL + Redis",
            files={
                "frontend/src/App.tsx": self._get_react_app_template(),
                "frontend/src/pages/ProductList.tsx": self._get_product_list_template(),
                "frontend/src/pages/Cart.tsx": self._get_cart_template(),
                "frontend/src/pages/Order.tsx": self._get_order_template(),
                "frontend/package.json": self._get_frontend_package_json(),
                "backend/app/main.py": self._get_fastapi_main_template(),
                "backend/app/models/product.py": self._get_product_model_template(),
                "backend/app/models/order.py": self._get_order_model_template(),
                "backend/app/api/products.py": self._get_products_api_template(),
                "backend/app/api/orders.py": self._get_orders_api_template(),
                "backend/requirements.txt": self._get_backend_requirements(),
                "database/schema.sql": self._get_database_schema(),
                "docker-compose.yml": self._get_docker_compose_template(),
                "kubernetes/deployment.yaml": self._get_k8s_deployment_template(),
                "README.md": self._get_readme_template()
            },
            variables=["APP_NAME", "DB_NAME", "REDIS_CONFIG", "DOMAIN"],
            dependencies=["fastapi", "uvicorn", "sqlalchemy", "redis", "mysql-connector-python"]
        )
        templates["ecommerce"] = ecommerce_template
        
        # 在线教育模板
        education_template = CodeTemplate(
            name="education",
            description="在线教育平台应用",
            tech_stack="React + FastAPI + PostgreSQL + Redis",
            files={
                "frontend/src/App.tsx": self._get_education_app_template(),
                "frontend/src/pages/CourseList.tsx": self._get_course_list_template(),
                "frontend/src/pages/LiveClass.tsx": self._get_live_class_template(),
                "backend/app/main.py": self._get_education_main_template(),
                "backend/app/models/course.py": self._get_course_model_template(),
                "backend/app/api/courses.py": self._get_courses_api_template(),
                "database/schema.sql": self._get_education_schema(),
                "docker-compose.yml": self._get_education_docker_template(),
                "README.md": self._get_education_readme_template()
            },
            variables=["APP_NAME", "DB_NAME", "LIVE_STREAM_CONFIG"],
            dependencies=["fastapi", "uvicorn", "sqlalchemy", "redis", "psycopg2-binary"]
        )
        templates["education"] = education_template
        
        return templates
    
    def _load_ai_patterns(self) -> Dict[str, str]:
        """加载AI生成模式"""
        return {
            "crud_api": """
# AI生成的CRUD API模式
class {MODEL_NAME}API:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_{model_name}(self, {model_name}_data: {MODEL_NAME}Create):
        {model_name} = {MODEL_NAME}(**{model_name}_data.dict())
        self.db.add({model_name})
        self.db.commit()
        return {model_name}
    
    async def get_{model_name}(self, {model_name}_id: int):
        return self.db.query({MODEL_NAME}).filter({MODEL_NAME}.id == {model_name}_id).first()
    
    async def update_{model_name}(self, {model_name}_id: int, {model_name}_data: {MODEL_NAME}Update):
        {model_name} = self.get_{model_name}({model_name}_id)
        if {model_name}:
            for key, value in {model_name}_data.dict(exclude_unset=True).items():
                setattr({model_name}, key, value)
            self.db.commit()
        return {model_name}
    
    async def delete_{model_name}(self, {model_name}_id: int):
        {model_name} = self.get_{model_name}({model_name}_id)
        if {model_name}:
            self.db.delete({model_name})
            self.db.commit()
        return {model_name}
            """,
            
            "react_component": """
// AI生成的React组件模式
import React, {{ useState, useEffect }} from 'react';
import {{ {IMPORTS} }} from 'antd';

const {COMPONENT_NAME}: React.FC = () => {{
    const [data, setData] = useState<{DATA_TYPE}[]>([]);
    const [loading, setLoading] = useState(false);
    
    useEffect(() => {{
        loadData();
    }}, []);
    
    const loadData = async () => {{
        setLoading(true);
        try {{
            const response = await fetch('/api/{api_endpoint}');
            const result = await response.json();
            setData(result);
        }} catch (error) {{
            console.error('加载数据失败:', error);
        }} finally {{
            setLoading(false);
        }}
    }};
    
    return (
        <div>
            <h2>{TITLE}</h2>
            {/* AI生成的组件内容 */}
            {{data.map(item => (
                <div key={{item.id}}>
                    {{/* 根据数据类型自动生成展示逻辑 */}}
                </div>
            ))}}
        </div>
    );
}};

export default {COMPONENT_NAME};
            """
        }
    
    def generate_project(self, requirement: str, app_type: str, project_id: str) -> GeneratedProject:
        """根据需求生成完整项目"""
        
        # 1. 选择合适的模板
        template = self.templates.get(app_type.lower(), self.templates["ecommerce"])
        
        # 2. AI分析需求，提取关键信息
        ai_analysis = self._analyze_requirement_with_ai(requirement)
        
        # 3. 生成项目变量
        project_vars = self._generate_project_variables(ai_analysis, project_id)
        
        # 4. 基于模板和AI分析生成代码
        generated_files = {}
        for file_path, template_content in template.files.items():
            generated_code = self._generate_file_content(
                template_content, 
                project_vars, 
                ai_analysis,
                file_path
            )
            generated_files[file_path] = generated_code
        
        # 5. 生成云资源配置
        cloud_config = self._generate_cloud_config(ai_analysis, project_vars)
        
        # 6. 生成部署配置
        deployment_config = self._generate_deployment_config(ai_analysis, project_vars)
        
        return GeneratedProject(
            project_id=project_id,
            name=project_vars["APP_NAME"],
            app_type=app_type,
            tech_stack=template.tech_stack,
            files=generated_files,
            cloud_config=cloud_config,
            deployment_config=deployment_config
        )
    
    def _analyze_requirement_with_ai(self, requirement: str) -> Dict:
        """AI分析需求"""
        analysis = {
            "entities": [],
            "features": [],
            "business_logic": [],
            "ui_components": [],
            "api_endpoints": [],
            "database_tables": []
        }
        
        # 模拟AI分析过程
        req_lower = requirement.lower()
        
        # 识别实体
        if "商品" in req_lower or "产品" in req_lower:
            analysis["entities"].append("Product")
            analysis["database_tables"].append("products")
            analysis["api_endpoints"].append("products")
            analysis["ui_components"].append("ProductList")
        
        if "订单" in req_lower:
            analysis["entities"].append("Order")
            analysis["database_tables"].append("orders")
            analysis["api_endpoints"].append("orders")
            analysis["ui_components"].append("OrderManagement")
        
        if "用户" in req_lower or "客户" in req_lower:
            analysis["entities"].append("User")
            analysis["database_tables"].append("users")
            analysis["api_endpoints"].append("users")
            analysis["ui_components"].append("UserProfile")
        
        if "购物车" in req_lower:
            analysis["entities"].append("Cart")
            analysis["ui_components"].append("ShoppingCart")
            analysis["api_endpoints"].append("cart")
        
        if "课程" in req_lower:
            analysis["entities"].append("Course")
            analysis["database_tables"].append("courses")
            analysis["api_endpoints"].append("courses")
            analysis["ui_components"].append("CourseList")
        
        if "直播" in req_lower:
            analysis["features"].append("live_streaming")
            analysis["ui_components"].append("LivePlayer")
        
        # 识别功能特性
        if "支付" in req_lower:
            analysis["features"].append("payment")
        
        if "搜索" in req_lower:
            analysis["features"].append("search")
        
        if "评论" in req_lower:
            analysis["features"].append("comments")
            analysis["entities"].append("Comment")
        
        return analysis
    
    def _generate_project_variables(self, ai_analysis: Dict, project_id: str) -> Dict[str, str]:
        """生成项目变量"""
        return {
            "APP_NAME": f"ai_generated_app_{project_id}",
            "PROJECT_ID": project_id,
            "DB_NAME": f"db_{project_id}",
            "REDIS_CONFIG": "redis:6379",
            "DOMAIN": f"{project_id}.ecloud-demo.com",
            "API_PREFIX": "/api/v1",
            "ENTITIES": ",".join(ai_analysis.get("entities", [])),
            "FEATURES": ",".join(ai_analysis.get("features", []))
        }
    
    def _generate_file_content(self, template: str, variables: Dict, ai_analysis: Dict, file_path: str) -> str:
        """生成文件内容"""
        content = template
        
        # 替换基础变量
        for var_name, var_value in variables.items():
            content = content.replace(f"{{{var_name}}}", str(var_value))
        
        # AI增强：根据分析结果动态生成内容
        if file_path.endswith('.tsx') or file_path.endswith('.ts'):
            content = self._enhance_frontend_code(content, ai_analysis)
        elif file_path.endswith('.py'):
            content = self._enhance_backend_code(content, ai_analysis)
        elif file_path.endswith('.sql'):
            content = self._enhance_database_schema(content, ai_analysis)
        
        return content
    
    def _enhance_frontend_code(self, content: str, ai_analysis: Dict) -> str:
        """增强前端代码"""
        # 根据AI分析的UI组件，动态生成React组件
        ui_components = ai_analysis.get("ui_components", [])
        for component in ui_components:
            if component in content:
                # 插入AI生成的组件逻辑
                enhanced_logic = f"""
    // AI生成的{component}组件逻辑
    const handle{component}Action = async (action: string, data: any) => {{
        try {{
            const response = await fetch(`/api/{{action}}`, {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(data)
            }});
            const result = await response.json();
            return result;
        }} catch (error) {{
            console.error('操作失败:', error);
        }}
    }};
                """
                content = content.replace(f"// {component}", enhanced_logic)
        
        return content
    
    def _enhance_backend_code(self, content: str, ai_analysis: Dict) -> str:
        """增强后端代码"""
        # 根据AI分析的API端点，动态生成API路由
        api_endpoints = ai_analysis.get("api_endpoints", [])
        for endpoint in api_endpoints:
            if f"/{endpoint}" in content:
                # 插入AI生成的API逻辑
                enhanced_api = f"""
# AI生成的{endpoint} API端点
@router.get("/{endpoint}")
async def get_{endpoint}(db: Session = Depends(get_db)):
    items = db.query({endpoint.title()}).all()
    return items

@router.post("/{endpoint}")
async def create_{endpoint}(item_data: {endpoint.title()}Create, db: Session = Depends(get_db)):
    item = {endpoint.title()}(**item_data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
                """
                content += enhanced_api
        
        return content
    
    def _enhance_database_schema(self, content: str, ai_analysis: Dict) -> str:
        """增强数据库模式"""
        # 根据AI分析的数据库表，动态生成表结构
        tables = ai_analysis.get("database_tables", [])
        enhanced_schema = ""
        
        for table in tables:
            if table == "products":
                enhanced_schema += """
-- AI生成的商品表
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    category_id INT,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_price ON products(price);
                """
            elif table == "orders":
                enhanced_schema += """
-- AI生成的订单表
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'paid', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    shipping_address TEXT,
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
                """
            elif table == "courses":
                enhanced_schema += """
-- AI生成的课程表
CREATE TABLE courses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructor_id INT NOT NULL,
    price DECIMAL(10,2),
    duration_hours INT,
    level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    thumbnail_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
                """
        
        return content + enhanced_schema
    
    def _generate_cloud_config(self, ai_analysis: Dict, variables: Dict) -> Dict:
        """生成移动云资源配置"""
        features = ai_analysis.get("features", [])
        entities = ai_analysis.get("entities", [])
        
        # 基础配置
        cloud_config = {
            "ecs_instances": [
                {
                    "name": f"{variables['PROJECT_ID']}-web",
                    "type": "ecs.c6.large",
                    "cpu": 2,
                    "memory": 4,
                    "purpose": "前端应用服务器"
                },
                {
                    "name": f"{variables['PROJECT_ID']}-api",
                    "type": "ecs.c6.xlarge", 
                    "cpu": 4,
                    "memory": 8,
                    "purpose": "后端API服务器"
                }
            ],
            "rds_instance": {
                "name": f"{variables['PROJECT_ID']}-db",
                "engine": "MySQL",
                "version": "8.0",
                "cpu": 2,
                "memory": 4,
                "storage": 100
            },
            "redis_instance": {
                "name": f"{variables['PROJECT_ID']}-cache",
                "memory": 2,
                "purpose": "缓存和会话存储"
            },
            "oss_bucket": {
                "name": f"{variables['PROJECT_ID']}-storage",
                "purpose": "静态文件存储"
            },
            "vpc_config": {
                "name": f"{variables['PROJECT_ID']}-vpc",
                "cidr": "10.0.0.0/16",
                "subnets": [
                    {"name": "public", "cidr": "10.0.1.0/24"},
                    {"name": "private", "cidr": "10.0.2.0/24"}
                ]
            }
        }
        
        # 根据功能特性调整配置
        if "live_streaming" in features:
            cloud_config["ecs_instances"].append({
                "name": f"{variables['PROJECT_ID']}-stream",
                "type": "ecs.c6.2xlarge",
                "cpu": 8,
                "memory": 16,
                "purpose": "直播流媒体服务器"
            })
            cloud_config["cdn_config"] = {
                "name": f"{variables['PROJECT_ID']}-cdn",
                "purpose": "直播内容分发"
            }
        
        if "payment" in features:
            cloud_config["security_group"] = {
                "name": f"{variables['PROJECT_ID']}-security",
                "rules": [
                    {"port": 443, "protocol": "HTTPS", "source": "0.0.0.0/0"},
                    {"port": 80, "protocol": "HTTP", "source": "0.0.0.0/0"}
                ]
            }
        
        # 根据数据量调整资源配置
        entity_count = len(entities)
        if entity_count > 3:
            # 复杂应用，增加资源配置
            cloud_config["rds_instance"]["cpu"] = 4
            cloud_config["rds_instance"]["memory"] = 8
            cloud_config["redis_instance"]["memory"] = 4
        
        return cloud_config
    
    def _generate_deployment_config(self, ai_analysis: Dict, variables: Dict) -> Dict:
        """生成部署配置"""
        return {
            "docker_config": {
                "frontend_image": f"{variables['PROJECT_ID']}-frontend:latest",
                "backend_image": f"{variables['PROJECT_ID']}-backend:latest",
                "registry": "ecloud-registry.cn"
            },
            "kubernetes_config": {
                "namespace": variables['PROJECT_ID'],
                "replicas": {
                    "frontend": 2,
                    "backend": 3
                },
                "resources": {
                    "frontend": {"cpu": "100m", "memory": "256Mi"},
                    "backend": {"cpu": "500m", "memory": "512Mi"}
                }
            },
            "ci_cd_config": {
                "pipeline": "jenkins",
                "stages": ["build", "test", "deploy"],
                "auto_deploy": True
            }
        }
    
    # 模板方法（简化版本，实际应用中会更复杂）
    def _get_react_app_template(self) -> str:
        return '''
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import ProductList from './pages/ProductList';
import Cart from './pages/Cart';
import Order from './pages/Order';

const { Header, Content, Sider } = Layout;

const App: React.FC = () => {
  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Header>
          <h1 style={{ color: 'white', margin: 0 }}>{APP_NAME}</h1>
        </Header>
        <Layout>
          <Sider>
            <Menu mode="inline" defaultSelectedKeys={['1']}>
              <Menu.Item key="1">商品列表</Menu.Item>
              <Menu.Item key="2">购物车</Menu.Item>
              <Menu.Item key="3">订单管理</Menu.Item>
            </Menu>
          </Sider>
          <Content style={{ padding: '20px' }}>
            <Routes>
              <Route path="/" element={<ProductList />} />
              <Route path="/cart" element={<Cart />} />
              <Route path="/orders" element={<Order />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
};

export default App;
        '''
    
    def _get_fastapi_main_template(self) -> str:
        return '''
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db
from app.api import products, orders

app = FastAPI(
    title="{APP_NAME}",
    description="AI生成的{APP_NAME}应用",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])

@app.get("/")
async def root():
    return {"message": "欢迎使用{APP_NAME}！这是AI生成的应用。"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": "{APP_NAME}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
        '''
    
    def _get_docker_compose_template(self) -> str:
        return '''
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:8000
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://root:password@mysql:3306/{DB_NAME}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - mysql
      - redis

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE={DB_NAME}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  mysql_data:
        '''
    
    def _get_readme_template(self) -> str:
        return '''
# {APP_NAME}

这是由CloudCoder AI自动生成的应用程序。

## 技术栈
- 前端: React + TypeScript + Ant Design
- 后端: FastAPI + SQLAlchemy
- 数据库: MySQL 8.0
- 缓存: Redis
- 部署: Docker + Kubernetes

## 移动云资源配置
- ECS实例: 用于应用部署
- RDS数据库: MySQL数据存储
- Redis缓存: 会话和数据缓存
- OSS存储: 静态文件存储
- VPC网络: 安全网络隔离

## 快速开始

### 本地开发
```bash
# 启动所有服务
docker-compose up -d

# 访问应用
前端: http://localhost:3000
后端API: http://localhost:8000
API文档: http://localhost:8000/docs
```

### 部署到移动云
```bash
# 构建镜像
docker build -t {PROJECT_ID}-frontend ./frontend
docker build -t {PROJECT_ID}-backend ./backend

# 推送到移动云镜像仓库
docker push ecloud-registry.cn/{PROJECT_ID}-frontend
docker push ecloud-registry.cn/{PROJECT_ID}-backend

# Kubernetes部署
kubectl apply -f kubernetes/deployment.yaml
```

## AI生成说明
本应用由CloudCoder AI根据以下需求自动生成:
- 应用类型: 电商平台
- 核心功能: 商品管理、订单系统、用户管理
- 技术偏好: 现代化微服务架构
- 云平台: 移动云原生部署

生成时间: {GENERATION_TIME}
项目ID: {PROJECT_ID}
        '''
    
    # 其他模板方法简化实现
    def _get_product_list_template(self) -> str:
        return "// AI生成的商品列表组件"
    
    def _get_cart_template(self) -> str:
        return "// AI生成的购物车组件"
    
    def _get_order_template(self) -> str:
        return "// AI生成的订单组件"
    
    def _get_frontend_package_json(self) -> str:
        return '{"name": "frontend", "dependencies": {"react": "^18.0.0", "antd": "^5.0.0"}}'
    
    def _get_product_model_template(self) -> str:
        return "# AI生成的商品模型"
    
    def _get_order_model_template(self) -> str:
        return "# AI生成的订单模型"
    
    def _get_products_api_template(self) -> str:
        return "# AI生成的商品API"
    
    def _get_orders_api_template(self) -> str:
        return "# AI生成的订单API"
    
    def _get_backend_requirements(self) -> str:
        return "fastapi\nuvicorn\nsqlalchemy\nmysql-connector-python\nredis"
    
    def _get_database_schema(self) -> str:
        return "-- AI生成的数据库模式"
    
    def _get_k8s_deployment_template(self) -> str:
        return "# AI生成的Kubernetes部署配置"
    
    def _get_education_app_template(self) -> str:
        return "// AI生成的教育应用模板"
    
    def _get_course_list_template(self) -> str:
        return "// AI生成的课程列表组件"
    
    def _get_live_class_template(self) -> str:
        return "// AI生成的直播课堂组件"
    
    def _get_education_main_template(self) -> str:
        return "# AI生成的教育应用后端"
    
    def _get_course_model_template(self) -> str:
        return "# AI生成的课程模型"
    
    def _get_courses_api_template(self) -> str:
        return "# AI生成的课程API"
    
    def _get_education_schema(self) -> str:
        return "-- AI生成的教育数据库模式"
    
    def _get_education_docker_template(self) -> str:
        return "# AI生成的教育应用Docker配置"
    
    def _get_education_readme_template(self) -> str:
        return "# AI生成的教育应用README"

# 使用示例
if __name__ == "__main__":
    generator = CodeGenerator()
    
    # 生成电商应用
    project = generator.generate_project(
        requirement="我想要一个电商网站，支持用户注册登录、商品展示、购物车、订单管理",
        app_type="ecommerce",
        project_id="demo_123"
    )
    
    print(f"生成项目: {project.name}")
    print(f"技术栈: {project.tech_stack}")
    print(f"生成文件数: {len(project.files)}")
    print(f"云资源配置: {len(project.cloud_config)} 项")
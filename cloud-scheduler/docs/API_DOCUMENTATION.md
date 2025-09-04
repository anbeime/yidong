# CloudCoder API 文档

## 概述

CloudCoder提供RESTful API接口，支持自然语言代码生成、云资源管理、项目管理等核心功能。

**基础URL**: `http://localhost:8084/api`
**认证方式**: JWT Bearer Token
**数据格式**: JSON

---

## 认证接口

### 用户注册
```http
POST /api/auth/register
```

**请求体**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "success": true,
  "user_id": "uuid",
  "message": "用户注册成功"
}
```

### 用户登录
```http
POST /api/auth/login
```

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "success": true,
  "token": "jwt_token",
  "user_info": {
    "user_id": "uuid",
    "username": "string",
    "email": "string"
  }
}
```

---

## 代码生成接口

### 生成应用代码
```http
POST /api/generate
```

**请求头**:
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**请求体**:
```json
{
  "requirement": "创建一个电商平台，包含用户管理、商品展示、订单处理功能",
  "app_type": "ecommerce",
  "tech_stack": {
    "frontend": "react",
    "backend": "fastapi",
    "database": "mysql"
  },
  "features": [
    "user_management",
    "product_catalog",
    "order_processing",
    "payment_integration"
  ]
}
```

**响应**:
```json
{
  "success": true,
  "project_id": "uuid",
  "generation_status": "completed",
  "files": [
    {
      "path": "frontend/src/App.tsx",
      "content": "file_content",
      "size": 1024
    }
  ],
  "metadata": {
    "total_files": 23,
    "languages": ["typescript", "python"],
    "framework": "react_fastapi",
    "estimated_complexity": "medium"
  }
}
```

### 获取生成状态
```http
GET /api/generate/status/{project_id}
```

**响应**:
```json
{
  "success": true,
  "project_id": "uuid",
  "status": "generating|completed|failed",
  "progress": 85,
  "current_step": "生成后端API接口",
  "estimated_time_remaining": 30
}
```

---

## 项目管理接口

### 获取用户项目列表
```http
GET /api/projects
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `size`: 每页数量 (默认: 10)
- `app_type`: 应用类型筛选
- `status`: 项目状态筛选

**响应**:
```json
{
  "success": true,
  "projects": [
    {
      "project_id": "uuid",
      "name": "电商平台",
      "app_type": "ecommerce",
      "status": "completed",
      "created_at": "2025-08-25T10:00:00Z",
      "updated_at": "2025-08-25T12:00:00Z",
      "files_count": 23,
      "size": "2.5MB"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 10,
    "total": 15,
    "pages": 2
  }
}
```

### 获取项目详情
```http
GET /api/projects/{project_id}
```

**响应**:
```json
{
  "success": true,
  "project": {
    "project_id": "uuid",
    "name": "电商平台",
    "description": "包含用户管理、商品展示、订单处理的完整电商系统",
    "app_type": "ecommerce",
    "tech_stack": {
      "frontend": "react",
      "backend": "fastapi",
      "database": "mysql"
    },
    "files": [
      {
        "path": "frontend/src/App.tsx",
        "size": 1024,
        "modified_at": "2025-08-25T12:00:00Z"
      }
    ],
    "versions": [
      {
        "version": "1.0.0",
        "created_at": "2025-08-25T10:00:00Z",
        "changes": "初始版本"
      }
    ]
  }
}
```

### 下载项目文件
```http
GET /api/projects/{project_id}/download
```

**查询参数**:
- `format`: 下载格式 (zip|tar)
- `version`: 版本号 (可选)

**响应**: 二进制文件流

---

## 云资源管理接口

### 估算云资源成本
```http
POST /api/cloud/estimate
```

**请求体**:
```json
{
  "app_type": "ecommerce",
  "expected_users": 1000,
  "expected_traffic": "medium",
  "regions": ["beijing", "shanghai"],
  "services": {
    "compute": {
      "instance_type": "ecs.g6.large",
      "count": 2
    },
    "database": {
      "type": "mysql",
      "storage": "100GB",
      "instance_class": "db.mysql.s2.large"
    },
    "cache": {
      "type": "redis",
      "memory": "4GB"
    }
  }
}
```

**响应**:
```json
{
  "success": true,
  "estimation": {
    "monthly_cost": 1248.50,
    "currency": "CNY",
    "breakdown": {
      "compute": 800.00,
      "database": 300.00,
      "cache": 100.00,
      "network": 48.50
    },
    "optimizations": [
      {
        "type": "cost_saving",
        "description": "使用预付费实例可节省20%",
        "potential_savings": 160.00
      }
    ]
  }
}
```

### 部署到移动云
```http
POST /api/cloud/deploy
```

**请求体**:
```json
{
  "project_id": "uuid",
  "deployment_config": {
    "region": "beijing",
    "environment": "production",
    "auto_scaling": true,
    "backup_enabled": true
  },
  "resources": {
    "compute": {
      "instance_type": "ecs.g6.large",
      "count": 2
    },
    "database": {
      "type": "mysql",
      "storage": "100GB"
    }
  }
}
```

**响应**:
```json
{
  "success": true,
  "deployment_id": "uuid",
  "status": "deploying",
  "estimated_time": 600,
  "resources": [
    {
      "type": "ecs",
      "id": "i-abc123",
      "status": "creating"
    }
  ]
}
```

### 获取部署状态
```http
GET /api/cloud/deploy/{deployment_id}/status
```

**响应**:
```json
{
  "success": true,
  "deployment_id": "uuid",
  "status": "completed|deploying|failed",
  "progress": 100,
  "resources": [
    {
      "type": "ecs",
      "id": "i-abc123",
      "status": "running",
      "public_ip": "123.456.789.0",
      "private_ip": "10.0.0.1"
    }
  ],
  "endpoints": {
    "web": "http://123.456.789.0:80",
    "api": "http://123.456.789.0:8000"
  }
}
```

---

## 监控接口

### 获取资源监控数据
```http
GET /api/monitoring/resources/{deployment_id}
```

**查询参数**:
- `start_time`: 开始时间 (ISO 8601)
- `end_time`: 结束时间 (ISO 8601)
- `metrics`: 指标类型 (cpu,memory,disk,network)

**响应**:
```json
{
  "success": true,
  "metrics": {
    "cpu": [
      {
        "timestamp": "2025-08-25T12:00:00Z",
        "value": 45.2,
        "unit": "percent"
      }
    ],
    "memory": [
      {
        "timestamp": "2025-08-25T12:00:00Z",
        "value": 2048,
        "unit": "MB"
      }
    ]
  }
}
```

### 获取应用健康状态
```http
GET /api/monitoring/health/{deployment_id}
```

**响应**:
```json
{
  "success": true,
  "health": {
    "overall_status": "healthy|warning|critical",
    "services": [
      {
        "name": "web-frontend",
        "status": "healthy",
        "response_time": 120,
        "error_rate": 0.1
      },
      {
        "name": "api-backend",
        "status": "healthy",
        "response_time": 80,
        "error_rate": 0.0
      }
    ],
    "last_check": "2025-08-25T12:00:00Z"
  }
}
```

---

## 错误响应格式

所有错误响应都遵循统一格式：

```json
{
  "success": false,
  "error_code": "ERROR_CODE",
  "error_type": "validation_error|authentication_error|system_error",
  "title": "错误标题",
  "message": "详细错误信息",
  "suggestion": "解决建议",
  "timestamp": "2025-08-25T12:00:00Z",
  "support_contact": "support@cloudcoder.com"
}
```

### 常见错误码

| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| `AUTHENTICATION_FAILED` | 401 | 认证失败 |
| `PERMISSION_DENIED` | 403 | 权限不足 |
| `RESOURCE_NOT_FOUND` | 404 | 资源不存在 |
| `VALIDATION_ERROR` | 400 | 请求参数验证失败 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `INTERNAL_SERVER_ERROR` | 500 | 服务器内部错误 |

---

## 请求限制

### 速率限制
- **认证接口**: 每分钟最多10次请求
- **代码生成**: 每小时最多5次请求
- **其他接口**: 每分钟最多100次请求

### 数据限制
- **单个项目最大文件数**: 100个
- **单个文件最大大小**: 1MB
- **需求描述最大长度**: 2000字符
- **项目名称最大长度**: 100字符

---

## SDK 和示例

### Python SDK 示例

```python
import requests

class CloudCoderClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def generate_code(self, requirement, app_type='default'):
        response = requests.post(
            f'{self.base_url}/api/generate',
            json={
                'requirement': requirement,
                'app_type': app_type
            },
            headers=self.headers
        )
        return response.json()
    
    def get_projects(self):
        response = requests.get(
            f'{self.base_url}/api/projects',
            headers=self.headers
        )
        return response.json()

# 使用示例
client = CloudCoderClient('http://localhost:8084', 'your_jwt_token')
result = client.generate_code('创建一个博客系统')
print(result)
```

### JavaScript SDK 示例

```javascript
class CloudCoderClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.token = token;
    }
    
    async generateCode(requirement, appType = 'default') {
        const response = await fetch(`${this.baseUrl}/api/generate`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                requirement,
                app_type: appType
            })
        });
        return await response.json();
    }
    
    async getProjects() {
        const response = await fetch(`${this.baseUrl}/api/projects`, {
            headers: {
                'Authorization': `Bearer ${this.token}`
            }
        });
        return await response.json();
    }
}

// 使用示例
const client = new CloudCoderClient('http://localhost:8084', 'your_jwt_token');
client.generateCode('创建一个电商平台').then(result => {
    console.log(result);
});
```

---

## 更新日志

### v1.0.0 (2025-08-25)
- 初始版本发布
- 支持基础代码生成功能
- 集成移动云API
- 提供项目管理功能

---

## 支持

如有问题或建议，请联系：
- **邮箱**: support@cloudcoder.com
- **文档**: https://docs.cloudcoder.com
- **GitHub**: https://github.com/cloudcoder/api
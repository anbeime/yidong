# 云智调度 - 基于AI的算网资源统一编排平台

## 项目简介

本项目是参加移动云开发者大赛的作品，实现了基于AI的智能算网资源调度平台，能够自动预测资源需求，优化资源分配，降低云计算成本。

## 技术架构

- **后端**: FastAPI + Python 3.9+
- **前端**: React + TypeScript + Ant Design
- **数据库**: MySQL + Redis
- **AI/ML**: PyTorch + scikit-learn
- **部署**: Docker + 移动云容器服务

## 项目结构

```
cloud-scheduler/
├── backend/                 # 后端服务
│   ├── app/                # 应用主体
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务逻辑
│   │   └── utils/         # 工具函数
│   ├── alembic/           # 数据库迁移
│   ├── tests/             # 测试文件
│   └── requirements.txt   # Python依赖
├── frontend/               # 前端应用
│   ├── src/               # 源代码
│   │   ├── components/    # React组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API服务
│   │   └── utils/         # 工具函数
│   ├── public/            # 静态资源
│   └── package.json       # Node.js依赖
├── ai-engine/             # AI算法引擎
│   ├── models/            # 机器学习模型
│   ├── algorithms/        # 调度算法
│   ├── training/          # 模型训练
│   └── prediction/        # 预测服务
├── deployment/            # 部署配置
│   ├── docker/            # Docker配置
│   ├── kubernetes/        # K8s配置
│   └── scripts/           # 部署脚本
├── docs/                  # 项目文档
├── tests/                 # 集成测试
└── docker-compose.yml     # 本地开发环境
```

## 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd cloud-scheduler

# 安装依赖
pip install -r backend/requirements.txt
cd frontend && npm install
```

### 2. 配置移动云认证信息
在项目根目录创建 `.env` 文件并配置移动云认证信息：

```env
# 移动云配置
ECLOUD_ACCESS_KEY=ed7bbd03fad34980834cae597a02cbfc
ECLOUD_SECRET_KEY=9ae0582e1e9e4f40ab5c68b744829c61
ECLOUD_REGION=cn-north-1
```

或者通过环境变量设置：
```bash
export ECLOUD_ACCESS_KEY=ed7bbd03fad34980834cae597a02cbfc
export ECLOUD_SECRET_KEY=9ae0582e1e9e4f40ab5c68b744829c61
```

### 3. 启动服务
```bash
# 启动后端服务
cd backend && uvicorn app.main:app --reload

# 启动前端服务
cd frontend && npm start
```

### 4. Docker部署
```bash
docker-compose up -d
```

## 公网IP部署

项目已配置公网IP地址 `36.138.182.96`，详细部署指南请参考 [PUBLIC_IP_DEPLOYMENT_GUIDE.md](file:///C:/D/compet/yidong/cloud-scheduler/PUBLIC_IP_DEPLOYMENT_GUIDE.md)。

部署完成后，可通过以下地址访问：
- **前端管理界面**: http://36.138.182.96:3000
- **后端API文档**: http://36.138.182.96:8000/docs
- **AI引擎接口**: http://36.138.182.96:8001/docs

## 核心功能

1. **智能资源预测** - 基于历史数据预测资源需求
2. **自动调度优化** - AI驱动的资源分配策略
3. **实时监控** - 资源使用情况实时展示
4. **成本分析** - 多维度成本优化建议
5. **告警通知** - 异常情况自动告警

## 开发团队

- 项目负责人：[你的姓名]
- 开发团队：AI助手团队

## 许可证

MIT License
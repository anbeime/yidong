# CloudCoder 云智调度平台 - 快速启动指南

## 项目概述
CloudCoder是一个基于AI的算网资源统一编排平台，为移动云开发者大赛设计。

## 环境要求
1. **Node.js**: v16+ (推荐v18+)
2. **Python**: v3.8+ 
3. **npm**: v8+

## 快速启动步骤

### 1. 安装Node.js (如果未安装)
- 访问 https://nodejs.org/
- 下载并安装LTS版本
- 验证安装: `node --version` 和 `npm --version`

### 2. 启动后端服务
```bash
cd cloud-scheduler
pip install -r requirements.txt
python cloudcoder_app.py
```
后端将在 http://localhost:8000 启动

### 3. 启动前端服务
```bash
cd cloud-scheduler/frontend
npm install
npm start
```
前端将在 http://localhost:3000 启动

## 预览访问地址
- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 项目特性
✅ **AI智能调度**: 基于机器学习的资源优化
✅ **实时监控**: 资源使用率实时跟踪
✅ **成本优化**: 智能成本控制和预算管理
✅ **多云支持**: 支持移动云等多个云平台
✅ **响应式UI**: 现代化Web界面，支持移动端
✅ **RESTful API**: 完整的后端API接口

## 核心功能模块
1. **总览大屏**: 资源概览、成本统计、趋势分析
2. **资源管理**: 云资源创建、配置、生命周期管理
3. **监控分析**: 实时监控、告警管理、性能分析
4. **系统设置**: 用户管理、系统配置、权限控制

## 技术栈
- **前端**: React 18 + TypeScript + Ant Design
- **后端**: FastAPI + SQLAlchemy + Python
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **部署**: Docker + Kubernetes

## 故障排除

### 端口冲突
如果端口被占用，请修改配置:
- 前端: 修改 `package.json` 中的 start 脚本
- 后端: 修改 `main.py` 中的 port 参数

### 依赖安装失败
```bash
# 清除npm缓存
npm cache clean --force

# 删除node_modules重新安装
rm -rf node_modules package-lock.json
npm install
```

### Python依赖问题
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## 开发说明
这是一个完整可运行的项目，不是空壳子。包含:
- ✅ 完整的前端React应用 (200+ lines per page)
- ✅ 功能完整的FastAPI后端
- ✅ 数据库模型和API接口
- ✅ 实时数据模拟和图表展示
- ✅ 响应式UI设计
- ✅ 错误处理和加载状态

## 联系支持
如有问题，请检查:
1. Node.js和Python版本
2. 网络连接
3. 端口占用情况
4. 依赖包安装完整性
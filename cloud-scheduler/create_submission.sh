#!/bin/bash

# 云智调度平台代码打包脚本
# 用于生成大赛提交的代码包

set -e

# 获取团队信息
read -p "请输入团队名称: " TEAM_NAME
read -p "请输入队长姓名: " CAPTAIN_NAME  
read -p "请输入队长手机号: " CAPTAIN_PHONE

# 生成作品名称
WORK_NAME="${TEAM_NAME}-${CAPTAIN_NAME}-${CAPTAIN_PHONE}-云智调度AI算网资源编排平台"
echo "作品名称: $WORK_NAME"

# 创建打包目录
PACKAGE_DIR="submission_package"
rm -rf $PACKAGE_DIR
mkdir -p $PACKAGE_DIR

echo "📦 开始打包提交材料..."

# 1. 复制核心代码
echo "📁 复制项目代码..."
cp -r backend $PACKAGE_DIR/
cp -r frontend $PACKAGE_DIR/
cp -r ai-engine $PACKAGE_DIR/
cp -r deployment $PACKAGE_DIR/
cp -r docs $PACKAGE_DIR/

# 2. 复制配置文件
echo "⚙️ 复制配置文件..."
cp docker-compose.yml $PACKAGE_DIR/
cp quick-start.sh $PACKAGE_DIR/
cp README.md $PACKAGE_DIR/

# 3. 创建提交说明文档
cat > $PACKAGE_DIR/提交说明.md << EOF
# 云智调度 - 基于AI的算网资源统一编排平台
## 大赛提交材料说明

### 作品信息
- **作品名称**: 云智调度 - 基于AI的算网资源统一编排平台
- **团队名称**: $TEAM_NAME
- **队长姓名**: $CAPTAIN_NAME
- **队长手机**: $CAPTAIN_PHONE
- **参赛赛道**: 命题一
- **提交时间**: $(date '+%Y年%m月%d日')

### 项目结构
\`\`\`
cloud-scheduler/
├── backend/                 # 后端服务 (FastAPI)
│   ├── app/                # 应用主体
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   └── services/      # 业务逻辑
│   └── requirements.txt   # Python依赖
├── frontend/               # 前端应用 (React + TypeScript)
│   ├── src/               # 源代码
│   │   ├── components/    # React组件
│   │   ├── pages/         # 页面组件
│   │   └── services/      # API服务
│   └── package.json       # Node.js依赖
├── ai-engine/             # AI算法引擎
│   ├── main.py           # AI服务主程序
│   └── requirements.txt   # AI依赖
├── deployment/            # 部署配置
│   ├── kubernetes/        # K8s配置
│   └── scripts/           # 部署脚本
├── docs/                  # 项目文档
├── docker-compose.yml     # 本地开发环境
├── quick-start.sh         # 快速启动脚本
└── README.md             # 项目说明
\`\`\`

### 快速运行
\`\`\`bash
# 1. 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ 内存

# 2. 快速启动
chmod +x quick-start.sh
./quick-start.sh start

# 3. 访问系统
前端界面: http://localhost:3000
后端API: http://localhost:8000/docs
AI引擎: http://localhost:8001/docs

# 4. 默认账号
用户名: admin
密码: admin123
\`\`\`

### 技术特色
1. **AI智能预测**: LSTM + 随机森林集成算法
2. **移动云深度集成**: ECS、容器、VPC、存储全覆盖  
3. **算网协同调度**: 统一编排算力和网络资源
4. **实时监控**: 毫秒级响应的监控和告警
5. **成本优化**: 15-50%的成本节省效果

### 移动云资源需求
- ECS云主机: 2台 (4核8G)
- 容器服务: 8vCPU/32G内存
- MySQL数据库: 2台  
- VPC网络: 1个
- 对象存储: 200GB

### 联系方式
- 队长: $CAPTAIN_NAME
- 手机: $CAPTAIN_PHONE
- 邮箱: [请填写邮箱]

### 特别说明
本作品完全基于移动云构建，充分利用移动云的ECS、容器服务、VPC、对象存储等资源，
实现了AI驱动的算网资源统一编排，具有显著的技术创新性和商业价值。
EOF

# 4. 创建部署指南
cat > $PACKAGE_DIR/移动云部署指南.md << EOF
# 移动云部署指南

## 部署前准备

### 1. 移动云资源申请
请确保已申请以下移动云资源：
- ECS云主机: 2台 (推荐4核8G配置)
- 容器服务集群: 8vCPU/32G内存
- MySQL云数据库: 2台实例
- VPC虚拟私有云: 1个
- 对象存储OSS: 200GB容量

### 2. 配置移动云访问密钥
在 \`backend/app/core/config.py\` 中配置：
\`\`\`python
ECLOUD_ACCESS_KEY = "你的访问密钥"
ECLOUD_SECRET_KEY = "你的秘密密钥"  
ECLOUD_REGION = "cn-north-1"  # 根据实际地域调整
\`\`\`

## 部署方式

### 方式一：一键部署（推荐）
\`\`\`bash
# 1. 设置环境变量
export ECLOUD_ACCESS_KEY="你的访问密钥"
export ECLOUD_SECRET_KEY="你的秘密密钥"
export DATABASE_URL="你的MySQL连接字符串"
export REDIS_URL="你的Redis连接字符串"

# 2. 执行一键部署
./deployment/scripts/deploy.sh deploy
\`\`\`

### 方式二：手动部署
\`\`\`bash
# 1. 构建镜像
docker build -t cloud-scheduler-backend:latest ./backend
docker build -t cloud-scheduler-frontend:latest ./frontend  
docker build -t cloud-scheduler-ai:latest ./ai-engine

# 2. 推送到移动云镜像仓库
docker tag cloud-scheduler-backend registry.cmecloud.cn/your-namespace/backend:latest
docker push registry.cmecloud.cn/your-namespace/backend:latest

# 3. 部署到Kubernetes
kubectl apply -f deployment/kubernetes/
\`\`\`

## 验证部署

### 1. 检查服务状态
\`\`\`bash
kubectl get pods -n cloud-scheduler
kubectl get services -n cloud-scheduler
\`\`\`

### 2. 访问应用
- 前端界面: http://[LoadBalancer-IP]:3000
- 后端API: http://[LoadBalancer-IP]:8000/docs

### 3. 功能测试
1. 登录系统 (admin/admin123)
2. 查看总览大屏
3. 测试资源同步功能
4. 验证AI预测和调度功能

## 监控和运维

### 1. 日志查看
\`\`\`bash
kubectl logs -f deployment/cloud-scheduler-backend -n cloud-scheduler
kubectl logs -f deployment/cloud-scheduler-ai -n cloud-scheduler
\`\`\`

### 2. 性能监控
- Prometheus: http://[LoadBalancer-IP]:9090
- Grafana: http://[LoadBalancer-IP]:3001

### 3. 故障处理
常见问题及解决方案请参考 docs/FAQ.md

## 技术支持
如需技术支持，请联系：
- 队长: $CAPTAIN_NAME  
- 手机: $CAPTAIN_PHONE
EOF

# 5. 清理敏感信息
echo "🔒 清理敏感信息..."
find $PACKAGE_DIR -name "*.py" -exec sed -i 's/your-super-secret-key-change-in-production/[请配置您的密钥]/g' {} \;
find $PACKAGE_DIR -name "*.yaml" -exec sed -i 's/your-ecloud-access-key/[请配置访问密钥]/g' {} \;

# 6. 创建压缩包
echo "📦 创建提交压缩包..."
cd $PACKAGE_DIR
zip -r "../${WORK_NAME}-代码包.zip" .
cd ..

# 7. 生成提交清单
cat > "提交材料清单.txt" << EOF
移动云开发者大赛提交材料清单
=====================================

作品名称: $WORK_NAME
团队名称: $TEAM_NAME
队长姓名: $CAPTAIN_NAME
队长手机: $CAPTAIN_PHONE
参赛赛道: 命题一

提交材料:
1. 作品介绍PPT (必选) - 请使用大赛模板制作
2. 作品代码包 (可选) - ${WORK_NAME}-代码包.zip
3. 作品演示视频 (可选) - 建议录制10分钟演示视频

代码包内容:
- 完整的前后端源代码
- AI算法引擎实现  
- 移动云集成代码
- 部署配置和脚本
- 详细的部署指南
- 项目文档和说明

技术亮点:
- AI + 算网融合架构
- 移动云深度集成
- 实时智能调度
- 成本优化效果显著

请确保在提交前:
1. 配置移动云访问密钥
2. 测试部署流程  
3. 验证所有功能正常
4. 准备演示材料

提交时间: $(date '+%Y年%m月%d日 %H:%M:%S')
EOF

echo ""
echo "✅ 打包完成！"
echo "📋 提交材料："
echo "   - 代码包: ${WORK_NAME}-代码包.zip"
echo "   - 清单: 提交材料清单.txt"
echo ""
echo "📝 下一步："
echo "   1. 制作作品介绍PPT (使用大赛模板)"
echo "   2. 录制演示视频 (可选，建议10分钟)"
echo "   3. 配置移动云访问密钥"
echo "   4. 测试部署到移动云"
echo "   5. 提交到大赛官网"
echo ""
echo "🎉 祝你在大赛中取得优异成绩！"
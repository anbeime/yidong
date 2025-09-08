#!/bin/bash

# 生成项目部署脚本
# 用于在云主机上部署CloudCoder生成的应用

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查参数
if [ $# -lt 2 ]; then
    echo -e "${RED}用法: $0 <项目ID> <部署目录>${NC}"
    echo "示例: $0 ae14a4cb /var/www/myapp"
    exit 1
fi

PROJECT_ID=$1
DEPLOY_DIR=$2
PROJECT_NAME="cloudcoder_app_${PROJECT_ID}"

echo -e "${GREEN}开始部署生成的项目: ${PROJECT_ID}${NC}"
echo -e "${GREEN}部署目录: ${DEPLOY_DIR}${NC}"

# 创建部署目录
echo -e "${YELLOW}创建部署目录...${NC}"
sudo mkdir -p ${DEPLOY_DIR}
sudo chown $USER:$USER ${DEPLOY_DIR}

# 复制项目文件（这里假设项目文件已经通过其他方式传输到云主机）
# 在实际使用中，您可能需要通过scp或其他方式将项目文件传输到云主机
echo -e "${YELLOW}检查项目文件...${NC}"
if [ ! -d "${PROJECT_NAME}" ]; then
    echo -e "${RED}错误: 项目目录 ${PROJECT_NAME} 不存在${NC}"
    echo "请确保项目文件已传输到当前目录"
    exit 1
fi

# 复制项目文件到部署目录
echo -e "${YELLOW}复制项目文件到部署目录...${NC}"
cp -r ${PROJECT_NAME}/* ${DEPLOY_DIR}/

# 进入部署目录
cd ${DEPLOY_DIR}

# 检查是否存在docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    echo -e "${YELLOW}使用Docker Compose部署...${NC}"
    
    # 构建并启动服务
    docker-compose up -d --build
    
    echo -e "${GREEN}项目已通过Docker Compose部署成功!${NC}"
    echo -e "${GREEN}访问地址: http://<your-server-ip>:3000${NC}"
else
    # 分别部署前后端
    echo -e "${YELLOW}分别部署前后端服务...${NC}"
    
    # 部署后端
    if [ -d "backend" ]; then
        echo -e "${YELLOW}部署后端服务...${NC}"
        cd backend
        
        # 安装Python依赖
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        fi
        
        # 启动后端服务（使用screen或nohup后台运行）
        nohup python main.py > backend.log 2>&1 &
        BACKEND_PID=$!
        echo -e "${GREEN}后端服务已启动，PID: ${BACKEND_PID}${NC}"
        
        cd ..
    fi
    
    # 部署前端
    if [ -d "frontend" ]; then
        echo -e "${YELLOW}部署前端服务...${NC}"
        cd frontend
        
        # 安装Node.js依赖
        if [ -f "package.json" ]; then
            npm install
        fi
        
        # 构建前端
        npm run build
        
        # 启动前端服务
        nohup npm start > frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo -e "${GREEN}前端服务已启动，PID: ${FRONTEND_PID}${NC}"
        
        cd ..
    fi
    
    echo -e "${GREEN}项目已分别部署成功!${NC}"
    echo -e "${GREEN}后端访问地址: http://<your-server-ip>:8000${NC}"
    echo -e "${GREEN}前端访问地址: http://<your-server-ip>:3000${NC}"
fi

echo -e "${GREEN}部署完成!${NC}"
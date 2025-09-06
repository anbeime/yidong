#!/bin/bash

# CloudCoder 一键部署脚本
# 作者: [您的姓名/团队名]
# 描述: 用于在移动云 Ubuntu 24.04 服务器上自动部署 AI 生成的全栈应用
# 使用: ./deploy.sh

set -e # 遇到任何错误立即退出脚本

echo "🚀 开始部署 CloudCoder 应用..."
echo "📋 服务器信息: $(uname -a)"
echo "🌐 公网地址: 36.138.182.96"

# 1. 更新系统及基础软件包
echo "🔁 步骤 1/6: 更新系统软件包..."
apt update > /dev/null 2>&1
apt upgrade -y > /dev/null 2>&1
echo "✅ 系统更新完成"

# 2. 安装核心依赖
echo "📦 步骤 2/6: 安装核心依赖 (Docker, Python, Node.js, Git)..."
apt install -y \
    docker.io \
    docker-compose \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    git \
    curl \
    wget > /dev/null 2>&1

# 启动并启用 Docker 服务
systemctl start docker
systemctl enable docker > /dev/null 2>&1
echo "✅ 核心依赖安装完成"

# 3. 拉取或更新项目代码
echo "📂 步骤 3/6: 获取最新项目代码..."
cd /root

if [ -d "yidong" ]; then
    echo "📁 项目目录已存在，尝试更新..."
    cd yidong
    git stash > /dev/null 2>&1 # 暂存本地更改
    git pull origin main > /dev/null 2>&1
    echo "✅ 代码更新完成"
else
    echo "📥 克隆新项目..."
    git clone https://github.com/anbeime/yidong.git  > /dev/null 2>&1
    cd yidong
    echo "✅ 代码克隆完成"
fi

# 4. 根据项目类型安装特定依赖
echo "🔧 步骤 4/6: 安装项目特定依赖..."

# 检查并安装 Python 依赖
if [ -f "requirements.txt" ]; then
    echo "🐍 发现 Python 依赖文件，正在安装..."
    pip3 install -r requirements.txt > /dev/null 2>&1
    echo "✅ Python 依赖安装完成"
fi

# 检查并安装 Node.js 依赖
if [ -f "package.json" ]; then
    echo "⬢ 发现 Node.js 依赖文件，正在安装..."
    npm install > /dev/null 2>&1
    echo "✅ Node.js 依赖安装完成"
fi

# 5. 启动服务
echo "🚀 步骤 5/6: 启动应用服务..."

# 优先使用 Docker Compose
if [ -f "docker-compose.yml" ]; then
    echo "🐳 使用 Docker Compose 启动服务..."
    docker-compose down > /dev/null 2>&1
    docker-compose up -d --build > /dev/null 2>&1
    echo "✅ Docker 服务已启动"

# 其次检查 Python 应用
elif [ -f "app.py" ]; then
    echo "🐍 启动 Python 应用 (app.py)..."
    # 停止可能正在运行的旧进程
    pkill -f "python3 app.py" || true
    nohup python3 app.py > app.log 2>&1 &
    echo "✅ Python 应用已启动，日志见 app.log"

elif [ -f "main.py" ]; then
    echo "🐍 启动 Python 应用 (main.py)..."
    pkill -f "python3 main.py" || true
    nohup python3 main.py > main.log 2>&1 &
    echo "✅ Python 应用已启动，日志见 main.log"

else
    echo "⚠️  未识别到标准启动文件，请手动启动服务"
    echo "📁 当前目录内容:"
    ls -la
fi

# 6. 验证部署
echo "🔍 步骤 6/6: 验证部署状态..."
sleep 3 # 等待服务启动

echo "📊 系统资源状态:"
echo "💾 磁盘使用: $(df -h | grep '/$' | awk '{print $5}')"
echo "🧠 内存使用: $(free -h | grep Mem | awk '{print $3"/"$2}')"
echo "🔥 CPU 使用: $(top -bn1 | grep load | awk '{printf "%.2f", $(NF-2)}')"

echo "🌐 网络监听状态:"
netstat -tulpn | grep :80 || true
netstat -tulpn | grep :8000 || true
netstat -tulpn | grep :3000 || true

echo ""
echo "🎉 部署完成!"
echo "💡 下一步操作:"
echo "   1. 访问应用: http://36.138.182.96:8000  (或您应用的实际端口)"
echo "   2. 查看实时日志: tail -f /root/yidong/*.log"
echo "   3. 查看 Docker 容器: docker ps -a"
echo "   4. 如需重新部署，只需再次运行 ./deploy.sh"
echo ""
echo "⚠️  注意: 如果您的应用使用非标准端口，请确保移动云安全组已开放对应端口!"

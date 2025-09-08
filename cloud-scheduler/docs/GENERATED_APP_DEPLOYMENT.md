# 生成应用云主机部署指南

本文档介绍了如何在云主机上部署CloudCoder生成的应用。

## 部署方式概述

CloudCoder生成的应用支持两种部署方式：

1. **Docker Compose部署**（推荐）：一键部署，无需手动安装依赖
2. **手动部署**：分别部署前后端服务，需要手动安装依赖

## 部署前准备

### 1. 云主机环境要求

- 操作系统：Ubuntu 18.04+ 或 CentOS 7+
- 内存：至少4GB
- 存储：至少20GB可用空间
- 网络：可访问外网以下载依赖

### 2. 必需软件安装

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose git

# CentOS/RHEL
sudo yum install -y docker docker-compose git

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker
```

## 部署步骤

### 方式一：Docker Compose部署（推荐）

1. **下载生成的项目代码**
   - 在CloudCoder界面中点击"📦 下载代码"按钮
   - 将下载的ZIP文件传输到云主机

2. **解压项目文件**
   ```bash
   unzip cloudcoder_app_<项目ID>.zip
   cd cloudcoder_app_<项目ID>
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

4. **验证部署**
   ```bash
   # 查看服务状态
   docker-compose ps
   
   # 查看日志
   docker-compose logs
   ```

5. **访问应用**
   - 前端：http://<云主机IP>:3000
   - 后端API：http://<云主机IP>:8000

### 方式二：手动部署

1. **下载并解压项目代码**（同上）

2. **部署后端服务**
   ```bash
   cd backend
   
   # 安装Python依赖
   pip install -r requirements.txt
   
   # 启动后端服务
   nohup python main.py > backend.log 2>&1 &
   ```

3. **部署前端服务**
   ```bash
   cd frontend
   
   # 安装Node.js依赖
   npm install
   
   # 构建前端
   npm run build
   
   # 启动前端服务
   nohup npm start > frontend.log 2>&1 &
   ```

4. **访问应用**
   - 前端：http://<云主机IP>:3000
   - 后端API：http://<云主机IP>:8000

## 在线预览和修改

CloudCoder提供了在线文件浏览器和编辑器功能：

1. 在应用详情页面点击"📁 浏览文件"按钮
2. 在文件浏览器中选择要查看或编辑的文件
3. 在右侧编辑器中查看和修改文件内容
4. 点击"💾 保存文件"按钮保存修改

## 常见问题

### 1. 端口被占用
```bash
# 查看端口占用情况
sudo netstat -tlnp | grep :3000
sudo netstat -tlnp | grep :8000

# 杀掉占用端口的进程
sudo kill -9 <进程ID>
```

### 2. Docker权限问题
```bash
# 将当前用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker
```

### 3. 内存不足
```bash
# 增加swap空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 监控和维护

### 查看服务状态
```bash
# Docker Compose方式
docker-compose ps

# 手动部署方式
ps aux | grep python
ps aux | grep node
```

### 查看日志
```bash
# Docker Compose方式
docker-compose logs backend
docker-compose logs frontend

# 手动部署方式
tail -f backend.log
tail -f frontend.log
```

### 重启服务
```bash
# Docker Compose方式
docker-compose restart

# 手动部署方式
# 先杀掉旧进程，再重新启动
```

## 安全建议

1. **使用HTTPS**：在生产环境中配置SSL证书
2. **防火墙配置**：只开放必要的端口
3. **定期更新**：定期更新系统和依赖包
4. **备份数据**：定期备份重要数据和配置文件

## 性能优化

1. **使用Nginx反向代理**：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /api/ {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **启用Gzip压缩**：
   ```nginx
   gzip on;
   gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
   ```

3. **使用CDN加速静态资源**：
   - 将前端构建后的静态资源部署到CDN
   - 修改前端配置指向CDN地址

通过以上步骤，您可以成功在云主机上部署和运行CloudCoder生成的应用，并根据需要进行预览和修改。
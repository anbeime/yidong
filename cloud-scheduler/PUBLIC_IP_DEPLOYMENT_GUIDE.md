# 公网IP部署指南

本指南将帮助您将云智调度平台部署到具有公网IP的云主机上，使外部用户可以通过公网IP访问应用。

## 部署环境要求

- Ubuntu 24.04 64位操作系统
- 公网IP地址：36.138.182.96
- CPU和内存配置：8核32GB
- 系统盘：200GB
- 公网带宽：10 Mbps

## 部署步骤

### 1. 环境准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
sudo apt install docker.io -y

# 安装Docker Compose
sudo apt install docker-compose -y

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker
```

### 2. 配置防火墙

```bash
# 开放必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 3000/tcp  # 前端应用
sudo ufw allow 8000/tcp  # 后端API
sudo ufw allow 8001/tcp  # AI引擎
sudo ufw allow 3306/tcp  # MySQL
sudo ufw allow 6379/tcp  # Redis

# 启用防火墙
sudo ufw enable
```

### 3. 配置移动云认证信息

项目已配置以下移动云认证信息：
- **ECLOUD_ACCESS_KEY**: `ed7bbd03fad34980834cae597a02cbfc`
- **ECLOUD_SECRET_KEY**: `9ae0582e1e9e4f40ab5c68b744829c61`
- **ECLOUD_REGION**: `cn-north-1`

### 4. 启动服务

```bash
# 克隆项目代码（如果尚未克隆）
git clone <repository-url>
cd cloud-scheduler

# 使用快速启动脚本启动服务
./quick-start.sh start
```

### 5. 验证部署

启动完成后，您可以通过以下地址访问应用：

- **前端管理界面**: http://36.138.182.96:3000
- **后端API文档**: http://36.138.182.96:8000/docs
- **AI引擎接口**: http://36.138.182.96:8001/docs

默认登录账号：
- **用户名**: admin
- **密码**: admin123

## 配置说明

### 已更新的配置文件

1. **[.env](file:///C:/D/compet/yidong/cloud-scheduler/.env) 文件**:
   ```env
   REACT_APP_API_URL=http://36.138.182.96:8000
   ```

2. **[docker-compose.yml](file:///C:/D/compet/yidong/cloud-scheduler/docker-compose.yml) 文件**:
   ```yaml
   frontend:
     environment:
       - REACT_APP_API_URL=http://36.138.182.96:8000
   ```

3. **[deployment/kubernetes/deployment.yaml](file:///C:/D/compet/yidong/cloud-scheduler/deployment/kubernetes/deployment.yaml) 文件**:
   ```yaml
   frontend:
     env:
       - name: REACT_APP_API_URL
         value: "http://36.138.182.96:8000"
   ```

4. **[backend/app/core/config.py](file:///C:/D/compet/yidong/cloud-scheduler/backend/app/core/config.py) 文件**:
   ```python
   ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://36.138.182.96:3000", "http://36.138.182.96", "*"]
   ```

## 故障排除

### 1. 无法访问应用

- 检查防火墙设置，确保相应端口已开放
- 检查Docker容器是否正常运行：`docker-compose ps`
- 查看服务日志：`docker-compose logs -f`

### 2. 前端无法连接后端API

- 检查 [REACT_APP_API_URL](file:///C:/D/compet/yidong/cloud-scheduler/.env#L24-L24) 配置是否正确
- 确保后端服务已正常启动并监听8000端口
- 检查CORS配置是否允许来自前端的请求

### 3. 移动云服务无法访问

- 验证移动云认证信息是否正确配置
- 检查网络连接是否能访问移动云API端点
- 确认公网IP是否已在移动云控制台添加到白名单

## 安全建议

1. **修改默认密码**：部署后立即修改admin用户的默认密码
2. **配置SSL证书**：为生产环境配置HTTPS
3. **限制访问来源**：根据实际需求调整ALLOWED_HOSTS配置
4. **定期更新**：定期更新系统和应用依赖包
5. **监控日志**：定期检查应用日志，及时发现异常行为

## 技术支持

如需技术支持，请参考以下文档：
- [docs/DEVELOPER_GUIDE.md](file:///C:/D/compet/yidong/cloud-scheduler/docs/DEVELOPER_GUIDE.md)
- [docs/ECLOUD_DEPLOYMENT_CHECKLIST.md](file:///C:/D/compet/yidong/cloud-scheduler/docs/ECLOUD_DEPLOYMENT_CHECKLIST.md)
- [DEMO_SCRIPT.md](file:///C:/D/compet/yidong/cloud-scheduler/DEMO_SCRIPT.md)
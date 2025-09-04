#!/bin/bash

# 云智调度平台部署脚本
# 适用于移动云容器服务部署

set -e

echo "🚀 开始部署云智调度平台..."

# 检查必要的环境变量
check_env() {
    echo "📋 检查环境变量..."
    
    required_vars=(
        "DATABASE_URL"
        "REDIS_URL" 
        "ECLOUD_ACCESS_KEY"
        "ECLOUD_SECRET_KEY"
        "SECRET_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo "❌ 环境变量 $var 未设置"
            exit 1
        fi
    done
    
    echo "✅ 环境变量检查通过"
}

# 构建Docker镜像
build_images() {
    echo "🏗️ 构建Docker镜像..."
    
    # 构建后端镜像
    echo "构建后端服务镜像..."
    docker build -t cloud-scheduler-backend:latest ./backend
    
    # 构建AI引擎镜像
    echo "构建AI引擎镜像..."
    docker build -t cloud-scheduler-ai:latest ./ai-engine
    
    # 构建前端镜像
    echo "构建前端服务镜像..."
    docker build -t cloud-scheduler-frontend:latest ./frontend
    
    echo "✅ 镜像构建完成"
}

# 推送镜像到移动云容器镜像仓库
push_images() {
    echo "📦 推送镜像到容器镜像仓库..."
    
    # 设置镜像仓库地址
    REGISTRY_URL=${REGISTRY_URL:-"registry.cmecloud.cn/cloud-scheduler"}
    
    # 标记并推送镜像
    docker tag cloud-scheduler-backend:latest $REGISTRY_URL/backend:latest
    docker tag cloud-scheduler-ai:latest $REGISTRY_URL/ai-engine:latest
    docker tag cloud-scheduler-frontend:latest $REGISTRY_URL/frontend:latest
    
    docker push $REGISTRY_URL/backend:latest
    docker push $REGISTRY_URL/ai-engine:latest
    docker push $REGISTRY_URL/frontend:latest
    
    echo "✅ 镜像推送完成"
}

# 部署到Kubernetes
deploy_k8s() {
    echo "☸️ 部署到Kubernetes集群..."
    
    # 创建命名空间
    kubectl create namespace cloud-scheduler --dry-run=client -o yaml | kubectl apply -f -
    
    # 应用配置
    kubectl apply -f deployment/kubernetes/ -n cloud-scheduler
    
    # 等待部署完成
    echo "⏳ 等待服务启动..."
    kubectl wait --for=condition=ready pod -l app=cloud-scheduler -n cloud-scheduler --timeout=300s
    
    # 获取服务状态
    kubectl get pods -n cloud-scheduler
    kubectl get services -n cloud-scheduler
    
    echo "✅ Kubernetes部署完成"
}

# 初始化数据库
init_database() {
    echo "🗄️ 初始化数据库..."
    
    # 等待数据库服务就绪
    echo "等待数据库连接..."
    timeout 60 bash -c 'until kubectl exec -n cloud-scheduler deployment/cloud-scheduler-backend -- python -c "from app.core.database import engine; engine.connect()"; do sleep 2; done'
    
    # 运行数据库迁移
    kubectl exec -n cloud-scheduler deployment/cloud-scheduler-backend -- alembic upgrade head
    
    # 初始化基础数据
    kubectl exec -n cloud-scheduler deployment/cloud-scheduler-backend -- python -c "
from app.core.database import SessionLocal
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db = SessionLocal()

# 创建管理员用户
admin_user = User(
    username='admin',
    email='admin@example.com',
    hashed_password=pwd_context.hash('admin123'),
    full_name='系统管理员',
    is_superuser=True
)

db.add(admin_user)
db.commit()
db.close()
print('管理员用户创建成功')
"
    
    echo "✅ 数据库初始化完成"
}

# 启动监控服务
setup_monitoring() {
    echo "📊 设置监控服务..."
    
    # 部署Prometheus
    kubectl apply -f deployment/monitoring/ -n cloud-scheduler
    
    # 等待监控服务启动
    kubectl wait --for=condition=ready pod -l app=prometheus -n cloud-scheduler --timeout=120s
    
    echo "✅ 监控服务启动完成"
}

# 健康检查
health_check() {
    echo "🔍 执行健康检查..."
    
    # 获取服务端点
    BACKEND_URL=$(kubectl get svc cloud-scheduler-backend -n cloud-scheduler -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    FRONTEND_URL=$(kubectl get svc cloud-scheduler-frontend -n cloud-scheduler -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -z "$BACKEND_URL" ]; then
        BACKEND_URL=$(kubectl get svc cloud-scheduler-backend -n cloud-scheduler -o jsonpath='{.spec.clusterIP}')
    fi
    
    if [ -z "$FRONTEND_URL" ]; then
        FRONTEND_URL=$(kubectl get svc cloud-scheduler-frontend -n cloud-scheduler -o jsonpath='{.spec.clusterIP}')
    fi
    
    # 检查后端健康状态
    echo "检查后端服务..."
    curl -f http://$BACKEND_URL:8000/health || {
        echo "❌ 后端服务健康检查失败"
        exit 1
    }
    
    # 检查AI引擎
    AI_URL=$(kubectl get svc cloud-scheduler-ai -n cloud-scheduler -o jsonpath='{.spec.clusterIP}')
    echo "检查AI引擎..."
    curl -f http://$AI_URL:8001/health || {
        echo "❌ AI引擎健康检查失败"
        exit 1
    }
    
    echo "✅ 健康检查通过"
    echo ""
    echo "🎉 部署成功！"
    echo "前端访问地址: http://$FRONTEND_URL:3000"
    echo "后端API地址: http://$BACKEND_URL:8000"
    echo "AI引擎地址: http://$AI_URL:8001"
    echo ""
    echo "默认管理员账号: admin / admin123"
}

# 清理部署
cleanup() {
    echo "🧹 清理部署..."
    kubectl delete namespace cloud-scheduler --ignore-not-found=true
    docker rmi cloud-scheduler-backend:latest cloud-scheduler-ai:latest cloud-scheduler-frontend:latest --force
    echo "✅ 清理完成"
}

# 显示帮助信息
show_help() {
    echo "云智调度平台部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  deploy    完整部署（默认）"
    echo "  build     仅构建镜像"
    echo "  push      仅推送镜像"
    echo "  k8s       仅部署到K8s"
    echo "  cleanup   清理部署"
    echo "  help      显示此帮助信息"
    echo ""
    echo "环境变量:"
    echo "  DATABASE_URL      数据库连接字符串"
    echo "  REDIS_URL         Redis连接字符串"
    echo "  ECLOUD_ACCESS_KEY 移动云访问密钥"
    echo "  ECLOUD_SECRET_KEY 移动云秘密密钥"
    echo "  SECRET_KEY        应用秘密密钥"
    echo "  REGISTRY_URL      镜像仓库地址（可选）"
}

# 主函数
main() {
    case "${1:-deploy}" in
        "deploy")
            check_env
            build_images
            push_images
            deploy_k8s
            init_database
            setup_monitoring
            health_check
            ;;
        "build")
            build_images
            ;;
        "push")
            push_images
            ;;
        "k8s")
            deploy_k8s
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo "❌ 未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 捕获中断信号
trap 'echo "❌ 部署被中断"; exit 1' INT TERM

# 执行主函数
main "$@"
#!/bin/bash

# 云智调度平台快速启动脚本
# 用于本地开发和演示

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_message $BLUE "🚀 云智调度平台快速启动"
print_message $BLUE "================================"

# 检查Docker和Docker Compose
check_prerequisites() {
    print_message $YELLOW "📋 检查环境依赖..."
    
    if ! command -v docker &> /dev/null; then
        print_message $RED "❌ Docker 未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_message $RED "❌ Docker Compose 未安装，请先安装Docker Compose"
        exit 1
    fi
    
    print_message $GREEN "✅ 环境检查通过"
}

# 创建环境配置文件
setup_environment() {
    print_message $YELLOW "⚙️ 设置环境配置..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# 数据库配置
DATABASE_URL=mysql+pymysql://scheduler:schedulerpass@mysql:3306/cloud_scheduler
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_PASSWORD=schedulerpass

# Redis配置
REDIS_URL=redis://redis:6379

# 安全配置
SECRET_KEY=your-super-secret-key-change-in-production-$(date +%s)

# 移动云配置（请替换为实际的密钥）
ECLOUD_ACCESS_KEY=ed7bbd03fad34980834cae597a02cbfc
ECLOUD_SECRET_KEY=9ae0582e1e9e4f40ab5c68b744829c61
ECLOUD_REGION=cn-north-1

# AI引擎配置
AI_ENGINE_URL=http://ai-engine:8001
MODEL_UPDATE_INTERVAL=3600

# 应用配置
DEBUG=true
LOG_LEVEL=INFO
REACT_APP_API_URL=http://36.138.182.96:8000
EOF
        print_message $GREEN "✅ 环境配置文件已创建"
    else
        print_message $YELLOW "📝 使用已存在的环境配置文件"
    fi
}

# 启动服务
start_services() {
    print_message $YELLOW "🔧 启动服务..."
    
    # 停止可能存在的服务
    docker-compose down 2>/dev/null || true
    
    # 启动所有服务
    docker-compose up -d
    
    print_message $GREEN "✅ 服务启动成功"
}

# 等待服务就绪
wait_for_services() {
    print_message $YELLOW "⏳ 等待服务就绪..."
    
    # 等待MySQL就绪
    print_message $BLUE "等待MySQL数据库..."
    timeout 60 bash -c 'while ! docker-compose exec -T mysql mysqladmin ping -h localhost --silent; do sleep 2; done' || {
        print_message $RED "❌ MySQL启动超时"
        exit 1
    }
    
    # 等待Redis就绪
    print_message $BLUE "等待Redis缓存..."
    timeout 30 bash -c 'while ! docker-compose exec -T redis redis-cli ping | grep -q PONG; do sleep 2; done' || {
        print_message $RED "❌ Redis启动超时"
        exit 1
    }
    
    # 等待后端API就绪
    print_message $BLUE "等待后端API..."
    timeout 120 bash -c 'while ! curl -f http://localhost:8000/health &>/dev/null; do sleep 3; done' || {
        print_message $RED "❌ 后端API启动超时"
        exit 1
    }
    
    # 等待AI引擎就绪
    print_message $BLUE "等待AI引擎..."
    timeout 120 bash -c 'while ! curl -f http://localhost:8001/health &>/dev/null; do sleep 3; done' || {
        print_message $RED "❌ AI引擎启动超时"
        exit 1
    }
    
    # 等待前端就绪
    print_message $BLUE "等待前端服务..."
    timeout 120 bash -c 'while ! curl -f http://localhost:3000 &>/dev/null; do sleep 3; done' || {
        print_message $RED "❌ 前端服务启动超时"
        exit 1
    }
    
    print_message $GREEN "✅ 所有服务已就绪"
}

# 初始化数据
initialize_data() {
    print_message $YELLOW "📊 初始化演示数据..."
    
    # 运行数据库迁移
    docker-compose exec backend alembic upgrade head
    
    # 创建演示数据
    docker-compose exec backend python << 'EOF'
import asyncio
from app.core.database import SessionLocal
from app.models import User, Project, Resource
from app.services.ecloud_service import resource_manager
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def create_demo_data():
    db = SessionLocal()
    
    try:
        # 创建管理员用户
        admin_user = User(
            username='admin',
            email='admin@example.com',
            hashed_password=pwd_context.hash('admin123'),
            full_name='系统管理员',
            phone='13800138000',
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
        
        # 创建演示项目
        demo_project = Project(
            name='云智调度演示项目',
            description='移动云开发者大赛演示项目，展示AI驱动的算网资源统一编排能力',
            owner_id=admin_user.id,
            status='active',
            config={
                'auto_scaling': True,
                'cost_optimization': True,
                'ai_scheduling': True
            }
        )
        db.add(demo_project)
        db.commit()
        
        # 创建演示资源
        demo_resources = [
            Resource(
                project_id=demo_project.id,
                resource_type='compute',
                resource_id='ecs-demo-001',
                name='Web服务器-演示',
                provider='ecloud',
                region='cn-north-1',
                zone='cn-north-1a',
                cpu_cores=4,
                memory_gb=8,
                storage_gb=100,
                status='running',
                cost_per_hour=2.5,
                tags={'env': 'demo', 'type': 'web'}
            ),
            Resource(
                project_id=demo_project.id,
                resource_type='compute',
                resource_id='ecs-demo-002',
                name='DB服务器-演示',
                provider='ecloud',
                region='cn-north-1',
                zone='cn-north-1a',
                cpu_cores=8,
                memory_gb=32,
                storage_gb=500,
                status='running',
                cost_per_hour=8.0,
                tags={'env': 'demo', 'type': 'database'}
            ),
            Resource(
                project_id=demo_project.id,
                resource_type='memory',
                resource_id='redis-demo-001',
                name='Redis缓存-演示',
                provider='ecloud',
                region='cn-north-1',
                zone='cn-north-1a',
                cpu_cores=2,
                memory_gb=16,
                storage_gb=50,
                status='running',
                cost_per_hour=1.5,
                tags={'env': 'demo', 'type': 'cache'}
            )
        ]
        
        for resource in demo_resources:
            db.add(resource)
        
        db.commit()
        print('✅ 演示数据创建成功')
        
    except Exception as e:
        print(f'❌ 演示数据创建失败: {e}')
        db.rollback()
    finally:
        db.close()

# 运行数据初始化
asyncio.run(create_demo_data())
EOF
    
    print_message $GREEN "✅ 演示数据初始化完成"
}

# 显示访问信息
show_access_info() {
    print_message $GREEN "🎉 启动完成！"
    print_message $BLUE "================================"
    print_message $BLUE "访问地址:"
    print_message $BLUE "  前端管理界面: http://localhost:3000"
    print_message $BLUE "  后端API文档:  http://localhost:8000/docs"
    print_message $BLUE "  AI引擎接口:   http://localhost:8001/docs"
    print_message $BLUE "  公网访问地址: http://36.138.182.96:3000"
    print_message $BLUE ""
    print_message $BLUE "默认账号:"
    print_message $BLUE "  用户名: admin"
    print_message $BLUE "  密码:   admin123"
    print_message $BLUE ""
    print_message $BLUE "服务状态:"
    docker-compose ps
    print_message $BLUE ""
    print_message $YELLOW "💡 提示:"
    print_message $YELLOW "  - 使用 'docker-compose logs -f' 查看日志"
    print_message $YELLOW "  - 使用 'docker-compose down' 停止服务"
    print_message $YELLOW "  - 使用 './quick-start.sh stop' 停止所有服务"
}

# 停止服务
stop_services() {
    print_message $YELLOW "🛑 停止服务..."
    docker-compose down
    print_message $GREEN "✅ 服务已停止"
}

# 清理环境
cleanup() {
    print_message $YELLOW "🧹 清理环境..."
    docker-compose down -v
    docker system prune -f
    print_message $GREEN "✅ 环境清理完成"
}

# 显示日志
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f $service
    fi
}

# 显示帮助
show_help() {
    print_message $BLUE "云智调度平台快速启动脚本"
    print_message $BLUE ""
    print_message $BLUE "用法: $0 [命令]"
    print_message $BLUE ""
    print_message $BLUE "命令:"
    print_message $BLUE "  start    启动所有服务（默认）"
    print_message $BLUE "  stop     停止所有服务"
    print_message $BLUE "  restart  重启所有服务"
    print_message $BLUE "  status   查看服务状态"
    print_message $BLUE "  logs     查看服务日志"
    print_message $BLUE "  cleanup  清理环境和数据"
    print_message $BLUE "  help     显示此帮助"
}

# 主函数
main() {
    case "${1:-start}" in
        "start")
            check_prerequisites
            setup_environment
            start_services
            wait_for_services
            initialize_data
            show_access_info
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            start_services
            wait_for_services
            show_access_info
            ;;
        "status")
            docker-compose ps
            ;;
        "logs")
            show_logs $2
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_message $RED "❌ 未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 捕获中断信号
trap 'print_message $RED "❌ 操作被中断"; exit 1' INT TERM

# 执行主函数
main "$@"
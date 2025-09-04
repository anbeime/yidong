from fastapi import APIRouter
from .endpoints import auth, users, resources, schedules, monitoring

# 创建主路由器
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])
api_router.include_router(resources.router, prefix="/resources", tags=["资源管理"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["调度管理"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["监控数据"])
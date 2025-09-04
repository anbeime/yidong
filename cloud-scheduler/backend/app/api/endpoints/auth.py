from fastapi import APIRouter
from .users import router as user_router

# 认证相关的路由都在users.py中实现
# 这里创建一个简单的router指向用户相关的认证端点
router = APIRouter()

# 将用户认证相关的路由包含进来
router.include_router(user_router, tags=["认证"])
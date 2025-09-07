from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn
import os

from app.core.config import settings
from app.core.database import engine, Base
from app.api import api_router

# 导入CloudCoder应用
from cloudcoder_app import app as cloudcoder_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时的生命周期管理"""
    # 启动时初始化数据库
    Base.metadata.create_all(bind=engine)
    print("🚀 云智调度平台启动成功!")
    
    yield
    
    # 关闭时清理资源
    print("👋 云智调度平台正在关闭...")


# 创建FastAPI应用实例
app = FastAPI(
    title="云智调度 - AI算网资源编排平台",
    description="基于AI的智能算网资源统一编排平台，为移动云开发者大赛而设计",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加Gzip压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")

# 挂载CloudCoder应用
app.mount("/cloudcoder", cloudcoder_app)

# 挂载生成的应用静态文件目录
if not os.path.exists("generated_projects"):
    os.makedirs("generated_projects")
app.mount("/projects", StaticFiles(directory="generated_projects"), name="projects")


@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "云智调度 - AI算网资源编排平台",
        "version": "1.0.0",
        "status": "运行中",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "message": "服务运行正常"
    }


if __name__ == "__main__":
    # 本地开发时使用
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
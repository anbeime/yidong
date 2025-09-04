from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List, Optional
import os


class Settings(BaseSettings):
    """应用配置设置"""
    
    # 基础配置
    PROJECT_NAME: str = "云智调度平台"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 安全配置
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8天
    ALGORITHM: str = "HS256"
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://scheduler:schedulerpass@localhost:3306/cloud_scheduler"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        return values.get("DATABASE_URL")
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
    
    # AI引擎配置
    AI_ENGINE_URL: str = "http://localhost:8001"
    MODEL_UPDATE_INTERVAL: int = 3600  # 模型更新间隔(秒)
    
    # 移动云API配置
    ECLOUD_API_BASE: str = "https://ecs.cmecloud.cn"
    ECLOUD_ACCESS_KEY: Optional[str] = None
    ECLOUD_SECRET_KEY: Optional[str] = None
    ECLOUD_REGION: str = "cn-north-1"
    
    # 监控配置
    PROMETHEUS_ENABLED: bool = True
    METRICS_PATH: str = "/metrics"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # 任务调度配置
    SCHEDULER_INTERVAL: int = 60  # 调度间隔(秒)
    MAX_CONCURRENT_JOBS: int = 10
    
    # 资源预测配置
    PREDICTION_HORIZON: int = 24  # 预测时间范围(小时)
    HISTORICAL_DATA_DAYS: int = 30  # 历史数据天数
    
    # 告警配置
    ALERT_EMAIL_ENABLED: bool = False
    ALERT_EMAIL_SMTP_HOST: str = "smtp.qq.com"
    ALERT_EMAIL_SMTP_PORT: int = 587
    ALERT_EMAIL_USERNAME: Optional[str] = None
    ALERT_EMAIL_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局设置实例
settings = Settings()


# 数据库连接池配置
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 300,
    "echo": settings.DEBUG
}

# Redis连接配置
REDIS_CONFIG = {
    "encoding": "utf-8",
    "decode_responses": True,
    "socket_keepalive": True,
    "socket_keepalive_options": {},
    "health_check_interval": 30
}
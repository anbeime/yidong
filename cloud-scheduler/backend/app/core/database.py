from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis
from .config import settings, DATABASE_CONFIG, REDIS_CONFIG

# 创建数据库引擎
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    **DATABASE_CONFIG
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 创建元数据实例
metadata = MetaData()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis连接池
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    **REDIS_CONFIG
)

# Redis客户端
redis_client = redis.Redis(connection_pool=redis_pool)


def get_redis():
    """获取Redis客户端"""
    return redis_client


# 数据库表命名约定
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata.naming_convention = naming_convention
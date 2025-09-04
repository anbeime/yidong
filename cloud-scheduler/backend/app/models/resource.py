from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Resource(Base):
    """资源模型"""
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)  # ECS, RDS, Redis等
    status = Column(String(50), nullable=False, default="pending")  # pending, running, stopped, error
    project_id = Column(Integer, nullable=True, index=True)
    region = Column(String(100), nullable=False)
    instance_id = Column(String(255), unique=True, index=True)  # 云资源实例ID
    
    # 配置信息
    config = Column(Text)  # JSON格式的配置信息
    
    # 规格信息
    cpu_cores = Column(Float, default=0)
    memory_gb = Column(Float, default=0)
    disk_gb = Column(Float, default=0)
    
    # 成本信息
    hourly_cost = Column(Float, default=0.0)
    monthly_cost = Column(Float, default=0.0)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    metrics = relationship("ResourceMetric", back_populates="resource", cascade="all, delete-orphan")


class ResourceMetric(Base):
    """资源监控指标模型"""
    __tablename__ = "resource_metrics"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False, index=True)
    
    # 指标类型
    metric_type = Column(String(100), nullable=False, index=True)  # cpu, memory, disk, network
    
    # 指标值
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)  # %, bytes, count等
    
    # 时间戳
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # 关系
    resource = relationship("Resource", back_populates="metrics")


class Project(Base):
    """项目模型"""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="active")  # active, inactive, archived
    
    # 项目配置
    config = Column(Text)  # JSON格式的配置信息
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
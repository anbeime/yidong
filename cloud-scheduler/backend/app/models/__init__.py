from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class BaseModel(Base):
    """基础模型类"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)


class User(BaseModel):
    """用户表"""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # 关联关系
    projects = relationship("Project", back_populates="owner")
    alerts = relationship("Alert", back_populates="user")


class Project(BaseModel):
    """项目表"""
    __tablename__ = "projects"
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="active")  # active, paused, archived
    config = Column(JSON)  # 项目配置
    
    # 关联关系
    owner = relationship("User", back_populates="projects")
    resources = relationship("Resource", back_populates="project")
    schedules = relationship("Schedule", back_populates="project")


class Resource(BaseModel):
    """资源表"""
    __tablename__ = "resources"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    resource_type = Column(String(50), nullable=False)  # compute, storage, network
    resource_id = Column(String(100), nullable=False)  # 云资源ID
    name = Column(String(100), nullable=False)
    provider = Column(String(50), default="ecloud")  # 云服务提供商
    region = Column(String(50), nullable=False)
    zone = Column(String(50))
    
    # 资源规格
    cpu_cores = Column(Integer)
    memory_gb = Column(Float)
    storage_gb = Column(Float)
    bandwidth_mbps = Column(Float)
    
    # 资源状态
    status = Column(String(20), default="running")  # running, stopped, error
    cost_per_hour = Column(Float)  # 每小时成本
    tags = Column(JSON)  # 资源标签
    
    # 关联关系
    project = relationship("Project", back_populates="resources")
    metrics = relationship("ResourceMetric", back_populates="resource")
    schedules = relationship("Schedule", back_populates="resource")


class ResourceMetric(BaseModel):
    """资源监控指标表"""
    __tablename__ = "resource_metrics"
    
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # CPU指标
    cpu_usage_percent = Column(Float)
    cpu_load_1m = Column(Float)
    cpu_load_5m = Column(Float)
    cpu_load_15m = Column(Float)
    
    # 内存指标
    memory_usage_percent = Column(Float)
    memory_used_gb = Column(Float)
    memory_available_gb = Column(Float)
    
    # 存储指标
    disk_usage_percent = Column(Float)
    disk_read_iops = Column(Float)
    disk_write_iops = Column(Float)
    disk_read_bytes = Column(Float)
    disk_write_bytes = Column(Float)
    
    # 网络指标
    network_in_bytes = Column(Float)
    network_out_bytes = Column(Float)
    network_in_packets = Column(Float)
    network_out_packets = Column(Float)
    
    # 关联关系
    resource = relationship("Resource", back_populates="metrics")


class Schedule(BaseModel):
    """调度记录表"""
    __tablename__ = "schedules"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    
    # 调度信息
    schedule_type = Column(String(50), nullable=False)  # scale, migrate, optimize
    action = Column(String(50), nullable=False)  # start, stop, resize, move
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    
    # 调度前后状态
    before_config = Column(JSON)
    after_config = Column(JSON)
    
    # 执行信息
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    # AI决策信息
    ai_score = Column(Float)  # AI置信度得分
    prediction_data = Column(JSON)  # 预测数据
    
    # 关联关系
    project = relationship("Project", back_populates="schedules")
    resource = relationship("Resource", back_populates="schedules")


class Prediction(BaseModel):
    """预测结果表"""
    __tablename__ = "predictions"
    
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    prediction_time = Column(DateTime, nullable=False)  # 预测时间点
    prediction_horizon = Column(Integer, nullable=False)  # 预测时长(小时)
    
    # 预测结果
    predicted_cpu = Column(Float)
    predicted_memory = Column(Float)
    predicted_storage = Column(Float)
    predicted_network = Column(Float)
    
    # 预测置信度
    confidence_score = Column(Float)
    model_version = Column(String(50))
    
    # 实际值(用于模型评估)
    actual_cpu = Column(Float)
    actual_memory = Column(Float)
    actual_storage = Column(Float)
    actual_network = Column(Float)
    
    # 关联关系
    resource = relationship("Resource")


class Alert(BaseModel):
    """告警表"""
    __tablename__ = "alerts"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    
    # 告警信息
    alert_type = Column(String(50), nullable=False)  # threshold, anomaly, prediction
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # 告警状态
    status = Column(String(20), default="open")  # open, acknowledged, resolved
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # 告警规则
    rule_config = Column(JSON)
    trigger_value = Column(Float)
    threshold_value = Column(Float)
    
    # 关联关系
    user = relationship("User", back_populates="alerts")
    resource = relationship("Resource")


class CostOptimization(BaseModel):
    """成本优化建议表"""
    __tablename__ = "cost_optimizations"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"))
    
    # 优化建议
    optimization_type = Column(String(50), nullable=False)  # rightsizing, scheduling, termination
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # 成本影响
    current_cost_monthly = Column(Float)
    potential_savings_monthly = Column(Float)
    savings_percentage = Column(Float)
    
    # 建议状态
    status = Column(String(20), default="pending")  # pending, applied, ignored
    applied_at = Column(DateTime)
    
    # AI评分
    priority_score = Column(Float)
    confidence_score = Column(Float)
    
    # 关联关系
    project = relationship("Project")
    resource = relationship("Resource")


class GeneratedApp(BaseModel):
    """生成的应用记录表"""
    __tablename__ = "generated_apps"
    
    # 应用基本信息
    project_id = Column(String(50), unique=True, index=True, nullable=False)  # 生成的项目ID
    name = Column(String(200), nullable=False)  # 应用名称
    app_type = Column(String(50), nullable=False)  # 应用类型
    requirement = Column(Text, nullable=False)  # 用户需求描述
    
    # 技术信息
    tech_stack = Column(JSON)  # 技术栈
    files_count = Column(Integer)  # 文件数量
    generated_files = Column(JSON)  # 生成的文件列表
    
    # 配置信息
    features = Column(JSON)  # 功能特性
    complexity = Column(String(20))  # 复杂度
    cloud_resources = Column(JSON)  # 云资源配置
    deployment_config = Column(JSON)  # 部署配置
    
    # 访问信息
    deployment_url = Column(String(500))  # 部署URL
    status = Column(String(20), default="completed")  # 状态: completed, error
    
    # 成本估算
    cost_estimate = Column(String(50))  # 成本估算
    
    # 添加索引以提高查询性能
    __table_args__ = (
        Index('idx_generated_apps_app_type', 'app_type'),
        Index('idx_generated_apps_created_at', 'created_at'),
    )
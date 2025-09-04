from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ResourceBase(BaseModel):
    """资源基础Schema"""
    name: str = Field(..., description="资源名称")
    resource_type: str = Field(..., description="资源类型")
    region: str = Field(..., description="区域")
    project_id: Optional[int] = Field(None, description="项目ID")


class ResourceCreate(ResourceBase):
    """创建资源Schema"""
    config: Optional[Dict[str, Any]] = Field(None, description="配置信息")
    cpu_cores: Optional[float] = Field(0, description="CPU核心数")
    memory_gb: Optional[float] = Field(0, description="内存GB")
    storage_gb: Optional[float] = Field(0, description="存储GB")


class ResourceUpdate(BaseModel):
    """更新资源Schema"""
    name: Optional[str] = Field(None, description="资源名称")
    status: Optional[str] = Field(None, description="资源状态")
    config: Optional[Dict[str, Any]] = Field(None, description="配置信息")
    cpu_cores: Optional[float] = Field(None, description="CPU核心数")
    memory_gb: Optional[float] = Field(None, description="内存GB")
    storage_gb: Optional[float] = Field(None, description="存储GB")


class ResourceResponse(ResourceBase):
    """资源响应Schema"""
    id: int
    status: str
    instance_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    cpu_cores: Optional[float] = 0
    memory_gb: Optional[float] = 0
    disk_gb: Optional[float] = 0
    hourly_cost: Optional[float] = 0.0
    monthly_cost: Optional[float] = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResourceMetricBase(BaseModel):
    """资源指标基础Schema"""
    metric_type: str = Field(..., description="指标类型")
    value: float = Field(..., description="指标值")
    unit: str = Field(..., description="单位")


class ResourceMetricCreate(ResourceMetricBase):
    """创建资源指标Schema"""
    resource_id: int = Field(..., description="资源ID")


class ResourceMetricResponse(ResourceMetricBase):
    """资源指标响应Schema"""
    id: int
    resource_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class ResourceStatsResponse(BaseModel):
    """资源统计响应Schema"""
    resource_id: int
    period: str
    avg_cpu_usage: Optional[float] = None
    avg_memory_usage: Optional[float] = None
    avg_disk_usage: Optional[float] = None
    avg_network_usage: Optional[float] = None
    max_cpu_usage: Optional[float] = None
    max_memory_usage: Optional[float] = None
    max_disk_usage: Optional[float] = None
    max_network_usage: Optional[float] = None
    total_cost: Optional[float] = None
    
    class Config:
        from_attributes = True
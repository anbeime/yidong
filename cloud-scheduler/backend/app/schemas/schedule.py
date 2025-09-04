from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class ScheduleBase(BaseModel):
    """调度基础模型"""
    project_id: int
    resource_id: int
    schedule_type: str  # scale, migrate, optimize
    action: str  # start, stop, resize, move
    before_config: Optional[Dict[str, Any]] = None
    after_config: Optional[Dict[str, Any]] = None
    ai_score: Optional[float] = None
    prediction_data: Optional[Dict[str, Any]] = None


class ScheduleCreate(ScheduleBase):
    """创建调度请求模型"""
    pass


class ScheduleUpdate(BaseModel):
    """更新调度请求模型"""
    status: Optional[str] = None
    error_message: Optional[str] = None
    after_config: Optional[Dict[str, Any]] = None
    ai_score: Optional[float] = None
    prediction_data: Optional[Dict[str, Any]] = None


class ScheduleResponse(ScheduleBase):
    """调度响应模型"""
    id: int
    status: str  # pending, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScheduleDecisionRequest(BaseModel):
    """AI调度决策请求模型"""
    resource_id: int
    current_metrics: Dict[str, float]


class ScheduleDecisionResponse(BaseModel):
    """AI调度决策响应模型"""
    resource_id: int
    action: str
    confidence: float
    predicted_metrics: Dict[str, float]
    reasoning: str
    estimated_savings: float
    execution_plan: Dict[str, Any]


class ScheduleStatistics(BaseModel):
    """调度统计模型"""
    total_schedules: int
    completed_schedules: int
    failed_schedules: int
    success_rate: float
    type_statistics: Dict[str, Dict[str, int]]
    period_days: int
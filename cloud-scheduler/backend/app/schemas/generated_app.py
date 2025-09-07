from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class GeneratedAppBase(BaseModel):
    """生成应用基础模型"""
    project_id: str
    name: str
    app_type: str
    requirement: str
    tech_stack: List[str]
    files_count: int
    generated_files: List[str]
    features: List[str]
    complexity: str
    cloud_resources: List[str]
    deployment_config: Dict[str, Any]
    deployment_url: Optional[str] = None
    status: Optional[str] = "completed"
    cost_estimate: Optional[str] = None

class GeneratedAppCreate(GeneratedAppBase):
    """创建生成应用模型"""
    pass

class GeneratedAppUpdate(GeneratedAppBase):
    """更新生成应用模型"""
    project_id: Optional[str] = None
    name: Optional[str] = None
    app_type: Optional[str] = None
    requirement: Optional[str] = None

class GeneratedAppInDB(GeneratedAppBase):
    """数据库中的生成应用模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class GeneratedAppResponse(GeneratedAppInDB):
    """生成应用响应模型"""
    pass
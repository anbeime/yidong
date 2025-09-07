from sqlalchemy.orm import Session
from app.models import GeneratedApp
from app.schemas.generated_app import GeneratedAppCreate, GeneratedAppUpdate
from typing import List, Optional
from datetime import datetime

def create_generated_app(db: Session, app_data: GeneratedAppCreate) -> GeneratedApp:
    """创建生成的应用记录"""
    db_app = GeneratedApp(
        project_id=app_data.project_id,
        name=app_data.name,
        app_type=app_data.app_type,
        requirement=app_data.requirement,
        tech_stack=app_data.tech_stack,
        files_count=app_data.files_count,
        generated_files=app_data.generated_files,
        features=app_data.features,
        complexity=app_data.complexity,
        cloud_resources=app_data.cloud_resources,
        deployment_config=app_data.deployment_config,
        deployment_url=app_data.deployment_url,
        status=app_data.status,
        cost_estimate=app_data.cost_estimate,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app

def get_generated_app(db: Session, project_id: str) -> Optional[GeneratedApp]:
    """根据项目ID获取生成的应用记录"""
    return db.query(GeneratedApp).filter(GeneratedApp.project_id == project_id).first()

def get_generated_apps(db: Session, skip: int = 0, limit: int = 100) -> List[GeneratedApp]:
    """获取生成的应用记录列表"""
    return db.query(GeneratedApp).offset(skip).limit(limit).all()

def get_generated_apps_by_type(db: Session, app_type: str, skip: int = 0, limit: int = 100) -> List[GeneratedApp]:
    """根据应用类型获取生成的应用记录列表"""
    return db.query(GeneratedApp).filter(GeneratedApp.app_type == app_type).offset(skip).limit(limit).all()

def get_recent_generated_apps(db: Session, limit: int = 10) -> List[GeneratedApp]:
    """获取最近生成的应用记录列表"""
    return db.query(GeneratedApp).order_by(GeneratedApp.created_at.desc()).limit(limit).all()

def update_generated_app(db: Session, project_id: str, app_data: GeneratedAppUpdate) -> Optional[GeneratedApp]:
    """更新生成的应用记录"""
    db_app = get_generated_app(db, project_id)
    if db_app:
        update_data = app_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_app, key, value)
        db_app.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_app)
    return db_app

def delete_generated_app(db: Session, project_id: str) -> bool:
    """删除生成的应用记录"""
    db_app = get_generated_app(db, project_id)
    if db_app:
        db.delete(db_app)
        db.commit()
        return True
    return False
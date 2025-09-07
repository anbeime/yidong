from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.schemas.generated_app import GeneratedAppCreate, GeneratedAppUpdate, GeneratedAppResponse
from app.services.generated_app_service import (
    create_generated_app,
    get_generated_app,
    get_generated_apps,
    get_generated_apps_by_type,
    update_generated_app,
    delete_generated_app
)

router = APIRouter()

@router.post("/", response_model=GeneratedAppResponse, tags=["生成应用"])
def create_app(app_data: GeneratedAppCreate, db: Session = Depends(get_db)):
    """创建生成的应用记录"""
    db_app = get_generated_app(db, app_data.project_id)
    if db_app:
        raise HTTPException(status_code=400, detail="应用记录已存在")
    return create_generated_app(db, app_data)

@router.get("/{project_id}", response_model=GeneratedAppResponse, tags=["生成应用"])
def read_app(project_id: str, db: Session = Depends(get_db)):
    """获取生成的应用记录"""
    db_app = get_generated_app(db, project_id)
    if db_app is None:
        raise HTTPException(status_code=404, detail="应用记录未找到")
    return db_app

@router.get("/", response_model=List[GeneratedAppResponse], tags=["生成应用"])
def read_apps(
    skip: int = 0,
    limit: int = 100,
    app_type: str = None,
    db: Session = Depends(get_db)
):
    """获取生成的应用记录列表"""
    if app_type:
        apps = get_generated_apps_by_type(db, app_type, skip=skip, limit=limit)
    else:
        apps = get_generated_apps(db, skip=skip, limit=limit)
    return apps

@router.get("/recent", response_model=List[GeneratedAppResponse], tags=["生成应用"])
def read_recent_apps(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """获取最近生成的应用记录列表"""
    # 按创建时间倒序排列，获取最新的记录
    from app.models import GeneratedApp
    apps = db.query(GeneratedApp).order_by(GeneratedApp.created_at.desc()).limit(limit).all()
    return apps

@router.put("/{project_id}", response_model=GeneratedAppResponse, tags=["生成应用"])
def update_app(project_id: str, app_data: GeneratedAppUpdate, db: Session = Depends(get_db)):
    """更新生成的应用记录"""
    db_app = update_generated_app(db, project_id, app_data)
    if db_app is None:
        raise HTTPException(status_code=404, detail="应用记录未找到")
    return db_app

@router.delete("/{project_id}", response_model=bool, tags=["生成应用"])
def delete_app(project_id: str, db: Session = Depends(get_db)):
    """删除生成的应用记录"""
    success = delete_generated_app(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="应用记录未找到")
    return success
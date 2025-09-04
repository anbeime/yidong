from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models import Resource, ResourceMetric
from app.schemas.resource import (
    ResourceCreate, ResourceUpdate, ResourceResponse,
    ResourceMetricResponse, ResourceStatsResponse
)
from app.services.resource_service import ResourceService
from app.services.monitoring_service import MonitoringService

router = APIRouter()
resource_service = ResourceService()
monitoring_service = MonitoringService()


@router.get("/", response_model=List[ResourceResponse])
async def get_resources(
    project_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """获取资源列表"""
    try:
        resources = await resource_service.get_resources(
            db=db,
            project_id=project_id,
            resource_type=resource_type,
            status=status,
            skip=skip,
            limit=limit
        )
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{resource_id}", response_model=ResourceResponse)
async def get_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """获取单个资源详情"""
    resource = await resource_service.get_resource(db=db, resource_id=resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")
    return resource


@router.post("/", response_model=ResourceResponse)
async def create_resource(
    resource_data: ResourceCreate,
    db: Session = Depends(get_db)
):
    """创建新资源"""
    try:
        resource = await resource_service.create_resource(db=db, resource_data=resource_data)
        return resource
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: int,
    resource_data: ResourceUpdate,
    db: Session = Depends(get_db)
):
    """更新资源信息"""
    try:
        resource = await resource_service.update_resource(
            db=db, 
            resource_id=resource_id, 
            resource_data=resource_data
        )
        if not resource:
            raise HTTPException(status_code=404, detail="资源不存在")
        return resource
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """删除资源"""
    try:
        success = await resource_service.delete_resource(db=db, resource_id=resource_id)
        if not success:
            raise HTTPException(status_code=404, detail="资源不存在")
        return {"message": "资源删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{resource_id}/metrics", response_model=List[ResourceMetricResponse])
async def get_resource_metrics(
    resource_id: int,
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    metric_type: Optional[str] = Query(None, description="指标类型"),
    db: Session = Depends(get_db)
):
    """获取资源监控指标"""
    try:
        # 默认获取最近24小时的数据
        if not start_time:
            start_time = datetime.now() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.now()
            
        metrics = await monitoring_service.get_resource_metrics(
            db=db,
            resource_id=resource_id,
            start_time=start_time,
            end_time=end_time,
            metric_type=metric_type
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{resource_id}/stats", response_model=ResourceStatsResponse)
async def get_resource_stats(
    resource_id: int,
    period: str = Query("24h", description="统计周期: 1h, 24h, 7d, 30d"),
    db: Session = Depends(get_db)
):
    """获取资源统计信息"""
    try:
        stats = await monitoring_service.get_resource_stats(
            db=db,
            resource_id=resource_id,
            period=period
        )
        return stats
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{resource_id}/scale")
async def scale_resource(
    resource_id: int,
    scale_config: dict,
    db: Session = Depends(get_db)
):
    """扩缩容资源"""
    try:
        result = await resource_service.scale_resource(
            db=db,
            resource_id=resource_id,
            scale_config=scale_config
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{resource_id}/start")
async def start_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """启动资源"""
    try:
        result = await resource_service.start_resource(db=db, resource_id=resource_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{resource_id}/stop")
async def stop_resource(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """停止资源"""
    try:
        result = await resource_service.stop_resource(db=db, resource_id=resource_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{resource_id}/cost")
async def get_resource_cost(
    resource_id: int,
    period: str = Query("30d", description="统计周期"),
    db: Session = Depends(get_db)
):
    """获取资源成本分析"""
    try:
        cost_data = await resource_service.get_resource_cost(
            db=db,
            resource_id=resource_id
        )
        return cost_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
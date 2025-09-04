from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import httpx

from app.core.database import get_db
from app.models import Schedule, Resource, Project
from app.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse,
    ScheduleDecisionRequest, ScheduleDecisionResponse
)
from app.services.schedule_service import ScheduleService
from app.services.ecloud_service import resource_manager
from app.core.config import settings

router = APIRouter()
schedule_service = ScheduleService()


@router.get("/", response_model=List[ScheduleResponse])
async def get_schedules(
    project_id: Optional[int] = None,
    resource_id: Optional[int] = None,
    status: Optional[str] = None,
    schedule_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取调度记录列表"""
    try:
        schedules = await schedule_service.get_schedules(
            db=db,
            project_id=project_id,
            resource_id=resource_id,
            status=status,
            schedule_type=schedule_type,
            skip=skip,
            limit=limit
        )
        return schedules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """获取单个调度记录详情"""
    schedule = await schedule_service.get_schedule(db=db, schedule_id=schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="调度记录不存在")
    return schedule


@router.post("/", response_model=ScheduleResponse)
async def create_schedule(
    schedule_data: ScheduleCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """创建新的调度任务"""
    try:
        schedule = await schedule_service.create_schedule(db=db, schedule_data=schedule_data)
        
        # 在后台执行调度任务
        schedule_id = getattr(schedule, 'id')
        background_tasks.add_task(execute_schedule_task, schedule_id, db)
        
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    db: Session = Depends(get_db)
):
    """更新调度记录"""
    try:
        schedule = await schedule_service.update_schedule(
            db=db, 
            schedule_id=schedule_id, 
            schedule_data=schedule_data
        )
        if not schedule:
            raise HTTPException(status_code=404, detail="调度记录不存在")
        return schedule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai-decision", response_model=ScheduleDecisionResponse)
async def get_ai_schedule_decision(
    request: ScheduleDecisionRequest,
    db: Session = Depends(get_db)
):
    """获取AI调度决策建议"""
    try:
        # 获取资源信息
        resource = db.query(Resource).filter(Resource.id == request.resource_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="资源不存在")
        
        # 调用AI引擎获取预测和决策
        async with httpx.AsyncClient() as client:
            # 获取资源历史数据
            historical_data = await schedule_service.get_resource_historical_data(
                db=db, 
                resource_id=request.resource_id,
                days=7
            )
            
            # 调用AI预测接口
            prediction_response = await client.post(
                f"{settings.AI_ENGINE_URL}/predict",
                json={
                    "resource_id": request.resource_id,
                    "historical_data": historical_data,
                    "prediction_horizon": 24
                },
                timeout=30
            )
            prediction_response.raise_for_status()
            prediction_data = prediction_response.json()
            
            # 调用AI决策接口
            decision_response = await client.post(
                f"{settings.AI_ENGINE_URL}/schedule",
                json={
                    "resource_id": request.resource_id,
                    "current_metrics": request.current_metrics,
                    "predicted_metrics": prediction_data["predictions"]
                },
                timeout=30
            )
            decision_response.raise_for_status()
            decision_data = decision_response.json()
            
            return ScheduleDecisionResponse(
                resource_id=request.resource_id,
                action=decision_data["action"],
                confidence=decision_data["confidence"],
                predicted_metrics=decision_data["predicted_metrics"],
                reasoning=decision_data["reasoning"],
                estimated_savings=await calculate_estimated_savings(
                    resource, decision_data["action"]
                ),
                execution_plan=await generate_execution_plan(
                    resource, decision_data["action"]
                )
            )
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=503, 
            detail=f"AI引擎服务异常: {e.response.status_code}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{schedule_id}/execute")
async def execute_schedule(
    schedule_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """执行调度任务"""
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="调度记录不存在")
        
        if str(schedule.status) != "pending":
            raise HTTPException(status_code=400, detail="调度任务状态不允许执行")
        
        # 更新状态为执行中
        setattr(schedule, 'status', "running")
        setattr(schedule, 'started_at', datetime.now())
        db.commit()
        
        # 在后台执行调度任务
        background_tasks.add_task(execute_schedule_task, schedule_id, db)
        
        return {"message": "调度任务已开始执行", "schedule_id": schedule_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{schedule_id}/cancel")
async def cancel_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """取消调度任务"""
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            raise HTTPException(status_code=404, detail="调度记录不存在")
        
        if str(schedule.status) not in ["pending", "running"]:
            raise HTTPException(status_code=400, detail="调度任务状态不允许取消")
        
        setattr(schedule, 'status', "cancelled")
        setattr(schedule, 'completed_at', datetime.now())
        db.commit()
        
        return {"message": "调度任务已取消"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/summary")
async def get_schedule_statistics(
    project_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """获取调度统计信息"""
    try:
        stats = await schedule_service.get_schedule_statistics(
            db=db,
            project_id=project_id,
            days=days
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def execute_schedule_task(schedule_id: int, db: Session):
    """后台执行调度任务"""
    schedule = None
    try:
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            return
        
        resource = db.query(Resource).filter(Resource.id == schedule.resource_id).first()
        if not resource:
            setattr(schedule, 'status', "failed")
            setattr(schedule, 'error_message', "关联资源不存在")
            setattr(schedule, 'completed_at', datetime.now())
            db.commit()
            return
        
        # 根据调度类型执行不同操作
        if str(schedule.schedule_type) == "scale":
            result = await execute_scaling_task(schedule, resource)
        elif str(schedule.schedule_type) == "migrate":
            result = await execute_migration_task(schedule, resource)
        elif str(schedule.schedule_type) == "optimize":
            result = await execute_optimization_task(schedule, resource)
        else:
            result = {"success": False, "message": f"不支持的调度类型: {str(schedule.schedule_type)}"}
        
        # 更新调度状态
        if result["success"]:
            setattr(schedule, 'status', "completed")
            setattr(schedule, 'after_config', result.get("after_config", {}))
        else:
            setattr(schedule, 'status', "failed")
            setattr(schedule, 'error_message', result.get("message", "执行失败"))
        
        setattr(schedule, 'completed_at', datetime.now())
        db.commit()
        
    except Exception as e:
        if schedule is not None:
            setattr(schedule, 'status', "failed")
            setattr(schedule, 'error_message', str(e))
            setattr(schedule, 'completed_at', datetime.now())
            db.commit()


async def execute_scaling_task(schedule: Schedule, resource: Resource) -> dict:
    """执行扩缩容任务"""
    try:
        after_config = schedule.after_config or {}
        
        if str(resource.resource_type) == "compute":
            # 云主机扩缩容
            instance_type = after_config.get("instance_type")
            if instance_type:
                result = await resource_manager.ecloud_client.resize_instance(
                    str(resource.resource_id), instance_type
                )
                return {"success": True, "result": result, "after_config": after_config}
        
        elif str(resource.resource_type) == "container":
            # 容器服务扩缩容
            scale_config = {
                "type": "container",
                "cluster_id": after_config.get("cluster_id"),
                "service_name": after_config.get("service_name"),
                "desired_count": after_config.get("desired_count")
            }
            result = await resource_manager.scale_resource(str(resource.resource_id), scale_config)
            return result
        
        return {"success": False, "message": "不支持的资源类型"}
        
    except Exception as e:
        return {"success": False, "message": str(e)}


async def execute_migration_task(schedule: Schedule, resource: Resource) -> dict:
    """执行迁移任务"""
    try:
        # 这里实现资源迁移逻辑
        # 由于是演示版本，返回模拟结果
        return {
            "success": True,
            "message": "迁移任务模拟执行成功",
            "after_config": schedule.after_config
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


async def execute_optimization_task(schedule: Schedule, resource: Resource) -> dict:
    """执行优化任务"""
    try:
        # 这里实现资源优化逻辑
        # 由于是演示版本，返回模拟结果
        return {
            "success": True,
            "message": "优化任务模拟执行成功",
            "after_config": schedule.after_config
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


async def calculate_estimated_savings(resource: Resource, action: str) -> float:
    """计算预估节省成本"""
    try:
        cost_per_hour = getattr(resource, 'cost_per_hour', None)
        current_cost = float(cost_per_hour or 0) * 24 * 30  # 月成本
        
        if action == "scale_down":
            return current_cost * 0.3  # 缩容节省30%
        elif action == "optimize":
            return current_cost * 0.15  # 优化节省15%
        elif action == "schedule":
            return current_cost * 0.1  # 调度节省10%
        
        return 0.0
    except:
        return 0.0


async def generate_execution_plan(resource: Resource, action: str) -> dict:
    """生成执行计划"""
    try:
        base_plan = {
            "steps": [],
            "estimated_duration": "5-10分钟",
            "rollback_plan": "支持一键回滚",
            "risk_level": "低"
        }
        
        if action == "scale_up":
            base_plan["steps"] = [
                "1. 验证资源状态",
                "2. 准备新配置",
                "3. 执行扩容操作",
                "4. 验证扩容结果",
                "5. 更新监控配置"
            ]
        elif action == "scale_down":
            base_plan["steps"] = [
                "1. 检查资源使用情况",
                "2. 确认缩容安全性",
                "3. 执行缩容操作",
                "4. 验证缩容结果",
                "5. 调整监控阈值"
            ]
        else:
            base_plan["steps"] = [
                "1. 分析当前配置",
                "2. 生成优化方案",
                "3. 执行配置变更",
                "4. 验证变更效果"
            ]
        
        return base_plan
    except:
        return {"steps": [], "estimated_duration": "未知", "risk_level": "中"}

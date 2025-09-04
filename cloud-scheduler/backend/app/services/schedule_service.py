from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
import random

from ..models import Schedule, Resource, ResourceMetric
from ..schemas.schedule import ScheduleCreate, ScheduleUpdate


class ScheduleService:
    """调度服务类"""
    
    async def get_schedules(
        self, 
        db: Session, 
        project_id: Optional[int] = None,
        resource_id: Optional[int] = None,
        status: Optional[str] = None,
        schedule_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Schedule]:
        """获取调度记录列表"""
        query = db.query(Schedule)
        
        if project_id:
            query = query.filter(Schedule.project_id == project_id)
        if resource_id:
            query = query.filter(Schedule.resource_id == resource_id)
        if status:
            query = query.filter(Schedule.status == status)
        if schedule_type:
            query = query.filter(Schedule.schedule_type == schedule_type)
        
        return query.order_by(desc(Schedule.created_at)).offset(skip).limit(limit).all()
    
    async def get_schedule(self, db: Session, schedule_id: int) -> Optional[Schedule]:
        """获取单个调度记录"""
        return db.query(Schedule).filter(Schedule.id == schedule_id).first()
    
    async def create_schedule(self, db: Session, schedule_data: ScheduleCreate) -> Schedule:
        """创建调度记录"""
        # 验证资源存在
        resource = db.query(Resource).filter(Resource.id == schedule_data.resource_id).first()
        if not resource:
            raise ValueError("指定的资源不存在")
        
        schedule_dict = schedule_data.dict()
        schedule = Schedule(**schedule_dict)
        
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule
    
    async def update_schedule(
        self, 
        db: Session, 
        schedule_id: int, 
        schedule_data: ScheduleUpdate
    ) -> Optional[Schedule]:
        """更新调度记录"""
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            return None
        
        update_data = schedule_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)
        
        db.commit()
        db.refresh(schedule)
        return schedule
    
    async def get_resource_historical_data(
        self, 
        db: Session, 
        resource_id: int, 
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """获取资源历史数据用于AI预测"""
        # 从资源监控表获取真实数据
        start_date = datetime.now() - timedelta(days=days)
        
        metrics = db.query(ResourceMetric).filter(
            and_(
                ResourceMetric.resource_id == resource_id,
                ResourceMetric.timestamp >= start_date
            )
        ).order_by(ResourceMetric.timestamp).all()
        
        if metrics:
            # 返回真实监控数据
            return [
                {
                    "timestamp": metric.timestamp.isoformat(),
                    "cpu_usage_percent": metric.cpu_usage_percent or 0,
                    "memory_usage_percent": metric.memory_usage_percent or 0,
                    "disk_usage_percent": metric.disk_usage_percent or 0,
                    "network_in_bytes": metric.network_in_bytes or 0,
                    "network_out_bytes": metric.network_out_bytes or 0
                }
                for metric in metrics
            ]
        else:
            # 如果没有真实数据，返回模拟数据
            return await self._generate_mock_historical_data(days)
    
    async def _generate_mock_historical_data(self, days: int) -> List[Dict[str, Any]]:
        """生成模拟历史数据"""
        data = []
        base_time = datetime.now() - timedelta(days=days)
        
        for i in range(days * 24):  # 每小时一个数据点
            timestamp = base_time + timedelta(hours=i)
            data.append({
                "timestamp": timestamp.isoformat(),
                "cpu_usage_percent": 20 + random.random() * 60,
                "memory_usage_percent": 30 + random.random() * 50,
                "disk_usage_percent": 10 + random.random() * 30,
                "network_in_bytes": 1000 + random.random() * 5000,
                "network_out_bytes": 800 + random.random() * 4000
            })
        
        return data
    
    async def get_schedule_statistics(
        self, 
        db: Session, 
        project_id: Optional[int] = None, 
        days: int = 30
    ) -> Dict[str, Any]:
        """获取调度统计信息"""
        # 计算时间范围
        start_date = datetime.now() - timedelta(days=days)
        
        query = db.query(Schedule).filter(Schedule.created_at >= start_date)
        if project_id:
            query = query.filter(Schedule.project_id == project_id)
        
        schedules = query.all()
        
        total_count = len(schedules)
        completed_count = len([s for s in schedules if str(s.status) == "completed"])
        failed_count = len([s for s in schedules if str(s.status) == "failed"])
        
        success_rate = (completed_count / total_count * 100) if total_count > 0 else 0
        
        # 按类型统计
        type_stats = {}
        for schedule in schedules:
            schedule_type = str(schedule.schedule_type)
            if schedule_type not in type_stats:
                type_stats[schedule_type] = {"total": 0, "completed": 0}
            type_stats[schedule_type]["total"] += 1
            if str(schedule.status) == "completed":
                type_stats[schedule_type]["completed"] += 1
        
        return {
            "total_schedules": total_count,
            "completed_schedules": completed_count,
            "failed_schedules": failed_count,
            "success_rate": round(success_rate, 2),
            "type_statistics": type_stats,
            "period_days": days
        }
    
    async def get_active_schedules(self, db: Session, resource_id: int) -> List[Schedule]:
        """获取资源的活跃调度任务"""
        return db.query(Schedule).filter(
            and_(
                Schedule.resource_id == resource_id,
                or_(
                    Schedule.status == "pending",
                    Schedule.status == "running"
                )
            )
        ).all()
    
    async def cancel_schedule(self, db: Session, schedule_id: int) -> bool:
        """取消调度任务"""
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            return False
        
        if schedule.status not in ["pending", "running"]:
            return False
        
        setattr(schedule, 'status', "cancelled")
        setattr(schedule, 'completed_at', datetime.now())
        db.commit()
        
        return True
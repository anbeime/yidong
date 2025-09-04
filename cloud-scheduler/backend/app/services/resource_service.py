from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import Resource, ResourceMetric
from app.schemas.resource import ResourceCreate, ResourceUpdate
from datetime import datetime
import json


class ResourceService:
    """资源服务类"""

    async def get_resources(
        self,
        db: Session,
        project_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Resource]:
        """获取资源列表"""
        query = db.query(Resource)
        
        # 添加过滤条件
        if project_id:
            query = query.filter(Resource.project_id == project_id)
        if resource_type:
            query = query.filter(Resource.resource_type == resource_type)
        if status:
            query = query.filter(Resource.status == status)
        
        # 分页
        resources = query.offset(skip).limit(limit).all()
        return resources

    async def get_resource(self, db: Session, resource_id: int) -> Optional[Resource]:
        """获取单个资源"""
        return db.query(Resource).filter(Resource.id == resource_id).first()

    async def create_resource(self, db: Session, resource_data: ResourceCreate) -> Resource:
        """创建资源"""
        # 创建资源对象
        db_resource = Resource(
            name=resource_data.name,
            resource_type=resource_data.resource_type,
            region=resource_data.region,
            project_id=resource_data.project_id,
            config=json.dumps(resource_data.config) if resource_data.config else None,
            cpu_cores=resource_data.cpu_cores,
            memory_gb=resource_data.memory_gb,
            disk_gb=resource_data.storage_gb,
            status="pending"
        )
        
        db.add(db_resource)
        db.commit()
        db.refresh(db_resource)
        return db_resource

    async def update_resource(
        self, 
        db: Session, 
        resource_id: int, 
        resource_data: ResourceUpdate
    ) -> Optional[Resource]:
        """更新资源"""
        db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not db_resource:
            return None

        # 更新字段
        update_data = resource_data.dict(exclude_unset=True)
        
        # 处理config字段
        if 'config' in update_data and update_data['config'] is not None:
            update_data['config'] = json.dumps(update_data['config'])
        
        for field, value in update_data.items():
            setattr(db_resource, field, value)

        db.commit()
        db.refresh(db_resource)
        return db_resource

    async def delete_resource(self, db: Session, resource_id: int) -> bool:
        """删除资源"""
        db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not db_resource:
            return False

        db.delete(db_resource)
        db.commit()
        return True

    async def scale_resource(
        self, 
        db: Session, 
        resource_id: int, 
        scale_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """扩缩容资源"""
        db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not db_resource:
            raise ValueError("资源不存在")

        # 模拟扩缩容操作
        current_config = json.loads(db_resource.config) if db_resource.config else {}
        
        # 更新配置
        if 'cpu_cores' in scale_config:
            db_resource.cpu_cores = scale_config['cpu_cores']
        if 'memory_gb' in scale_config:
            db_resource.memory_gb = scale_config['memory_gb']
        if 'disk_gb' in scale_config:
            db_resource.disk_gb = scale_config['disk_gb']

        # 更新状态
        setattr(db_resource, 'status', "scaling")
        current_config.update(scale_config)
        db_resource.config = json.dumps(current_config)

        db.commit()
        db.refresh(db_resource)

        return {
            "resource_id": resource_id,
            "action": "scale",
            "status": "success",
            "new_config": current_config,
            "message": "资源扩缩容操作已启动"
        }

    async def start_resource(self, db: Session, resource_id: int) -> Dict[str, Any]:
        """启动资源"""
        db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not db_resource:
            raise ValueError("资源不存在")

        if str(db_resource.status) == "running":
            return {
                "resource_id": resource_id,
                "action": "start",
                "status": "already_running",
                "message": "资源已在运行中"
            }

        # 更新状态
        setattr(db_resource, 'status', "running")
        db.commit()
        db.refresh(db_resource)

        return {
            "resource_id": resource_id,
            "action": "start",
            "status": "success",
            "message": "资源启动成功"
        }

    async def stop_resource(self, db: Session, resource_id: int) -> Dict[str, Any]:
        """停止资源"""
        db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not db_resource:
            raise ValueError("资源不存在")

        if str(db_resource.status) == "stopped":
            return {
                "resource_id": resource_id,
                "action": "stop",
                "status": "already_stopped",
                "message": "资源已停止"
            }

        # 更新状态
        setattr(db_resource, 'status', "stopped")
        db.commit()
        db.refresh(db_resource)

        return {
            "resource_id": resource_id,
            "action": "stop",
            "status": "success",
            "message": "资源停止成功"
        }

    async def get_resource_cost(
        self, 
        db: Session, 
        resource_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """获取资源成本信息"""
        db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not db_resource:
            raise ValueError("资源不存在")

        # 默认计算当月成本
        if not start_time:
            start_time = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if not end_time:
            end_time = datetime.now()

        # 计算小时数
        hours = (end_time - start_time).total_seconds() / 3600
        
        # 计算成本
        hourly_cost = db_resource.hourly_cost or 0.0
        total_cost = hourly_cost * hours
        monthly_cost = db_resource.monthly_cost or 0.0
        
        return {
            "resource_id": resource_id,
            "resource_name": db_resource.name,
            "resource_type": db_resource.resource_type,
            "hourly_cost": hourly_cost,
            "monthly_cost": monthly_cost,
            "period_cost": round(total_cost, 2),
            "period_hours": round(hours, 2),
            "start_time": start_time,
            "end_time": end_time,
            "status": db_resource.status
        }
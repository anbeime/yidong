from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from app.models import ResourceMetric, Resource
from app.schemas.resource import ResourceMetricResponse, ResourceStatsResponse
from datetime import datetime, timedelta
import statistics


class MonitoringService:
    """监控服务类"""

    async def get_resource_metrics(
        self,
        db: Session,
        resource_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        metric_type: Optional[str] = None
    ) -> List[ResourceMetricResponse]:
        """获取资源监控指标"""
        query = db.query(ResourceMetric).filter(ResourceMetric.resource_id == resource_id)
        
        # 时间范围过滤
        if start_time:
            query = query.filter(ResourceMetric.timestamp >= start_time)
        if end_time:
            query = query.filter(ResourceMetric.timestamp <= end_time)
        
        # 指标类型过滤
        if metric_type:
            query = query.filter(ResourceMetric.metric_type == metric_type)
        
        # 按时间排序
        metrics = query.order_by(desc(ResourceMetric.timestamp)).limit(1000).all()
        
        return [
            ResourceMetricResponse(
                id=getattr(metric, 'id'),
                resource_id=getattr(metric, 'resource_id'),
                metric_type=getattr(metric, 'metric_type', ''),
                value=getattr(metric, 'value', 0.0),
                unit=getattr(metric, 'unit', ''),
                timestamp=getattr(metric, 'timestamp')
            )
            for metric in metrics
        ]

    async def get_resource_stats(
        self,
        db: Session,
        resource_id: int,
        period: str = "24h"
    ) -> ResourceStatsResponse:
        """获取资源统计信息"""
        # 计算时间范围
        end_time = datetime.now()
        if period == "1h":
            start_time = end_time - timedelta(hours=1)
        elif period == "24h":
            start_time = end_time - timedelta(hours=24)
        elif period == "7d":
            start_time = end_time - timedelta(days=7)
        elif period == "30d":
            start_time = end_time - timedelta(days=30)
        else:
            raise ValueError(f"不支持的时间周期: {period}")

        # 查询指标数据
        metrics_query = db.query(ResourceMetric).filter(
            and_(
                ResourceMetric.resource_id == resource_id,
                ResourceMetric.timestamp >= start_time,
                ResourceMetric.timestamp <= end_time
            )
        )

        # 分别获取不同类型的指标
        cpu_metrics = metrics_query.filter(ResourceMetric.metric_type == "cpu").all()
        memory_metrics = metrics_query.filter(ResourceMetric.metric_type == "memory").all()
        disk_metrics = metrics_query.filter(ResourceMetric.metric_type == "disk").all()
        network_metrics = metrics_query.filter(ResourceMetric.metric_type == "network").all()

        # 计算统计信息
        stats = ResourceStatsResponse(
            resource_id=resource_id,
            period=period,
            avg_cpu_usage=self._calculate_avg([m.value for m in cpu_metrics]),
            avg_memory_usage=self._calculate_avg([m.value for m in memory_metrics]),
            avg_disk_usage=self._calculate_avg([m.value for m in disk_metrics]),
            avg_network_usage=self._calculate_avg([m.value for m in network_metrics]),
            max_cpu_usage=self._calculate_max([m.value for m in cpu_metrics]),
            max_memory_usage=self._calculate_max([m.value for m in memory_metrics]),
            max_disk_usage=self._calculate_max([m.value for m in disk_metrics]),
            max_network_usage=self._calculate_max([m.value for m in network_metrics]),
            total_cost=await self._calculate_cost(db, resource_id, start_time, end_time)
        )

        return stats

    async def add_metric(
        self,
        db: Session,
        resource_id: int,
        metric_type: str,
        value: float,
        unit: str,
        timestamp: Optional[datetime] = None
    ) -> ResourceMetric:
        """添加监控指标"""
        if timestamp is None:
            timestamp = datetime.now()

        db_metric = ResourceMetric(
            resource_id=resource_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=timestamp
        )

        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)
        return db_metric

    async def get_latest_metrics(
        self,
        db: Session,
        resource_id: int
    ) -> Dict[str, Any]:
        """获取最新的监控指标"""
        # 获取每种类型的最新指标
        latest_cpu = db.query(ResourceMetric).filter(
            and_(
                ResourceMetric.resource_id == resource_id,
                ResourceMetric.metric_type == "cpu"
            )
        ).order_by(desc(ResourceMetric.timestamp)).first()

        latest_memory = db.query(ResourceMetric).filter(
            and_(
                ResourceMetric.resource_id == resource_id,
                ResourceMetric.metric_type == "memory"
            )
        ).order_by(desc(ResourceMetric.timestamp)).first()

        latest_disk = db.query(ResourceMetric).filter(
            and_(
                ResourceMetric.resource_id == resource_id,
                ResourceMetric.metric_type == "disk"
            )
        ).order_by(desc(ResourceMetric.timestamp)).first()

        latest_network = db.query(ResourceMetric).filter(
            and_(
                ResourceMetric.resource_id == resource_id,
                ResourceMetric.metric_type == "network"
            )
        ).order_by(desc(ResourceMetric.timestamp)).first()

        return {
            "resource_id": resource_id,
            "timestamp": datetime.now(),
            "cpu_usage": latest_cpu.value if latest_cpu else 0,
            "memory_usage": latest_memory.value if latest_memory else 0,
            "disk_usage": latest_disk.value if latest_disk else 0,
            "network_usage": latest_network.value if latest_network else 0
        }

    def _calculate_avg(self, values: List[float]) -> Optional[float]:
        """计算平均值"""
        if not values:
            return None
        return statistics.mean(values)

    def _calculate_max(self, values: List[float]) -> Optional[float]:
        """计算最大值"""
        if not values:
            return None
        return max(values)

    async def _calculate_cost(
        self,
        db: Session,
        resource_id: int,
        start_time: datetime,
        end_time: datetime
    ) -> Optional[float]:
        """计算成本"""
        # 获取资源信息
        resource = db.query(Resource).filter(Resource.id == resource_id).first()
        if not resource or not resource.hourly_cost:
            return None

        # 计算时间差（小时）
        time_diff = (end_time - start_time).total_seconds() / 3600
        
        # 计算总成本
        total_cost = resource.hourly_cost * time_diff
        return round(total_cost, 2)
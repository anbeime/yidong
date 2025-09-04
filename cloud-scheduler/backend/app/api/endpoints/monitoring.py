from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio
import httpx
from pydantic import BaseModel

from app.core.database import get_db, redis_client
from app.models import Resource, ResourceMetric
from app.services.ecloud_service import resource_manager
from app.core.config import settings

router = APIRouter()


class MetricDataPoint(BaseModel):
    """监控数据点模型"""
    timestamp: datetime
    resource_id: int
    cpu_usage_percent: Optional[float] = None
    cpu_load_1m: Optional[float] = None
    cpu_load_5m: Optional[float] = None
    cpu_load_15m: Optional[float] = None
    memory_usage_percent: Optional[float] = None
    memory_used_gb: Optional[float] = None
    memory_available_gb: Optional[float] = None
    disk_usage_percent: Optional[float] = None
    disk_read_iops: Optional[float] = None
    disk_write_iops: Optional[float] = None
    disk_read_bytes: Optional[float] = None
    disk_write_bytes: Optional[float] = None
    network_in_bytes: Optional[float] = None
    network_out_bytes: Optional[float] = None
    network_in_packets: Optional[float] = None
    network_out_packets: Optional[float] = None


class MetricQuery(BaseModel):
    """监控数据查询模型"""
    resource_ids: Optional[List[int]] = None
    metric_types: Optional[List[str]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    interval: Optional[str] = "5m"  # 5m, 15m, 1h, 1d
    aggregation: Optional[str] = "avg"  # avg, max, min, sum


@router.post("/collect")
async def collect_metrics(
    metrics: List[MetricDataPoint],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """收集监控数据"""
    try:
        # 批量插入监控数据
        metric_objects = []
        for metric in metrics:
            metric_obj = ResourceMetric(
                resource_id=metric.resource_id,
                timestamp=metric.timestamp,
                cpu_usage_percent=metric.cpu_usage_percent,
                cpu_load_1m=metric.cpu_load_1m,
                cpu_load_5m=metric.cpu_load_5m,
                cpu_load_15m=metric.cpu_load_15m,
                memory_usage_percent=metric.memory_usage_percent,
                memory_used_gb=metric.memory_used_gb,
                memory_available_gb=metric.memory_available_gb,
                disk_usage_percent=metric.disk_usage_percent,
                disk_read_iops=metric.disk_read_iops,
                disk_write_iops=metric.disk_write_iops,
                disk_read_bytes=metric.disk_read_bytes,
                disk_write_bytes=metric.disk_write_bytes,
                network_in_bytes=metric.network_in_bytes,
                network_out_bytes=metric.network_out_bytes,
                network_in_packets=metric.network_in_packets,
                network_out_packets=metric.network_out_packets
            )
            metric_objects.append(metric_obj)
        
        db.bulk_save_objects(metric_objects)
        db.commit()
        
        # 在后台更新Redis缓存
        background_tasks.add_task(update_metrics_cache, metrics)
        
        return {
            "message": f"成功收集 {len(metrics)} 条监控数据",
            "count": len(metrics)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据收集失败: {str(e)}")


@router.get("/resources/{resource_id}/metrics")
async def get_resource_metrics(
    resource_id: int,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    metric_type: Optional[str] = None,
    interval: str = "5m",
    db: Session = Depends(get_db)
):
    """获取指定资源的监控数据"""
    try:
        # 设置默认时间范围（最近24小时）
        if not end_time:
            end_time = datetime.now()
        if not start_time:
            start_time = end_time - timedelta(hours=24)
        
        # 查询数据库
        query = db.query(ResourceMetric).filter(
            ResourceMetric.resource_id == resource_id,
            ResourceMetric.timestamp >= start_time,
            ResourceMetric.timestamp <= end_time
        ).order_by(ResourceMetric.timestamp)
        
        metrics = query.all()
        
        # 根据间隔聚合数据
        aggregated_metrics = aggregate_metrics(metrics, interval)
        
        # 过滤指定的指标类型
        if metric_type:
            aggregated_metrics = filter_metric_type(aggregated_metrics, metric_type)
        
        return {
            "resource_id": resource_id,
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval,
            "count": len(aggregated_metrics),
            "metrics": aggregated_metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def query_metrics(
    query: MetricQuery,
    db: Session = Depends(get_db)
):
    """高级监控数据查询"""
    try:
        # 构建查询条件
        db_query = db.query(ResourceMetric)
        
        if query.resource_ids:
            db_query = db_query.filter(ResourceMetric.resource_id.in_(query.resource_ids))
        
        if query.start_time:
            db_query = db_query.filter(ResourceMetric.timestamp >= query.start_time)
        
        if query.end_time:
            db_query = db_query.filter(ResourceMetric.timestamp <= query.end_time)
        
        db_query = db_query.order_by(ResourceMetric.timestamp)
        
        metrics = db_query.all()
        
        # 聚合数据
        if query.interval != "raw":
            metrics = aggregate_metrics(metrics, query.interval, query.aggregation)
        
        # 过滤指标类型
        if query.metric_types:
            metrics = filter_metric_types(metrics, query.metric_types)
        
        return {
            "query": query.dict(),
            "count": len(metrics),
            "metrics": metrics
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources/{resource_id}/realtime")
async def get_realtime_metrics(
    resource_id: int,
    db: Session = Depends(get_db)
):
    """获取实时监控数据"""
    try:
        # 首先尝试从Redis缓存获取
        cache_key = f"metrics:realtime:{resource_id}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            import json
            return json.loads(cached_data)
        
        # 如果缓存没有，从数据库获取最新数据
        latest_metric = db.query(ResourceMetric).filter(
            ResourceMetric.resource_id == resource_id
        ).order_by(ResourceMetric.timestamp.desc()).first()
        
        if not latest_metric:
            raise HTTPException(status_code=404, detail="未找到监控数据")
        
        realtime_data = {
            "resource_id": resource_id,
            "timestamp": latest_metric.timestamp.isoformat(),
            "cpu_usage_percent": latest_metric.cpu_usage_percent or 0,
            "memory_usage_percent": latest_metric.memory_usage_percent or 0,
            "disk_usage_percent": latest_metric.disk_usage_percent or 0,
            "network_in_bytes": latest_metric.network_in_bytes or 0,
            "network_out_bytes": latest_metric.network_out_bytes or 0,
            "status": "normal" if latest_metric.cpu_usage_percent < 80 else "warning"
        }
        
        # 缓存数据30秒
        redis_client.setex(cache_key, 30, json.dumps(realtime_data))
        
        return realtime_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取仪表板汇总数据"""
    try:
        # 获取资源列表
        resources_query = db.query(Resource)
        if project_id:
            resources_query = resources_query.filter(Resource.project_id == project_id)
        
        resources = resources_query.all()
        resource_ids = [r.id for r in resources]
        
        if not resource_ids:
            return {
                "total_resources": 0,
                "average_cpu": 0,
                "average_memory": 0,
                "total_cost": 0,
                "alerts_count": 0
            }
        
        # 获取最近的监控数据
        recent_time = datetime.now() - timedelta(minutes=30)
        recent_metrics = db.query(ResourceMetric).filter(
            ResourceMetric.resource_id.in_(resource_ids),
            ResourceMetric.timestamp >= recent_time
        ).all()
        
        # 计算平均值
        if recent_metrics:
            avg_cpu = sum(m.cpu_usage_percent or 0 for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_usage_percent or 0 for m in recent_metrics) / len(recent_metrics)
        else:
            avg_cpu = avg_memory = 0
        
        # 计算总成本
        total_cost = sum(r.cost_per_hour or 0 for r in resources) * 24 * 30  # 月成本
        
        # 计算告警数量
        alerts_count = len([m for m in recent_metrics 
                           if (m.cpu_usage_percent or 0) > 80 or (m.memory_usage_percent or 0) > 80])
        
        return {
            "total_resources": len(resources),
            "average_cpu": round(avg_cpu, 2),
            "average_memory": round(avg_memory, 2),
            "total_cost": round(total_cost, 2),
            "alerts_count": alerts_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync/all")
async def sync_all_metrics(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """同步所有资源的监控数据"""
    try:
        # 获取所有资源
        resources = db.query(Resource).filter(Resource.status == "running").all()
        
        if not resources:
            return {"message": "没有运行中的资源需要同步"}
        
        # 在后台执行同步任务
        background_tasks.add_task(sync_metrics_from_cloud, resources, db)
        
        return {
            "message": f"已启动 {len(resources)} 个资源的监控数据同步任务",
            "resource_count": len(resources)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def sync_metrics_from_cloud(resources: List[Resource], db: Session):
    """从云平台同步监控数据"""
    try:
        for resource in resources:
            try:
                # 获取最近1小时的监控数据
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=1)
                
                # 调用云平台API获取监控数据
                metrics_data = await resource_manager.get_resource_metrics(
                    resource_id=resource.resource_id,
                    metric_type="all",
                    start_time=start_time,
                    end_time=end_time
                )
                
                # 转换并保存数据
                for metric in metrics_data:
                    db_metric = ResourceMetric(
                        resource_id=resource.id,
                        timestamp=datetime.fromisoformat(metric['timestamp'].replace('Z', '+00:00')),
                        cpu_usage_percent=metric.get('value', 0) if metric.get('metric_name') == 'CPUUtilization' else None,
                        memory_usage_percent=metric.get('value', 0) if metric.get('metric_name') == 'MemoryUtilization' else None,
                        network_in_bytes=metric.get('value', 0) if metric.get('metric_name') == 'NetworkIn' else None,
                        network_out_bytes=metric.get('value', 0) if metric.get('metric_name') == 'NetworkOut' else None,
                    )
                    db.add(db_metric)
                
                db.commit()
                
            except Exception as e:
                print(f"同步资源 {resource.name} 监控数据失败: {e}")
                continue
        
        print(f"监控数据同步完成，处理了 {len(resources)} 个资源")
        
    except Exception as e:
        print(f"监控数据同步任务失败: {e}")


async def update_metrics_cache(metrics: List[MetricDataPoint]):
    """更新Redis缓存中的监控数据"""
    try:
        import json
        
        for metric in metrics:
            cache_key = f"metrics:realtime:{metric.resource_id}"
            cache_data = {
                "resource_id": metric.resource_id,
                "timestamp": metric.timestamp.isoformat(),
                "cpu_usage_percent": metric.cpu_usage_percent or 0,
                "memory_usage_percent": metric.memory_usage_percent or 0,
                "disk_usage_percent": metric.disk_usage_percent or 0,
                "network_in_bytes": metric.network_in_bytes or 0,
                "network_out_bytes": metric.network_out_bytes or 0,
            }
            
            # 缓存30秒
            redis_client.setex(cache_key, 30, json.dumps(cache_data))
            
    except Exception as e:
        print(f"更新监控数据缓存失败: {e}")


def aggregate_metrics(metrics: List[ResourceMetric], interval: str, aggregation: str = "avg") -> List[Dict]:
    """聚合监控数据"""
    try:
        if not metrics:
            return []
        
        # 计算时间窗口大小
        window_minutes = {
            "5m": 5,
            "15m": 15,
            "1h": 60,
            "1d": 1440
        }.get(interval, 5)
        
        # 按时间窗口分组
        grouped_metrics = {}
        for metric in metrics:
            # 计算时间窗口的开始时间
            window_start = metric.timestamp.replace(
                minute=(metric.timestamp.minute // window_minutes) * window_minutes,
                second=0,
                microsecond=0
            )
            
            if window_start not in grouped_metrics:
                grouped_metrics[window_start] = []
            grouped_metrics[window_start].append(metric)
        
        # 聚合每个时间窗口的数据
        result = []
        for window_time, window_metrics in sorted(grouped_metrics.items()):
            aggregated = {
                "timestamp": window_time.isoformat(),
                "count": len(window_metrics)
            }
            
            # 聚合各项指标
            for field in ["cpu_usage_percent", "memory_usage_percent", "disk_usage_percent",
                         "network_in_bytes", "network_out_bytes"]:
                values = [getattr(m, field) for m in window_metrics if getattr(m, field) is not None]
                if values:
                    if aggregation == "avg":
                        aggregated[field] = sum(values) / len(values)
                    elif aggregation == "max":
                        aggregated[field] = max(values)
                    elif aggregation == "min":
                        aggregated[field] = min(values)
                    elif aggregation == "sum":
                        aggregated[field] = sum(values)
                else:
                    aggregated[field] = 0
            
            result.append(aggregated)
        
        return result
        
    except Exception as e:
        print(f"数据聚合失败: {e}")
        return []


def filter_metric_type(metrics: List[Dict], metric_type: str) -> List[Dict]:
    """过滤指定的指标类型"""
    try:
        metric_fields = {
            "cpu": ["cpu_usage_percent", "cpu_load_1m", "cpu_load_5m", "cpu_load_15m"],
            "memory": ["memory_usage_percent", "memory_used_gb", "memory_available_gb"],
            "disk": ["disk_usage_percent", "disk_read_iops", "disk_write_iops", "disk_read_bytes", "disk_write_bytes"],
            "network": ["network_in_bytes", "network_out_bytes", "network_in_packets", "network_out_packets"]
        }
        
        if metric_type not in metric_fields:
            return metrics
        
        fields_to_keep = ["timestamp", "count"] + metric_fields[metric_type]
        
        filtered_metrics = []
        for metric in metrics:
            filtered_metric = {k: v for k, v in metric.items() if k in fields_to_keep}
            filtered_metrics.append(filtered_metric)
        
        return filtered_metrics
        
    except Exception as e:
        print(f"指标过滤失败: {e}")
        return metrics


def filter_metric_types(metrics: List[Dict], metric_types: List[str]) -> List[Dict]:
    """过滤多个指标类型"""
    try:
        all_fields = ["timestamp", "count"]
        
        metric_fields = {
            "cpu": ["cpu_usage_percent", "cpu_load_1m", "cpu_load_5m", "cpu_load_15m"],
            "memory": ["memory_usage_percent", "memory_used_gb", "memory_available_gb"],
            "disk": ["disk_usage_percent", "disk_read_iops", "disk_write_iops", "disk_read_bytes", "disk_write_bytes"],
            "network": ["network_in_bytes", "network_out_bytes", "network_in_packets", "network_out_packets"]
        }
        
        for metric_type in metric_types:
            if metric_type in metric_fields:
                all_fields.extend(metric_fields[metric_type])
        
        filtered_metrics = []
        for metric in metrics:
            filtered_metric = {k: v for k, v in metric.items() if k in all_fields}
            filtered_metrics.append(filtered_metric)
        
        return filtered_metrics
        
    except Exception as e:
        print(f"多指标过滤失败: {e}")
        return metrics
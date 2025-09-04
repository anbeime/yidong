import httpx
import json
import hashlib
import hmac
import time
import urllib.parse
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class ECloudAPIClient:
    """移动云API客户端"""
    
    def __init__(self):
        self.base_url = settings.ECLOUD_API_BASE
        self.access_key = settings.ECLOUD_ACCESS_KEY
        self.secret_key = settings.ECLOUD_SECRET_KEY
        self.region = settings.ECLOUD_REGION
        
    def _generate_signature(self, method: str, path: str, params: Dict, headers: Dict) -> str:
        """生成API签名"""
        try:
            # 构建签名字符串
            timestamp = str(int(time.time()))
            nonce = str(int(time.time() * 1000))
            
            # 排序参数
            sorted_params = sorted(params.items())
            query_string = urllib.parse.urlencode(sorted_params)
            
            # 构建待签名字符串
            string_to_sign = f"{method}\n{path}\n{query_string}\n{timestamp}\n{nonce}"
            
            # 计算签名
            signature = hmac.new(
                (self.secret_key or '').encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # 更新headers
            headers.update({
                'Authorization': f'ECloud {self.access_key}:{signature}',
                'X-ECloud-Timestamp': timestamp,
                'X-ECloud-Nonce': nonce,
                'Content-Type': 'application/json'
            })
            
            return signature
            
        except Exception as e:
            logger.error(f"生成签名失败: {e}")
            raise
    
    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """发起API请求"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {}
            params = params or {}
            
            # 添加公共参数
            params.update({
                'Region': self.region,
                'Version': '2023-12-01'
            })
            
            # 生成签名
            self._generate_signature(method, endpoint, params, headers)
            
            async with httpx.AsyncClient() as client:
                if method.upper() == 'GET':
                    response = await client.get(url, params=params, headers=headers)
                elif method.upper() == 'POST':
                    response = await client.post(url, params=params, json=data, headers=headers)
                elif method.upper() == 'PUT':
                    response = await client.put(url, params=params, json=data, headers=headers)
                elif method.upper() == 'DELETE':
                    response = await client.delete(url, params=params, headers=headers)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"API请求失败: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"请求异常: {e}")
            raise
    
    async def list_instances(self, page_num: int = 1, page_size: int = 20) -> Dict:
        """获取云主机列表"""
        params = {
            'Action': 'DescribeInstances',
            'PageNumber': page_num,
            'PageSize': page_size
        }
        return await self._make_request('GET', '/api/v1/ecs/instances', params)
    
    async def get_instance_detail(self, instance_id: str) -> Dict:
        """获取云主机详情"""
        params = {
            'Action': 'DescribeInstanceAttribute',
            'InstanceId': instance_id
        }
        return await self._make_request('GET', '/api/v1/ecs/instances', params)
    
    async def start_instance(self, instance_id: str) -> Dict:
        """启动云主机"""
        data = {
            'Action': 'StartInstance',
            'InstanceId': instance_id
        }
        return await self._make_request('POST', '/api/v1/ecs/instances/start', data=data)
    
    async def stop_instance(self, instance_id: str, force: bool = False) -> Dict:
        """停止云主机"""
        data = {
            'Action': 'StopInstance',
            'InstanceId': instance_id,
            'ForceStop': force
        }
        return await self._make_request('POST', '/api/v1/ecs/instances/stop', data=data)
    
    async def resize_instance(self, instance_id: str, instance_type: str) -> Dict:
        """调整云主机规格"""
        data = {
            'Action': 'ModifyInstanceAttribute',
            'InstanceId': instance_id,
            'InstanceType': instance_type
        }
        return await self._make_request('PUT', '/api/v1/ecs/instances/resize', data=data)
    
    async def get_instance_monitoring(self, instance_id: str, start_time: str, end_time: str, metric: str = 'CPUUtilization') -> Dict:
        """获取云主机监控数据"""
        params = {
            'Action': 'GetMetricStatistics',
            'InstanceId': instance_id,
            'MetricName': metric,
            'StartTime': start_time,
            'EndTime': end_time,
            'Period': 300  # 5分钟间隔
        }
        return await self._make_request('GET', '/api/v1/cloudwatch/metrics', params)
    
    async def list_storage_volumes(self) -> Dict:
        """获取存储卷列表"""
        params = {
            'Action': 'DescribeVolumes'
        }
        return await self._make_request('GET', '/api/v1/ebs/volumes', params)
    
    async def list_vpcs(self) -> Dict:
        """获取VPC列表"""
        params = {
            'Action': 'DescribeVpcs'
        }
        return await self._make_request('GET', '/api/v1/vpc/vpcs', params)
    
    async def list_containers(self) -> Dict:
        """获取容器服务列表"""
        params = {
            'Action': 'DescribeClusters'
        }
        return await self._make_request('GET', '/api/v1/container/clusters', params)
    
    async def scale_container_service(self, cluster_id: str, service_name: str, desired_count: int) -> Dict:
        """扩缩容容器服务"""
        data = {
            'Action': 'UpdateService',
            'ClusterId': cluster_id,
            'ServiceName': service_name,
            'DesiredCount': desired_count
        }
        return await self._make_request('PUT', '/api/v1/container/services/scale', data=data)


class ResourceManager:
    """资源管理器"""
    
    def __init__(self):
        self.ecloud_client = ECloudAPIClient()
    
    async def sync_resources(self) -> List[Dict]:
        """同步云资源信息"""
        try:
            all_resources = []
            
            # 同步云主机
            instances = await self.ecloud_client.list_instances()
            for instance in instances.get('Instances', []):
                resource = {
                    'provider_id': instance['InstanceId'],
                    'name': instance.get('InstanceName', instance['InstanceId']),
                    'type': 'compute',
                    'provider': 'ecloud',
                    'region': instance.get('RegionId', self.ecloud_client.region),
                    'status': self._convert_instance_status(instance.get('Status', 'Unknown')),
                    'cpu_cores': instance.get('Cpu', 0),
                    'memory_gb': instance.get('Memory', 0) / 1024,  # 转换为GB
                    'instance_type': instance.get('InstanceType', ''),
                    'created_at': instance.get('CreationTime', ''),
                    'tags': instance.get('Tags', [])
                }
                all_resources.append(resource)
            
            # 同步存储卷
            volumes = await self.ecloud_client.list_storage_volumes()
            for volume in volumes.get('Volumes', []):
                resource = {
                    'provider_id': volume['VolumeId'],
                    'name': volume.get('VolumeName', volume['VolumeId']),
                    'type': 'storage',
                    'provider': 'ecloud',
                    'region': volume.get('RegionId', self.ecloud_client.region),
                    'status': self._convert_volume_status(volume.get('Status', 'Unknown')),
                    'storage_gb': volume.get('Size', 0),
                    'volume_type': volume.get('VolumeType', ''),
                    'created_at': volume.get('CreationTime', ''),
                    'tags': volume.get('Tags', [])
                }
                all_resources.append(resource)
            
            # 同步容器服务
            containers = await self.ecloud_client.list_containers()
            for cluster in containers.get('Clusters', []):
                resource = {
                    'provider_id': cluster['ClusterId'],
                    'name': cluster.get('ClusterName', cluster['ClusterId']),
                    'type': 'container',
                    'provider': 'ecloud',
                    'region': cluster.get('RegionId', self.ecloud_client.region),
                    'status': self._convert_cluster_status(cluster.get('State', 'Unknown')),
                    'node_count': cluster.get('NodeCount', 0),
                    'created_at': cluster.get('Created', ''),
                    'tags': cluster.get('Tags', [])
                }
                all_resources.append(resource)
            
            logger.info(f"成功同步 {len(all_resources)} 个云资源")
            return all_resources
            
        except Exception as e:
            logger.error(f"同步云资源失败: {e}")
            raise
    
    async def get_resource_metrics(self, resource_id: str, metric_type: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """获取资源监控指标"""
        try:
            # 转换时间格式
            start_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # 根据指标类型获取数据
            metrics_map = {
                'cpu': 'CPUUtilization',
                'memory': 'MemoryUtilization',
                'network_in': 'NetworkIn',
                'network_out': 'NetworkOut',
                'disk_read': 'DiskReadBytes',
                'disk_write': 'DiskWriteBytes'
            }
            
            metric_name = metrics_map.get(metric_type, 'CPUUtilization')
            
            response = await self.ecloud_client.get_instance_monitoring(
                instance_id=resource_id,
                start_time=start_str,
                end_time=end_str,
                metric=metric_name
            )
            
            # 转换数据格式
            metrics = []
            for point in response.get('Datapoints', []):
                metrics.append({
                    'timestamp': point['Timestamp'],
                    'value': point['Average'],
                    'unit': point.get('Unit', '')
                })
            
            return metrics
            
        except Exception as e:
            logger.error(f"获取资源监控指标失败: {e}")
            return []
    
    async def scale_resource(self, resource_id: str, scale_config: Dict) -> Dict:
        """扩缩容资源"""
        try:
            resource_type = scale_config.get('type', 'compute')
            
            if resource_type == 'compute':
                # 云主机扩缩容
                instance_type = scale_config.get('instance_type')
                if not instance_type:
                    return {
                        'success': False,
                        'message': '缺少instance_type参数',
                        'result': None
                    }
                result = await self.ecloud_client.resize_instance(resource_id, str(instance_type))
                
            elif resource_type == 'container':
                # 容器服务扩缩容
                cluster_id = scale_config.get('cluster_id')
                service_name = scale_config.get('service_name')
                desired_count = scale_config.get('desired_count')
                
                if not all([cluster_id, service_name, desired_count is not None]):
                    return {
                        'success': False,
                        'message': '缺少必要的容器扩缩容参数',
                        'result': None
                    }
                
                # 严格的参数类型验证和转换
                try:
                    validated_cluster_id = str(cluster_id) if cluster_id is not None else ''
                    validated_service_name = str(service_name) if service_name is not None else ''
                    validated_desired_count = int(desired_count) if desired_count is not None else 0
                    
                    if not validated_cluster_id or not validated_service_name or validated_desired_count < 0:
                        raise ValueError('参数验证失败')
                    
                    result = await self.ecloud_client.scale_container_service(
                        validated_cluster_id, validated_service_name, validated_desired_count
                    )
                except (ValueError, TypeError) as e:
                    return {
                        'success': False,
                        'message': f'参数类型错误: {str(e)}',
                        'result': None
                    }
            else:
                raise ValueError(f"不支持的资源类型: {resource_type}")
            
            return {
                'success': True,
                'message': '扩缩容操作已提交',
                'result': result
            }
            
        except Exception as e:
            logger.error(f"资源扩缩容失败: {e}")
            return {
                'success': False,
                'message': f'扩缩容失败: {str(e)}',
                'result': None
            }
    
    def _convert_instance_status(self, ecloud_status: str) -> str:
        """转换云主机状态"""
        status_map = {
            'Running': 'running',
            'Stopped': 'stopped',
            'Starting': 'starting',
            'Stopping': 'stopping',
            'Rebooting': 'rebooting'
        }
        return status_map.get(ecloud_status, 'unknown')
    
    def _convert_volume_status(self, ecloud_status: str) -> str:
        """转换存储卷状态"""
        status_map = {
            'Available': 'available',
            'In-use': 'in_use',
            'Creating': 'creating',
            'Deleting': 'deleting',
            'Error': 'error'
        }
        return status_map.get(ecloud_status, 'unknown')
    
    def _convert_cluster_status(self, ecloud_status: str) -> str:
        """转换容器集群状态"""
        status_map = {
            'ACTIVE': 'running',
            'INACTIVE': 'stopped',
            'CREATING': 'creating',
            'DELETING': 'deleting',
            'FAILED': 'error'
        }
        return status_map.get(ecloud_status, 'unknown')


# 全局资源管理器实例
resource_manager = ResourceManager()
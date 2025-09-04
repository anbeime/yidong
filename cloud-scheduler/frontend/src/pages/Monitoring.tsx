import React, { useState, useEffect } from 'react';
import { 
  Row, Col, Card, Select, DatePicker, Button, Space, Spin, Alert,
  Tabs, Table, Statistic, Tag, Switch, Tooltip, message
} from 'antd';
import { 
  ReloadOutlined, DownloadOutlined, FullscreenOutlined,
  LineChartOutlined, BarChartOutlined, PieChartOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';

const { Option } = Select;
const { RangePicker } = DatePicker;
const { TabPane } = Tabs;

interface MetricData {
  timestamp: string;
  cpu_usage_percent: number;
  memory_usage_percent: number;
  disk_usage_percent: number;
  network_in_bytes: number;
  network_out_bytes: number;
}

interface ResourceInfo {
  id: number;
  name: string;
  type: string;
  status: string;
}

const Monitoring: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [resources, setResources] = useState<ResourceInfo[]>([]);
  const [selectedResource, setSelectedResource] = useState<number | null>(null);
  const [timeRange, setTimeRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(24, 'hour'),
    dayjs()
  ]);
  const [interval, setInterval] = useState('5m');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [metricsData, setMetricsData] = useState<MetricData[]>([]);
  const [realtimeData, setRealtimeData] = useState<any>({});
  const [summary, setSummary] = useState<any>({});

  // 加载资源列表
  useEffect(() => {
    loadResources();
  }, []);

  // 自动刷新
  useEffect(() => {
    if (autoRefresh && selectedResource) {
      const timer = setInterval(() => {
        loadRealtimeData();
      }, 30000); // 30秒刷新一次

      return () => clearInterval(timer);
    }
  }, [autoRefresh, selectedResource]);

  // 加载监控数据
  useEffect(() => {
    if (selectedResource) {
      loadMetricsData();
      loadRealtimeData();
    }
  }, [selectedResource, timeRange, interval]);

  const loadResources = async () => {
    try {
      // 模拟API调用
      const mockResources: ResourceInfo[] = [
        { id: 1, name: 'Web服务器-01', type: 'compute', status: 'running' },
        { id: 2, name: 'DB服务器-01', type: 'compute', status: 'running' },
        { id: 3, name: 'Redis缓存', type: 'memory', status: 'warning' },
        { id: 4, name: 'AI计算节点', type: 'compute', status: 'running' },
        { id: 5, name: '对象存储', type: 'storage', status: 'running' }
      ];
      setResources(mockResources);
      if (mockResources.length > 0) {
        setSelectedResource(mockResources[0].id);
      }
    } catch (error) {
      message.error('加载资源列表失败');
    }
  };

  const loadMetricsData = async () => {
    if (!selectedResource) return;
    
    setLoading(true);
    try {
      // 模拟API调用生成监控数据
      const data: MetricData[] = [];
      const [start, end] = timeRange;
      const duration = end.diff(start, 'minute');
      const points = Math.min(duration / 5, 288); // 最多288个点（24小时，5分钟间隔）

      for (let i = 0; i < points; i++) {
        const timestamp = start.add(i * 5, 'minute');
        data.push({
          timestamp: timestamp.format('YYYY-MM-DD HH:mm:ss'),
          cpu_usage_percent: 20 + Math.random() * 60 + Math.sin(i * 0.1) * 15,
          memory_usage_percent: 30 + Math.random() * 50 + Math.sin(i * 0.05) * 20,
          disk_usage_percent: 10 + Math.random() * 30,
          network_in_bytes: 1000 + Math.random() * 5000,
          network_out_bytes: 800 + Math.random() * 4000
        });
      }

      setMetricsData(data);
    } catch (error) {
      message.error('加载监控数据失败');
    } finally {
      setLoading(false);
    }
  };

  const loadRealtimeData = async () => {
    if (!selectedResource) return;

    try {
      // 模拟实时数据
      const mockRealtime = {
        cpu_usage_percent: 45 + Math.random() * 30,
        memory_usage_percent: 60 + Math.random() * 20,
        disk_usage_percent: 25 + Math.random() * 15,
        network_in_bytes: 2000 + Math.random() * 3000,
        network_out_bytes: 1500 + Math.random() * 2500,
        timestamp: dayjs().format('YYYY-MM-DD HH:mm:ss')
      };
      setRealtimeData(mockRealtime);
    } catch (error) {
      console.error('加载实时数据失败:', error);
    }
  };

  // CPU使用率图表配置
  const getCpuChartOption = () => ({
    title: {
      text: 'CPU使用率趋势',
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params: any) => {
        const point = params[0];
        return `${point.name}<br/>CPU使用率: ${point.value.toFixed(2)}%`;
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: metricsData.map(d => dayjs(d.timestamp).format('HH:mm')),
      axisLabel: { 
        interval: Math.floor(metricsData.length / 10) 
      }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      name: 'CPU使用率',
      type: 'line',
      data: metricsData.map(d => d.cpu_usage_percent.toFixed(2)),
      smooth: true,
      areaStyle: {
        opacity: 0.3
      },
      lineStyle: {
        color: '#1890ff'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: '#1890ff'
          }, {
            offset: 1, color: '#ffffff'
          }]
        }
      }
    }]
  });

  // 内存使用率图表配置
  const getMemoryChartOption = () => ({
    title: {
      text: '内存使用率趋势',
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params: any) => {
        const point = params[0];
        return `${point.name}<br/>内存使用率: ${point.value.toFixed(2)}%`;
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: metricsData.map(d => dayjs(d.timestamp).format('HH:mm')),
      axisLabel: { 
        interval: Math.floor(metricsData.length / 10) 
      }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      name: '内存使用率',
      type: 'line',
      data: metricsData.map(d => d.memory_usage_percent.toFixed(2)),
      smooth: true,
      areaStyle: {
        opacity: 0.3
      },
      lineStyle: {
        color: '#52c41a'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: '#52c41a'
          }, {
            offset: 1, color: '#ffffff'
          }]
        }
      }
    }]
  });

  // 网络流量图表配置
  const getNetworkChartOption = () => ({
    title: {
      text: '网络流量趋势',
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params: any) => {
        return `${params[0].name}<br/>
                入流量: ${(params[0].value / 1024).toFixed(2)} KB/s<br/>
                出流量: ${(params[1].value / 1024).toFixed(2)} KB/s`;
      }
    },
    legend: {
      data: ['入流量', '出流量'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: metricsData.map(d => dayjs(d.timestamp).format('HH:mm')),
      axisLabel: { 
        interval: Math.floor(metricsData.length / 10) 
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => `${(value / 1024).toFixed(1)}KB/s`
      }
    },
    series: [
      {
        name: '入流量',
        type: 'line',
        data: metricsData.map(d => d.network_in_bytes.toFixed(0)),
        smooth: true,
        lineStyle: { color: '#faad14' }
      },
      {
        name: '出流量',
        type: 'line',
        data: metricsData.map(d => d.network_out_bytes.toFixed(0)),
        smooth: true,
        lineStyle: { color: '#f5222d' }
      }
    ]
  });

  // 综合监控图表
  const getOverviewChartOption = () => ({
    title: {
      text: '资源使用率综合视图',
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['CPU使用率', '内存使用率', '磁盘使用率'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: metricsData.map(d => dayjs(d.timestamp).format('HH:mm')),
      axisLabel: { 
        interval: Math.floor(metricsData.length / 10) 
      }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: 'CPU使用率',
        type: 'line',
        data: metricsData.map(d => d.cpu_usage_percent.toFixed(2)),
        smooth: true,
        lineStyle: { color: '#1890ff' }
      },
      {
        name: '内存使用率',
        type: 'line',
        data: metricsData.map(d => d.memory_usage_percent.toFixed(2)),
        smooth: true,
        lineStyle: { color: '#52c41a' }
      },
      {
        name: '磁盘使用率',
        type: 'line',
        data: metricsData.map(d => d.disk_usage_percent.toFixed(2)),
        smooth: true,
        lineStyle: { color: '#faad14' }
      }
    ]
  });

  // 实时数据表格列
  const realtimeColumns = [
    {
      title: '指标',
      dataIndex: 'metric',
      key: 'metric',
    },
    {
      title: '当前值',
      dataIndex: 'value',
      key: 'value',
      render: (value: string, record: any) => (
        <Space>
          <span style={{ fontWeight: 'bold' }}>{value}</span>
          {record.trend && (
            <Tag color={record.trend === 'up' ? 'red' : 'green'}>
              {record.trend === 'up' ? '↑' : '↓'}
            </Tag>
          )}
        </Space>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colorMap: Record<string, string> = {
          normal: 'green',
          warning: 'orange',
          critical: 'red'
        };
        return <Tag color={colorMap[status]}>{status}</Tag>;
      }
    }
  ];

  const realtimeTableData = [
    {
      key: 'cpu',
      metric: 'CPU使用率',
      value: `${realtimeData.cpu_usage_percent?.toFixed(2) || 0}%`,
      status: (realtimeData.cpu_usage_percent || 0) > 80 ? 'critical' : 
              (realtimeData.cpu_usage_percent || 0) > 60 ? 'warning' : 'normal',
      trend: Math.random() > 0.5 ? 'up' : 'down'
    },
    {
      key: 'memory',
      metric: '内存使用率',
      value: `${realtimeData.memory_usage_percent?.toFixed(2) || 0}%`,
      status: (realtimeData.memory_usage_percent || 0) > 80 ? 'critical' : 
              (realtimeData.memory_usage_percent || 0) > 60 ? 'warning' : 'normal',
      trend: Math.random() > 0.5 ? 'up' : 'down'
    },
    {
      key: 'disk',
      metric: '磁盘使用率',
      value: `${realtimeData.disk_usage_percent?.toFixed(2) || 0}%`,
      status: (realtimeData.disk_usage_percent || 0) > 80 ? 'critical' : 
              (realtimeData.disk_usage_percent || 0) > 60 ? 'warning' : 'normal',
      trend: Math.random() > 0.5 ? 'up' : 'down'
    },
    {
      key: 'network_in',
      metric: '网络入流量',
      value: `${((realtimeData.network_in_bytes || 0) / 1024).toFixed(2)} KB/s`,
      status: 'normal',
      trend: Math.random() > 0.5 ? 'up' : 'down'
    },
    {
      key: 'network_out',
      metric: '网络出流量',
      value: `${((realtimeData.network_out_bytes || 0) / 1024).toFixed(2)} KB/s`,
      status: 'normal',
      trend: Math.random() > 0.5 ? 'up' : 'down'
    }
  ];

  return (
    <div>
      {/* 控制面板 */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <Select
              style={{ width: '100%' }}
              placeholder="选择资源"
              value={selectedResource}
              onChange={setSelectedResource}
            >
              {resources.map(resource => (
                <Option key={resource.id} value={resource.id}>
                  {resource.name} ({resource.type})
                </Option>
              ))}
            </Select>
          </Col>
          
          <Col span={8}>
            <RangePicker
              style={{ width: '100%' }}
              value={timeRange}
              onChange={(dates) => setTimeRange(dates as [dayjs.Dayjs, dayjs.Dayjs])}
              showTime
              format="YYYY-MM-DD HH:mm"
            />
          </Col>
          
          <Col span={4}>
            <Select
              style={{ width: '100%' }}
              value={interval}
              onChange={setInterval}
            >
              <Option value="5m">5分钟</Option>
              <Option value="15m">15分钟</Option>
              <Option value="1h">1小时</Option>
              <Option value="1d">1天</Option>
            </Select>
          </Col>
          
          <Col span={6}>
            <Space>
              <Tooltip title="自动刷新">
                <Switch
                  checked={autoRefresh}
                  onChange={setAutoRefresh}
                  checkedChildren="自动"
                  unCheckedChildren="手动"
                />
              </Tooltip>
              
              <Button icon={<ReloadOutlined />} onClick={loadMetricsData}>
                刷新
              </Button>
              
              <Button icon={<DownloadOutlined />}>
                导出
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 实时状态卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="CPU使用率"
              value={realtimeData.cpu_usage_percent || 0}
              precision={2}
              suffix="%"
              valueStyle={{ 
                color: (realtimeData.cpu_usage_percent || 0) > 80 ? '#f5222d' : '#3f8600'
              }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="内存使用率"
              value={realtimeData.memory_usage_percent || 0}
              precision={2}
              suffix="%"
              valueStyle={{ 
                color: (realtimeData.memory_usage_percent || 0) > 80 ? '#f5222d' : '#3f8600'
              }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="磁盘使用率"
              value={realtimeData.disk_usage_percent || 0}
              precision={2}
              suffix="%"
              valueStyle={{ 
                color: (realtimeData.disk_usage_percent || 0) > 80 ? '#f5222d' : '#3f8600'
              }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="网络流量"
              value={(realtimeData.network_in_bytes || 0) / 1024}
              precision={2}
              suffix="KB/s"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 监控图表 */}
      <Tabs defaultActiveKey="overview">
        <TabPane tab={<span><LineChartOutlined />综合视图</span>} key="overview">
          <Spin spinning={loading}>
            <Row gutter={16}>
              <Col span={24}>
                <Card>
                  <ReactECharts option={getOverviewChartOption()} style={{ height: 400 }} />
                </Card>
              </Col>
            </Row>
          </Spin>
        </TabPane>

        <TabPane tab={<span><BarChartOutlined />详细指标</span>} key="details">
          <Spin spinning={loading}>
            <Row gutter={16}>
              <Col span={12}>
                <Card style={{ marginBottom: 16 }}>
                  <ReactECharts option={getCpuChartOption()} style={{ height: 300 }} />
                </Card>
              </Col>
              <Col span={12}>
                <Card style={{ marginBottom: 16 }}>
                  <ReactECharts option={getMemoryChartOption()} style={{ height: 300 }} />
                </Card>
              </Col>
              <Col span={24}>
                <Card>
                  <ReactECharts option={getNetworkChartOption()} style={{ height: 300 }} />
                </Card>
              </Col>
            </Row>
          </Spin>
        </TabPane>

        <TabPane tab={<span><PieChartOutlined />实时数据</span>} key="realtime">
          <Row gutter={16}>
            <Col span={16}>
              <Card title="实时监控指标" style={{ height: 400 }}>
                <Table
                  columns={realtimeColumns}
                  dataSource={realtimeTableData}
                  pagination={false}
                  size="middle"
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card title="系统信息" style={{ height: 400 }}>
                <div style={{ padding: '20px 0' }}>
                  <p><strong>资源名称:</strong> {resources.find(r => r.id === selectedResource)?.name}</p>
                  <p><strong>资源类型:</strong> {resources.find(r => r.id === selectedResource)?.type}</p>
                  <p><strong>运行状态:</strong> 
                    <Tag color="green" style={{ marginLeft: 8 }}>正常运行</Tag>
                  </p>
                  <p><strong>最后更新:</strong> {realtimeData.timestamp || '--'}</p>
                  <p><strong>监控间隔:</strong> 30秒</p>
                  <p><strong>数据点数:</strong> {metricsData.length}</p>
                </div>
                
                {(realtimeData.cpu_usage_percent > 80 || realtimeData.memory_usage_percent > 80) && (
                  <Alert
                    message="性能告警"
                    description="检测到资源使用率过高，建议关注资源状况"
                    type="warning"
                    style={{ marginTop: 16 }}
                  />
                )}
              </Card>
            </Col>
          </Row>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default Monitoring;
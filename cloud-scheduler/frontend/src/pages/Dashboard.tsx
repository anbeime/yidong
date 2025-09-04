import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Progress, Table, Tag, Space, Button, Alert } from 'antd';
import { 
  CloudOutlined, 
  ThunderboltOutlined, 
  DollarOutlined, 
  WarningOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import dayjs from 'dayjs';

interface ResourceData {
  id: string;
  name: string;
  type: string;
  status: 'running' | 'stopped' | 'warning';
  cpu: number;
  memory: number;
  cost: number;
}

interface MetricData {
  timestamp: string;
  cpu: number;
  memory: number;
  network: number;
}

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [resources, setResources] = useState<ResourceData[]>([]);
  const [metrics, setMetrics] = useState<MetricData[]>([]);
  const [totalCost, setTotalCost] = useState(0);
  const [savings, setSavings] = useState(0);

  // 模拟数据加载
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 模拟资源数据
      const mockResources: ResourceData[] = [
        { id: '1', name: 'Web服务器-01', type: 'compute', status: 'running', cpu: 65, memory: 78, cost: 128.50 },
        { id: '2', name: 'DB服务器-01', type: 'compute', status: 'running', cpu: 45, memory: 82, cost: 256.00 },
        { id: '3', name: 'Redis缓存', type: 'memory', status: 'warning', cpu: 25, memory: 95, cost: 64.00 },
        { id: '4', name: 'AI计算节点', type: 'compute', status: 'running', cpu: 88, memory: 67, cost: 512.00 },
        { id: '5', name: '对象存储', type: 'storage', status: 'running', cpu: 5, memory: 15, cost: 32.00 },
      ];
      
      // 模拟监控数据
      const mockMetrics: MetricData[] = [];
      for (let i = 23; i >= 0; i--) {
        mockMetrics.push({
          timestamp: dayjs().subtract(i, 'hour').format('HH:mm'),
          cpu: 40 + Math.random() * 40,
          memory: 35 + Math.random() * 45,
          network: 20 + Math.random() * 60
        });
      }
      
      setResources(mockResources);
      setMetrics(mockMetrics);
      setTotalCost(mockResources.reduce((sum, r) => sum + r.cost, 0));
      setSavings(234.56); // 模拟节省金额
      setLoading(false);
    };

    loadData();
    
    // 设置定时刷新
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  // 资源状态统计
  const resourceStats = {
    total: resources.length,
    running: resources.filter(r => r.status === 'running').length,
    warning: resources.filter(r => r.status === 'warning').length,
    stopped: resources.filter(r => r.status === 'stopped').length,
  };

  // CPU使用率趋势图配置
  const cpuTrendOption = {
    title: {
      text: 'CPU使用率趋势',
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>CPU: {c}%'
    },
    xAxis: {
      type: 'category',
      data: metrics.map(m => m.timestamp),
      axisLabel: { interval: 3 }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: { formatter: '{value}%' }
    },
    series: [{
      data: metrics.map(m => m.cpu.toFixed(1)),
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { color: '#1890ff' },
      areaStyle: { color: '#1890ff' }
    }],
    grid: { top: 60, bottom: 60, left: 60, right: 40 }
  };

  // 内存使用率趋势图配置
  const memoryTrendOption = {
    title: {
      text: '内存使用率趋势',
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>内存: {c}%'
    },
    xAxis: {
      type: 'category',
      data: metrics.map(m => m.timestamp),
      axisLabel: { interval: 3 }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: { formatter: '{value}%' }
    },
    series: [{
      data: metrics.map(m => m.memory.toFixed(1)),
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { color: '#52c41a' },
      areaStyle: { color: '#52c41a' }
    }],
    grid: { top: 60, bottom: 60, left: 60, right: 40 }
  };

  // 资源类型分布饼图
  const resourceTypeOption = {
    title: {
      text: '资源类型分布',
      left: 'center',
      textStyle: { fontSize: 16 }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [{
      name: '资源类型',
      type: 'pie',
      radius: ['30%', '70%'],
      data: [
        { value: 3, name: '计算资源', itemStyle: { color: '#1890ff' } },
        { value: 1, name: '内存资源', itemStyle: { color: '#52c41a' } },
        { value: 1, name: '存储资源', itemStyle: { color: '#faad14' } }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  };

  // 表格列配置
  const columns = [
    {
      title: '资源名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => {
        const colorMap: Record<string, string> = {
          compute: 'blue',
          memory: 'green',
          storage: 'orange'
        };
        return <Tag color={colorMap[type]}>{type}</Tag>;
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          running: { color: 'success', text: '运行中' },
          warning: { color: 'warning', text: '告警' },
          stopped: { color: 'error', text: '已停止' }
        };
        const { color, text } = statusMap[status];
        return <Tag color={color}>{text}</Tag>;
      }
    },
    {
      title: 'CPU使用率',
      dataIndex: 'cpu',
      key: 'cpu',
      render: (cpu: number) => (
        <Progress 
          percent={cpu} 
          size="small" 
          status={cpu > 80 ? 'exception' : cpu > 60 ? 'active' : 'success'}
        />
      )
    },
    {
      title: '内存使用率',
      dataIndex: 'memory',
      key: 'memory',
      render: (memory: number) => (
        <Progress 
          percent={memory} 
          size="small" 
          status={memory > 80 ? 'exception' : memory > 60 ? 'active' : 'success'}
        />
      )
    },
    {
      title: '月成本 (¥)',
      dataIndex: 'cost',
      key: 'cost',
      render: (cost: number) => `¥${cost.toFixed(2)}`
    }
  ];

  return (
    <div style={{ background: '#f5f5f5', minHeight: '100%', padding: '0' }}>
      {/* AI优化建议 */}
      <Alert
        message="AI智能建议"
        description={
          <div>
            <p>• 检测到Redis缓存内存使用率过高(95%)，建议增加内存配置或优化缓存策略</p>
            <p>• AI计算节点在未来2小时内预测负载将下降40%，可考虑临时缩容节省成本</p>
            <p>• 对象存储使用率较低，建议调整存储类型以降低成本</p>
          </div>
        }
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
        action={
          <Button size="small" type="primary">
            查看详情
          </Button>
        }
      />

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总资源数"
              value={resourceStats.total}
              prefix={<CloudOutlined />}
              suffix="个"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="运行中"
              value={resourceStats.running}
              prefix={<ThunderboltOutlined />}
              suffix="个"
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="告警资源"
              value={resourceStats.warning}
              prefix={<WarningOutlined />}
              suffix="个"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="月度成本"
              value={totalCost}
              precision={2}
              prefix={<DollarOutlined />}
              suffix="¥"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 成本优化统计 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Card>
            <Statistic
              title="本月节省成本"
              value={savings}
              precision={2}
              prefix={<ArrowDownOutlined />}
              suffix="¥"
              valueStyle={{ color: '#3f8600' }}
            />
            <div style={{ marginTop: 8, color: '#666' }}>
              通过AI智能调度节省了 15.2% 的成本
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card>
            <Statistic
              title="AI调度次数"
              value={89}
              prefix={<ArrowUpOutlined />}
              suffix="次"
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: 8, color: '#666' }}>
              本月自动调度优化，成功率 96.6%
            </div>
          </Card>
        </Col>
      </Row>

      {/* 监控图表 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card>
            <ReactECharts option={cpuTrendOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <ReactECharts option={memoryTrendOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <ReactECharts option={resourceTypeOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      {/* 资源列表 */}
      <Card title="资源列表" extra={
        <Space>
          <Button type="primary">刷新数据</Button>
          <Button>导出报告</Button>
        </Space>
      }>
        <Table
          columns={columns}
          dataSource={resources}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10, showSizeChanger: true }}
        />
      </Card>
    </div>
  );
};

export default Dashboard;
import React, { useState, useEffect } from 'react';
import { 
  Table, Card, Button, Space, Tag, Modal, Form, Input, Select, 
  Row, Col, Statistic, Progress, Tooltip, message, Drawer, Descriptions
} from 'antd';
import { 
  PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined,
  PauseCircleOutlined, SyncOutlined, EyeOutlined, ExpandAltOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';

const { Option } = Select;

interface Resource {
  id: string;
  name: string;
  type: string;
  provider: string;
  region: string;
  status: 'running' | 'stopped' | 'warning' | 'error';
  cpu_cores: number;
  memory_gb: number;
  storage_gb: number;
  cpu_usage: number;
  memory_usage: number;
  cost_per_hour: number;
  created_at: string;
  tags: string[];
}

const Resources: React.FC = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [form] = Form.useForm();

  // 模拟数据
  useEffect(() => {
    loadResources();
  }, []);

  const loadResources = async () => {
    setLoading(true);
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const mockData: Resource[] = [
      {
        id: '1',
        name: 'Web服务器-01',
        type: 'compute',
        provider: 'ecloud',
        region: 'cn-north-1',
        status: 'running',
        cpu_cores: 4,
        memory_gb: 8,
        storage_gb: 100,
        cpu_usage: 65,
        memory_usage: 78,
        cost_per_hour: 2.5,
        created_at: '2024-01-15 10:30:00',
        tags: ['web', 'production']
      },
      {
        id: '2',
        name: 'DB服务器-01',
        type: 'compute',
        provider: 'ecloud',
        region: 'cn-north-1',
        status: 'running',
        cpu_cores: 8,
        memory_gb: 32,
        storage_gb: 500,
        cpu_usage: 45,
        memory_usage: 82,
        cost_per_hour: 8.0,
        created_at: '2024-01-15 10:35:00',
        tags: ['database', 'mysql']
      },
      {
        id: '3',
        name: 'Redis缓存',
        type: 'memory',
        provider: 'ecloud',
        region: 'cn-north-1',
        status: 'warning',
        cpu_cores: 2,
        memory_gb: 16,
        storage_gb: 50,
        cpu_usage: 25,
        memory_usage: 95,
        cost_per_hour: 1.5,
        created_at: '2024-01-15 11:00:00',
        tags: ['cache', 'redis']
      },
      {
        id: '4',
        name: 'AI计算节点',
        type: 'compute',
        provider: 'ecloud',
        region: 'cn-north-1',
        status: 'running',
        cpu_cores: 16,
        memory_gb: 64,
        storage_gb: 200,
        cpu_usage: 88,
        memory_usage: 67,
        cost_per_hour: 15.0,
        created_at: '2024-01-15 14:20:00',
        tags: ['ai', 'gpu']
      },
      {
        id: '5',
        name: '对象存储',
        type: 'storage',
        provider: 'ecloud',
        region: 'cn-north-1',
        status: 'running',
        cpu_cores: 0,
        memory_gb: 0,
        storage_gb: 1000,
        cpu_usage: 5,
        memory_usage: 15,
        cost_per_hour: 0.8,
        created_at: '2024-01-15 15:45:00',
        tags: ['storage', 'backup']
      }
    ];
    
    setResources(mockData);
    setLoading(false);
  };

  // 资源操作
  const handleStart = async (resource: Resource) => {
    message.loading('启动资源中...', 1);
    // 模拟API调用
    setTimeout(() => {
      message.success(`${resource.name} 启动成功`);
      loadResources();
    }, 1000);
  };

  const handleStop = async (resource: Resource) => {
    message.loading('停止资源中...', 1);
    setTimeout(() => {
      message.success(`${resource.name} 停止成功`);
      loadResources();
    }, 1000);
  };

  const handleScale = async (resource: Resource) => {
    Modal.confirm({
      title: '资源扩缩容',
      content: '是否要对此资源进行智能扩缩容？',
      onOk: () => {
        message.loading('AI正在分析最优配置...', 2);
        setTimeout(() => {
          message.success('扩缩容建议已生成，请查看详情');
        }, 2000);
      }
    });
  };

  const handleDelete = async (resource: Resource) => {
    Modal.confirm({
      title: '删除资源',
      content: `确定要删除资源 "${resource.name}" 吗？此操作不可恢复。`,
      okType: 'danger',
      onOk: () => {
        message.success('资源删除成功');
        loadResources();
      }
    });
  };

  const showResourceDetail = (resource: Resource) => {
    setSelectedResource(resource);
    setDrawerVisible(true);
  };

  // 表格列配置
  const columns = [
    {
      title: '资源名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => {
        const typeMap: Record<string, { color: string; text: string }> = {
          compute: { color: 'blue', text: '计算' },
          memory: { color: 'green', text: '内存' },
          storage: { color: 'orange', text: '存储' }
        };
        const { color, text } = typeMap[type] || { color: 'default', text: type };
        return <Tag color={color}>{text}</Tag>;
      }
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          running: { color: 'success', text: '运行中' },
          stopped: { color: 'default', text: '已停止' },
          warning: { color: 'warning', text: '告警' },
          error: { color: 'error', text: '错误' }
        };
        const { color, text } = statusMap[status];
        return <Tag color={color}>{text}</Tag>;
      }
    },
    {
      title: '配置',
      key: 'config',
      width: 120,
      render: (_, record: Resource) => (
        <div>
          <div>CPU: {record.cpu_cores}核</div>
          <div>内存: {record.memory_gb}GB</div>
          {record.storage_gb > 0 && <div>存储: {record.storage_gb}GB</div>}
        </div>
      )
    },
    {
      title: 'CPU使用率',
      dataIndex: 'cpu_usage',
      key: 'cpu_usage',
      width: 120,
      render: (usage: number) => (
        <Progress 
          percent={usage} 
          size="small" 
          status={usage > 80 ? 'exception' : usage > 60 ? 'active' : 'success'}
        />
      )
    },
    {
      title: '内存使用率',
      dataIndex: 'memory_usage',
      key: 'memory_usage',
      width: 120,
      render: (usage: number) => (
        <Progress 
          percent={usage} 
          size="small" 
          status={usage > 80 ? 'exception' : usage > 60 ? 'active' : 'success'}
        />
      )
    },
    {
      title: '成本/小时',
      dataIndex: 'cost_per_hour',
      key: 'cost_per_hour',
      width: 100,
      render: (cost: number) => `¥${cost.toFixed(2)}`
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 150,
      render: (tags: string[]) => (
        <div>
          {tags.map(tag => (
            <Tag key={tag} size="small">{tag}</Tag>
          ))}
        </div>
      )
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      fixed: 'right' as const,
      render: (_, record: Resource) => (
        <Space size="small">
          <Tooltip title="查看详情">
            <Button 
              icon={<EyeOutlined />} 
              size="small"
              onClick={() => showResourceDetail(record)}
            />
          </Tooltip>
          
          {record.status === 'running' ? (
            <Tooltip title="停止">
              <Button 
                icon={<PauseCircleOutlined />} 
                size="small"
                onClick={() => handleStop(record)}
              />
            </Tooltip>
          ) : (
            <Tooltip title="启动">
              <Button 
                icon={<PlayCircleOutlined />} 
                size="small"
                type="primary"
                onClick={() => handleStart(record)}
              />
            </Tooltip>
          )}
          
          <Tooltip title="智能扩缩容">
            <Button 
              icon={<ExpandAltOutlined />} 
              size="small"
              onClick={() => handleScale(record)}
            />
          </Tooltip>
          
          <Tooltip title="编辑">
            <Button 
              icon={<EditOutlined />} 
              size="small"
              onClick={() => setModalVisible(true)}
            />
          </Tooltip>
          
          <Tooltip title="删除">
            <Button 
              icon={<DeleteOutlined />} 
              size="small"
              danger
              onClick={() => handleDelete(record)}
            />
          </Tooltip>
        </Space>
      )
    }
  ];

  // 资源监控图表
  const getResourceChart = (resource: Resource) => {
    const option = {
      title: {
        text: `${resource.name} - 24小时监控`,
        textStyle: { fontSize: 14 }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' }
      },
      legend: {
        data: ['CPU使用率', '内存使用率'],
        bottom: 0
      },
      xAxis: {
        type: 'category',
        data: Array.from({length: 24}, (_, i) => `${i}:00`)
      },
      yAxis: {
        type: 'value',
        max: 100,
        axisLabel: { formatter: '{value}%' }
      },
      series: [
        {
          name: 'CPU使用率',
          type: 'line',
          data: Array.from({length: 24}, () => Math.random() * 60 + 20),
          smooth: true,
          lineStyle: { color: '#1890ff' }
        },
        {
          name: '内存使用率',
          type: 'line',
          data: Array.from({length: 24}, () => Math.random() * 50 + 30),
          smooth: true,
          lineStyle: { color: '#52c41a' }
        }
      ],
      grid: { top: 40, bottom: 60, left: 60, right: 40 }
    };
    
    return <ReactECharts option={option} style={{ height: 300 }} />;
  };

  return (
    <div>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总资源数"
              value={resources.length}
              suffix="个"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="运行中"
              value={resources.filter(r => r.status === 'running').length}
              suffix="个"
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="告警资源"
              value={resources.filter(r => r.status === 'warning').length}
              suffix="个"
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总成本/小时"
              value={resources.reduce((sum, r) => sum + r.cost_per_hour, 0)}
              precision={2}
              prefix="¥"
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 资源列表 */}
      <Card 
        title="资源列表" 
        extra={
          <Space>
            <Button icon={<SyncOutlined />} onClick={loadResources}>
              刷新
            </Button>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setModalVisible(true)}
            >
              添加资源
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={resources}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1200 }}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`
          }}
        />
      </Card>

      {/* 添加/编辑资源模态框 */}
      <Modal
        title="添加资源"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        onOk={() => {
          form.validateFields().then(values => {
            console.log('添加资源:', values);
            message.success('资源添加成功');
            setModalVisible(false);
            form.resetFields();
            loadResources();
          });
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="资源名称" rules={[{ required: true }]}>
            <Input placeholder="请输入资源名称" />
          </Form.Item>
          <Form.Item name="type" label="资源类型" rules={[{ required: true }]}>
            <Select placeholder="请选择资源类型">
              <Option value="compute">计算资源</Option>
              <Option value="memory">内存资源</Option>
              <Option value="storage">存储资源</Option>
            </Select>
          </Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="cpu_cores" label="CPU核数">
                <Input type="number" placeholder="CPU核数" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="memory_gb" label="内存(GB)">
                <Input type="number" placeholder="内存大小" />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item name="region" label="地域" rules={[{ required: true }]}>
            <Select placeholder="请选择地域">
              <Option value="cn-north-1">华北1</Option>
              <Option value="cn-east-1">华东1</Option>
              <Option value="cn-south-1">华南1</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 资源详情抽屉 */}
      <Drawer
        title="资源详情"
        placement="right"
        size="large"
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
      >
        {selectedResource && (
          <div>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="资源名称">{selectedResource.name}</Descriptions.Item>
              <Descriptions.Item label="资源类型">{selectedResource.type}</Descriptions.Item>
              <Descriptions.Item label="提供商">{selectedResource.provider}</Descriptions.Item>
              <Descriptions.Item label="地域">{selectedResource.region}</Descriptions.Item>
              <Descriptions.Item label="CPU核数">{selectedResource.cpu_cores}</Descriptions.Item>
              <Descriptions.Item label="内存">{selectedResource.memory_gb}GB</Descriptions.Item>
              <Descriptions.Item label="存储">{selectedResource.storage_gb}GB</Descriptions.Item>
              <Descriptions.Item label="成本/小时">¥{selectedResource.cost_per_hour}</Descriptions.Item>
              <Descriptions.Item label="创建时间" span={2}>{selectedResource.created_at}</Descriptions.Item>
            </Descriptions>
            
            <div style={{ marginTop: 24 }}>
              {getResourceChart(selectedResource)}
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default Resources;
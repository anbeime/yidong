import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Form, 
  Input, 
  Button, 
  List, 
  Typography, 
  Progress, 
  Alert, 
  Space, 
  Tag, 
  Modal, 
  Descriptions,
  Spin,
  message
} from 'antd';
import { 
  RocketOutlined, 
  CloudOutlined, 
  CodeOutlined, 
  DatabaseOutlined,
  PlayCircleOutlined,
  DownloadOutlined,
  EyeOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;
const { TextArea } = Input;

interface GeneratedApp {
  id: string;
  name: string;
  type: string;
  requirement: string;
  created_at: string;
  status: string;
  url: string;
  tech_stack: string[];
  cloud_resources: string[];
  files_count: number;
  generated_files: string[];
  features: string[];
  complexity: string;
  cost_estimate: string;
  deployment_config: Record<string, any>;
}

interface GenerationStatus {
  project_id: string;
  status: string;
  progress: number;
  message: string;
  deployment_url?: string;
}

const AppGenerator: React.FC = () => {
  const [form] = Form.useForm();
  const [apps, setApps] = useState<GeneratedApp[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [selectedApp, setSelectedApp] = useState<GeneratedApp | null>(null);
  const [isModalVisible, setIsModalVisible] = useState(false);

  // 获取历史生成记录
  const fetchApps = async () => {
    try {
      setLoading(true);
      const response = await axios.get<GeneratedApp[]>('/api/v1/generated-apps');
      setApps(response.data);
    } catch (error) {
      console.error('获取应用列表失败:', error);
      message.error('获取应用列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 提交生成请求
  const handleSubmit = async (values: { requirement: string }) => {
    try {
      setGenerating(true);
      setProgress(0);
      setProgressMessage('正在提交生成请求...');
      
      const response = await axios.post('/cloudcoder/api/generate', {
        requirement: values.requirement
      });
      
      const { project_id } = response.data;
      setCurrentProjectId(project_id);
      pollGenerationStatus(project_id);
    } catch (error) {
      console.error('生成应用失败:', error);
      message.error('生成应用失败');
      setGenerating(false);
    }
  };

  // 轮询生成状态
  const pollGenerationStatus = async (projectId: string) => {
    try {
      const response = await axios.get<GenerationStatus>(`/cloudcoder/api/projects/${projectId}/status`);
      const status = response.data;
      
      setProgress(status.progress);
      setProgressMessage(status.message);
      
      if (status.status === 'completed') {
        message.success('应用生成完成！');
        setGenerating(false);
        fetchApps(); // 刷新应用列表
      } else if (status.status === 'error') {
        message.error('应用生成失败: ' + status.message);
        setGenerating(false);
      } else {
        // 继续轮询
        setTimeout(() => pollGenerationStatus(projectId), 1000);
      }
    } catch (error) {
      console.error('获取生成状态失败:', error);
      message.error('获取生成状态失败');
      setGenerating(false);
    }
  };

  // 查看应用详情
  const handleViewDetails = async (appId: string) => {
    try {
      const response = await axios.get<GeneratedApp>(`/api/v1/generated-apps/${appId}`);
      setSelectedApp(response.data);
      setIsModalVisible(true);
    } catch (error) {
      console.error('获取应用详情失败:', error);
      message.error('获取应用详情失败');
    }
  };

  // 访问应用
  const handleVisitApp = (url: string) => {
    window.open(url, '_blank');
  };

  // 下载代码
  const handleDownloadCode = (appId: string) => {
    message.info('代码下载功能即将实现');
  };

  useEffect(() => {
    fetchApps();
  }, []);

  return (
    <div style={{ background: '#f5f5f5', minHeight: '100%', padding: '24px' }}>
      <Card>
        <Title level={3}>
          <RocketOutlined /> AI应用生成器
        </Title>
        <Text type="secondary">使用自然语言描述您的需求，AI将自动生成完整的云原生应用</Text>
        
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          style={{ marginTop: 24 }}
        >
          <Form.Item
            name="requirement"
            label="应用需求描述"
            rules={[{ required: true, message: '请输入应用需求描述' }]}
          >
            <TextArea
              rows={4}
              placeholder="例如：我想要一个在线教育平台，支持课程管理、在线支付、直播授课..."
            />
          </Form.Item>
          
          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              size="large"
              loading={generating}
              disabled={generating}
            >
              <RocketOutlined /> AI生成应用
            </Button>
          </Form.Item>
        </Form>
        
        {generating && (
          <Card style={{ marginTop: 24 }}>
            <Title level={4}>生成进度</Title>
            <Progress percent={progress} status="active" />
            <Text>{progressMessage}</Text>
          </Card>
        )}
      </Card>
      
      <Card style={{ marginTop: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3}>
            <DatabaseOutlined /> 历史生成记录
          </Title>
          <Button onClick={fetchApps}>刷新</Button>
        </div>
        
        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <Spin size="large" />
          </div>
        ) : apps.length === 0 ? (
          <Alert
            message="暂无生成记录"
            description="您还没有生成任何应用，点击上方按钮开始生成您的第一个AI应用吧！"
            type="info"
            showIcon
          />
        ) : (
          <List
            dataSource={apps}
            renderItem={app => (
              <List.Item
                actions={[
                  <Button 
                    type="primary" 
                    icon={<EyeOutlined />} 
                    onClick={() => handleViewDetails(app.id)}
                  >
                    查看详情
                  </Button>,
                  <Button 
                    icon={<PlayCircleOutlined />} 
                    onClick={() => handleVisitApp(app.url)}
                  >
                    访问应用
                  </Button>,
                  <Button 
                    icon={<DownloadOutlined />} 
                    onClick={() => handleDownloadCode(app.id)}
                  >
                    下载代码
                  </Button>
                ]}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <Text strong>{app.name}</Text>
                      <Tag color="blue">{app.type}</Tag>
                      <Tag color={app.status === '运行中' ? 'green' : 'default'}>
                        {app.status}
                      </Tag>
                    </Space>
                  }
                  description={
                    <div>
                      <Text type="secondary">{app.requirement}</Text>
                      <br />
                      <Text type="secondary">创建时间: {app.created_at}</Text>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>
      
      <Modal
        title="应用详情"
        visible={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedApp && (
          <div>
            <Descriptions bordered column={1}>
              <Descriptions.Item label="应用名称">{selectedApp.name}</Descriptions.Item>
              <Descriptions.Item label="应用类型">{selectedApp.type}</Descriptions.Item>
              <Descriptions.Item label="复杂度">{selectedApp.complexity}</Descriptions.Item>
              <Descriptions.Item label="创建时间">{selectedApp.created_at}</Descriptions.Item>
              <Descriptions.Item label="访问地址">
                <a href={selectedApp.url} target="_blank" rel="noopener noreferrer">
                  {selectedApp.url}
                </a>
              </Descriptions.Item>
              <Descriptions.Item label="成本估算">{selectedApp.cost_estimate}</Descriptions.Item>
              <Descriptions.Item label="技术栈">
                <Space wrap>
                  {selectedApp.tech_stack.map((tech, index) => (
                    <Tag key={index} color="blue">{tech}</Tag>
                  ))}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="云资源配置">
                <Space wrap>
                  {selectedApp.cloud_resources.map((resource, index) => (
                    <Tag key={index} icon={<CloudOutlined />} color="green">
                      {resource}
                    </Tag>
                  ))}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="功能特性">
                <Space wrap>
                  {selectedApp.features.map((feature, index) => (
                    <Tag key={index} color="purple">{feature}</Tag>
                  ))}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="生成文件数">
                {selectedApp.files_count} 个文件
              </Descriptions.Item>
            </Descriptions>
            
            <Title level={4} style={{ marginTop: 24 }}>生成的文件列表</Title>
            <List
              bordered
              dataSource={selectedApp.generated_files}
              renderItem={file => (
                <List.Item>
                  <CodeOutlined /> {file}
                </List.Item>
              )}
            />
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AppGenerator;
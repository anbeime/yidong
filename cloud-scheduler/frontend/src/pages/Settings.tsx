import React, { useState, useEffect } from 'react';
import { 
  Card, Form, Input, Select, Switch, Button, Space, message, 
  Divider, Row, Col, InputNumber, Alert, Modal, Table, Tag
} from 'antd';
import { 
  SaveOutlined, ReloadOutlined, SettingOutlined, 
  SecurityScanOutlined, CloudOutlined, BellOutlined
} from '@ant-design/icons';

const { Option } = Select;
const { TextArea } = Input;

interface SystemConfig {
  // AI配置
  ai_model_update_interval: number;
  ai_prediction_horizon: number;
  ai_confidence_threshold: number;
  
  // 监控配置
  monitoring_interval: number;
  data_retention_days: number;
  alert_cpu_threshold: number;
  alert_memory_threshold: number;
  
  // 移动云配置
  ecloud_region: string;
  ecloud_auto_sync: boolean;
  ecloud_sync_interval: number;
  
  // 调度配置
  auto_scaling_enabled: boolean;
  cost_optimization_enabled: boolean;
  schedule_execution_timeout: number;
  
  // 通知配置
  email_notifications: boolean;
  email_smtp_host: string;
  email_smtp_port: number;
  webhook_notifications: boolean;
  webhook_url: string;
}

const Settings: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState<SystemConfig>({
    // AI配置默认值
    ai_model_update_interval: 3600,
    ai_prediction_horizon: 24,
    ai_confidence_threshold: 0.7,
    
    // 监控配置默认值
    monitoring_interval: 60,
    data_retention_days: 30,
    alert_cpu_threshold: 80,
    alert_memory_threshold: 80,
    
    // 移动云配置默认值
    ecloud_region: 'cn-north-1',
    ecloud_auto_sync: true,
    ecloud_sync_interval: 300,
    
    // 调度配置默认值
    auto_scaling_enabled: true,
    cost_optimization_enabled: true,
    schedule_execution_timeout: 600,
    
    // 通知配置默认值
    email_notifications: false,
    email_smtp_host: 'smtp.qq.com',
    email_smtp_port: 587,
    webhook_notifications: false,
    webhook_url: ''
  });

  const [testResults, setTestResults] = useState<any>({});
  const [testModalVisible, setTestModalVisible] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    setLoading(true);
    try {
      // 模拟API调用加载配置
      await new Promise(resolve => setTimeout(resolve, 1000));
      form.setFieldsValue(config);
    } catch (error) {
      message.error('加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async (values: SystemConfig) => {
    setLoading(true);
    try {
      // 模拟API调用保存配置
      await new Promise(resolve => setTimeout(resolve, 1500));
      setConfig(values);
      message.success('配置保存成功');
    } catch (error) {
      message.error('配置保存失败');
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async (type: string) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResults = {
        ecloud: {
          status: 'success',
          message: '移动云连接测试成功',
          details: {
            'API端点': 'https://ecs.cmecloud.cn',
            '响应时间': '156ms',
            '认证状态': '成功',
            '可用区域': 'cn-north-1, cn-east-1'
          }
        },
        email: {
          status: 'success',
          message: '邮件服务连接测试成功',
          details: {
            'SMTP服务器': form.getFieldValue('email_smtp_host'),
            '端口': form.getFieldValue('email_smtp_port'),
            '连接状态': '成功',
            '认证方式': 'STARTTLS'
          }
        },
        webhook: {
          status: 'error',
          message: 'Webhook连接测试失败',
          details: {
            'URL': form.getFieldValue('webhook_url') || '未配置',
            '错误信息': '连接超时',
            '建议': '请检查URL是否正确并确保网络连通'
          }
        },
        ai: {
          status: 'success',
          message: 'AI引擎连接测试成功',
          details: {
            '引擎状态': '运行中',
            '模型版本': 'v1.2.3',
            '预测能力': '正常',
            '响应时间': '234ms'
          }
        }
      };

      setTestResults({ ...testResults, [type]: mockResults[type] });
      
      if (mockResults[type].status === 'success') {
        message.success(mockResults[type].message);
      } else {
        message.error(mockResults[type].message);
      }
      
    } catch (error) {
      message.error(`${type}连接测试失败`);
    } finally {
      setLoading(false);
    }
  };

  const resetConfig = () => {
    Modal.confirm({
      title: '重置配置',
      content: '确定要重置所有配置为默认值吗？此操作不可恢复。',
      onOk: () => {
        form.resetFields();
        message.success('配置已重置为默认值');
      }
    });
  };

  const showTestResults = () => {
    setTestModalVisible(true);
  };

  const testResultColumns = [
    {
      title: '测试项',
      dataIndex: 'item',
      key: 'item',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'success' ? 'green' : 'red'}>
          {status === 'success' ? '成功' : '失败'}
        </Tag>
      )
    },
    {
      title: '详情',
      dataIndex: 'details',
      key: 'details',
    }
  ];

  const getTestResultData = () => {
    const data = [];
    Object.keys(testResults).forEach(key => {
      const result = testResults[key];
      Object.keys(result.details || {}).forEach(detailKey => {
        data.push({
          key: `${key}-${detailKey}`,
          item: detailKey,
          status: result.status,
          details: result.details[detailKey]
        });
      });
    });
    return data;
  };

  return (
    <div>
      <Form
        form={form}
        layout="vertical"
        onFinish={saveConfig}
        initialValues={config}
      >
        {/* AI引擎配置 */}
        <Card 
          title={<><SettingOutlined /> AI引擎配置</>}
          style={{ marginBottom: 16 }}
          extra={
            <Button onClick={() => testConnection('ai')}>
              测试连接
            </Button>
          }
        >
          <Alert
            message="AI引擎配置说明"
            description="配置AI预测模型的更新频率、预测范围和置信度阈值，影响智能调度的准确性和响应速度。"
            type="info"
            style={{ marginBottom: 16 }}
          />
          
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="模型更新间隔"
                name="ai_model_update_interval"
                tooltip="AI模型重新训练的时间间隔（秒）"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={300}
                  max={86400}
                  addonAfter="秒"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="预测时间范围"
                name="ai_prediction_horizon"
                tooltip="AI预测未来资源使用情况的时间范围（小时）"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={1}
                  max={168}
                  addonAfter="小时"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="置信度阈值"
                name="ai_confidence_threshold"
                tooltip="AI决策的最小置信度要求"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={0.1}
                  max={1.0}
                  step={0.1}
                />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 监控配置 */}
        <Card 
          title={<><BellOutlined /> 监控告警配置</>}
          style={{ marginBottom: 16 }}
        >
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="监控数据采集间隔"
                name="monitoring_interval"
                tooltip="系统监控数据的采集频率（秒）"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={30}
                  max={3600}
                  addonAfter="秒"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="数据保留天数"
                name="data_retention_days"
                tooltip="监控数据在数据库中的保留时间"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={7}
                  max={365}
                  addonAfter="天"
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="CPU告警阈值"
                name="alert_cpu_threshold"
                tooltip="CPU使用率超过此值时触发告警"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={50}
                  max={95}
                  addonAfter="%"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="内存告警阈值"
                name="alert_memory_threshold"
                tooltip="内存使用率超过此值时触发告警"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={50}
                  max={95}
                  addonAfter="%"
                />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 移动云配置 */}
        <Card 
          title={<><CloudOutlined /> 移动云集成配置</>}
          style={{ marginBottom: 16 }}
          extra={
            <Button onClick={() => testConnection('ecloud')}>
              测试连接
            </Button>
          }
        >
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="默认地域"
                name="ecloud_region"
                tooltip="移动云资源的默认部署地域"
              >
                <Select>
                  <Option value="cn-north-1">华北1（北京）</Option>
                  <Option value="cn-east-1">华东1（上海）</Option>
                  <Option value="cn-south-1">华南1（广州）</Option>
                  <Option value="cn-west-1">西南1（成都）</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="自动同步资源"
                name="ecloud_auto_sync"
                valuePropName="checked"
                tooltip="是否自动同步移动云上的资源信息"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="同步间隔"
                name="ecloud_sync_interval"
                tooltip="自动同步移动云资源的时间间隔（秒）"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={60}
                  max={3600}
                  addonAfter="秒"
                  disabled={!form.getFieldValue('ecloud_auto_sync')}
                />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 调度配置 */}
        <Card 
          title={<><SettingOutlined /> 智能调度配置</>}
          style={{ marginBottom: 16 }}
        >
          <Row gutter={16}>
            <Col span={8}>
              <Form.Item
                label="自动扩缩容"
                name="auto_scaling_enabled"
                valuePropName="checked"
                tooltip="是否启用基于AI预测的自动扩缩容"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="成本优化"
                name="cost_optimization_enabled"
                valuePropName="checked"
                tooltip="是否启用成本优化建议和自动调度"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item
                label="调度执行超时"
                name="schedule_execution_timeout"
                tooltip="单个调度任务的最大执行时间（秒）"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  min={60}
                  max={3600}
                  addonAfter="秒"
                />
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 通知配置 */}
        <Card 
          title={<><BellOutlined /> 通知配置</>}
          style={{ marginBottom: 16 }}
        >
          <Divider orientation="left">邮件通知</Divider>
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item
                label="启用邮件通知"
                name="email_notifications"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
            </Col>
            <Col span={9}>
              <Form.Item
                label="SMTP服务器"
                name="email_smtp_host"
              >
                <Input 
                  placeholder="如：smtp.qq.com"
                  disabled={!form.getFieldValue('email_notifications')}
                />
              </Form.Item>
            </Col>
            <Col span={6}>
              <Form.Item
                label="SMTP端口"
                name="email_smtp_port"
              >
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="587"
                  disabled={!form.getFieldValue('email_notifications')}
                />
              </Form.Item>
            </Col>
            <Col span={3}>
              <Form.Item label=" ">
                <Button 
                  onClick={() => testConnection('email')}
                  disabled={!form.getFieldValue('email_notifications')}
                >
                  测试
                </Button>
              </Form.Item>
            </Col>
          </Row>

          <Divider orientation="left">Webhook通知</Divider>
          <Row gutter={16}>
            <Col span={6}>
              <Form.Item
                label="启用Webhook"
                name="webhook_notifications"
                valuePropName="checked"
              >
                <Switch checkedChildren="开启" unCheckedChildren="关闭" />
              </Form.Item>
            </Col>
            <Col span={15}>
              <Form.Item
                label="Webhook URL"
                name="webhook_url"
              >
                <Input 
                  placeholder="https://your-webhook-url.com/notify"
                  disabled={!form.getFieldValue('webhook_notifications')}
                />
              </Form.Item>
            </Col>
            <Col span={3}>
              <Form.Item label=" ">
                <Button 
                  onClick={() => testConnection('webhook')}
                  disabled={!form.getFieldValue('webhook_notifications')}
                >
                  测试
                </Button>
              </Form.Item>
            </Col>
          </Row>
        </Card>

        {/* 操作按钮 */}
        <Card>
          <Space>
            <Button 
              type="primary" 
              icon={<SaveOutlined />}
              htmlType="submit"
              loading={loading}
              size="large"
            >
              保存配置
            </Button>
            
            <Button 
              icon={<ReloadOutlined />}
              onClick={loadConfig}
              loading={loading}
              size="large"
            >
              重新加载
            </Button>
            
            <Button 
              icon={<SettingOutlined />}
              onClick={resetConfig}
              size="large"
            >
              重置默认
            </Button>
            
            <Button 
              icon={<SecurityScanOutlined />}
              onClick={showTestResults}
              size="large"
            >
              查看测试结果
            </Button>
          </Space>
        </Card>
      </Form>

      {/* 测试结果模态框 */}
      <Modal
        title="连接测试结果"
        open={testModalVisible}
        onCancel={() => setTestModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setTestModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={800}
      >
        <Table
          columns={testResultColumns}
          dataSource={getTestResultData()}
          pagination={false}
          size="small"
        />
      </Modal>
    </div>
  );
};

export default Settings;
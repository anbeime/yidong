import React, { useState, useEffect } from 'react';
import { Layout, Menu, theme, Avatar, Dropdown, Space, Typography, Badge } from 'antd';
import {
  DashboardOutlined,
  CloudOutlined,
  BarChartOutlined,
  SettingOutlined,
  BellOutlined,
  UserOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  RocketOutlined,
} from '@ant-design/icons';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Resources from './pages/Resources';
import Monitoring from './pages/Monitoring';
import Settings from './pages/Settings';
import AppGenerator from './pages/AppGenerator';
import './App.css';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const App: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [alertCount, setAlertCount] = useState(3); // 模拟告警数量
  const navigate = useNavigate();
  const location = useLocation();
  
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 菜单项配置
  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '总览大屏',
    },
    {
      key: '/resources',
      icon: <CloudOutlined />,
      label: '资源管理',
    },
    {
      key: '/monitoring',
      icon: <BarChartOutlined />,
      label: '监控分析',
    },
    {
      key: '/app-generator',
      icon: <RocketOutlined />,
      label: 'AI应用生成',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ];

  // 用户菜单
  const userMenuItems = [
    {
      key: 'profile',
      label: '个人资料',
      icon: <UserOutlined />,
    },
    {
      key: 'logout',
      label: '退出登录',
      icon: <UserOutlined />,
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  const handleUserMenuClick = ({ key }: { key: string }) => {
    if (key === 'logout') {
      // 处理退出登录
      console.log('退出登录');
    }
  };

  useEffect(() => {
    // 模拟获取告警数量
    const fetchAlertCount = () => {
      // 这里应该调用实际的API
      setAlertCount(Math.floor(Math.random() * 10));
    };

    fetchAlertCount();
    const interval = setInterval(fetchAlertCount, 30000); // 30秒更新一次

    return () => clearInterval(interval);
  }, []);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        style={{
          background: colorBgContainer,
          borderRight: '1px solid #f0f0f0',
        }}
      >
        <div style={{ 
          height: 64, 
          margin: 16, 
          display: 'flex', 
          alignItems: 'center',
          justifyContent: collapsed ? 'center' : 'flex-start'
        }}>
          <CloudOutlined style={{ 
            fontSize: collapsed ? 24 : 20, 
            color: '#1890ff' 
          }} />
          {!collapsed && (
            <Title level={4} style={{ 
              margin: '0 0 0 8px', 
              color: '#1890ff',
              whiteSpace: 'nowrap',
              overflow: 'hidden'
            }}>
              云智调度
            </Title>
          )}
        </div>
        
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ border: 'none' }}
        />
      </Sider>
      
      <Layout>
        <Header style={{ 
          padding: '0 16px', 
          background: colorBgContainer,
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <Space>
            {React.createElement(
              collapsed ? MenuUnfoldOutlined : MenuFoldOutlined,
              {
                className: 'trigger',
                onClick: () => setCollapsed(!collapsed),
                style: { fontSize: 18, cursor: 'pointer' }
              },
            )}
            <Title level={4} style={{ margin: 0, color: '#262626' }}>
              基于AI的算网资源统一编排平台
            </Title>
          </Space>
          
          <Space size="large">
            <Badge count={alertCount} size="small">
              <BellOutlined style={{ fontSize: 18, cursor: 'pointer' }} />
            </Badge>
            
            <Dropdown 
              menu={{ 
                items: userMenuItems,
                onClick: handleUserMenuClick 
              }} 
              placement="bottomRight"
            >
              <Space style={{ cursor: 'pointer' }}>
                <Avatar icon={<UserOutlined />} />
                <span>管理员</span>
              </Space>
            </Dropdown>
          </Space>
        </Header>
        
        <Content style={{ 
          margin: '16px',
          padding: 24,
          minHeight: 280,
          background: colorBgContainer,
          borderRadius: borderRadiusLG,
        }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/resources" element={<Resources />} />
            <Route path="/monitoring" element={<Monitoring />} />
            <Route path="/app-generator" element={<AppGenerator />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

export default App;
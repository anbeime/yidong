import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { AuthProvider } from './contexts/AuthContext';
import AppRouter from './router';
import './styles/global.css';

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        {
          <AuthProvider>
            <div className="app">
              <AppRouter />
            </div>
          </AuthProvider>
        }
      </Router>
    </ConfigProvider>
  );
};

export default App;
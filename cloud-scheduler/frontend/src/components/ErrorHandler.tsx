/**
 * CloudCoder 前端错误处理组件
 * 提供统一的错误显示和用户引导
 */
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { notification } from 'antd';

// 全局类型声明
declare global {
  interface Window {
    cloudCoderErrorManager: CloudCoderErrorManager;
  }
  
  var process: {
    env: {
      NODE_ENV: 'development' | 'production' | 'test';
    }
  };
}

// 错误类型定义
interface ButtonConfig {
  text: string;
  onClick: () => void | Promise<void>;
}

interface ErrorInfo {
  success: boolean;
  error_code: string;
  error_type: string;
  error_level: string;
  title: string;
  message: string;
  suggestion: string;
  timestamp: string;
  context?: any;
  support_contact?: string;
  help_url?: string;
  componentStack?: string;
}

interface RetryConfig {
  max_retries: number;
  delay: number;
  exponential_backoff: boolean;
}

class CloudCoderErrorManager {
  private errorHistory: ErrorInfo[] = [];
  private retryCount: Map<string, number> = new Map();
  
  private retryConfigs: Record<string, RetryConfig> = {
    'NETWORK_TIMEOUT': { max_retries: 3, delay: 2000, exponential_backoff: true },
    'ECLOUD_API_ERROR': { max_retries: 2, delay: 5000, exponential_backoff: true },
    'CODE_GENERATION_FAILED': { max_retries: 1, delay: 10000, exponential_backoff: false },
    'DATABASE_CONNECTION_ERROR': { max_retries: 3, delay: 1000, exponential_backoff: true }
  };

  /**
   * 处理API错误响应
   */
  handleError(error: any, context?: any): ErrorInfo {
    let errorInfo: ErrorInfo;

    if (error.response && error.response.data) {
      // 后端返回的结构化错误
      errorInfo = error.response.data;
    } else if (error.message) {
      // 网络错误或其他错误
      errorInfo = this.createGenericError(error.message);
    } else {
      // 未知错误
      errorInfo = this.createGenericError('未知错误');
    }

    // 添加上下文信息
    if (context) {
      errorInfo.context = { ...errorInfo.context, ...context };
    }

    // 记录错误历史
    this.errorHistory.push(errorInfo);
    
    // 限制历史记录数量
    if (this.errorHistory.length > 100) {
      this.errorHistory = this.errorHistory.slice(-100);
    }

    return errorInfo;
  }

  /**
   * 创建通用错误信息
   */
  private createGenericError(message: string): ErrorInfo {
    return {
      success: false,
      error_code: 'GENERIC_ERROR',
      error_type: 'system_error',
      error_level: 'error',
      title: '系统错误',
      message: message,
      suggestion: '请刷新页面重试，如问题持续请联系技术支持',
      timestamp: new Date().toISOString(),
      support_contact: 'support@cloudcoder.com'
    };
  }

  /**
   * 显示错误通知
   */
  showError(errorInfo: ErrorInfo, options: any = {}) {
    const {
      duration = this.getNotificationDuration(errorInfo.error_level),
      showRetry = this.canRetry(errorInfo.error_code),
      showSupport = errorInfo.error_level === 'critical' || errorInfo.error_level === 'error'
    } = options;

    // 使用Ant Design的notification组件
    if (notification) {
      const config: any = {
        message: errorInfo.title,
        description: this.formatErrorMessage(errorInfo),
        duration: duration,
        placement: 'topRight'
      };

      // 根据错误级别设置图标和样式
      switch (errorInfo.error_level) {
        case 'critical':
          config.type = 'error';
          config.icon = '💥';
          break;
        case 'error':
          config.type = 'error';
          config.icon = '❌';
          break;
        case 'warning':
          config.type = 'warning';
          config.icon = '⚠️';
          break;
        case 'info':
          config.type = 'info';
          config.icon = 'ℹ️';
          break;
        default:
          config.type = 'error';
      }

      // 添加操作按钮
      const buttons: ButtonConfig[] = [];
      
      if (showRetry) {
        buttons.push({
          text: '重试',
          onClick: () => this.handleRetry(errorInfo)
        });
      }

      if (showSupport) {
        buttons.push({
          text: '联系支持',
          onClick: () => this.openSupport(errorInfo)
        });
      }

      if (errorInfo.help_url) {
        buttons.push({
          text: '查看帮助',
          onClick: () => { window.open(errorInfo.help_url, '_blank'); }
        });
      }

      if (buttons.length > 0) {
        config.btn = buttons.map((btn: any, index: number) => 
          `<button onclick="window.cloudCoderErrorManager.${btn.onClick.name}()" 
                   style="margin-right: 8px; padding: 4px 12px; border: 1px solid #d9d9d9; 
                          background: white; border-radius: 4px; cursor: pointer;">
             ${btn.text}
           </button>`
        ).join('');
      }

      notification.open(config);
    } else {
      // 降级到原生alert
      alert(`${errorInfo.title}\n\n${errorInfo.message}\n\n${errorInfo.suggestion}`);
    }
  }

  /**
   * 格式化错误消息
   */
  private formatErrorMessage(errorInfo: ErrorInfo): string {
    let message = errorInfo.message;
    
    if (errorInfo.suggestion) {
      message += `\n\n💡 建议：${errorInfo.suggestion}`;
    }

    // 添加错误码（仅在开发模式下）
    if (process.env.NODE_ENV === 'development') {
      message += `\n\n🔍 错误码：${errorInfo.error_code}`;
    }

    return message;
  }

  /**
   * 获取通知显示时长
   */
  private getNotificationDuration(level: string): number {
    switch (level) {
      case 'critical': return 0; // 不自动关闭
      case 'error': return 10;
      case 'warning': return 6;
      case 'info': return 4;
      default: return 6;
    }
  }

  /**
   * 判断是否可以重试
   */
  canRetry(errorCode: string): boolean {
    const config = this.retryConfigs[errorCode];
    if (!config) return false;

    const currentRetries = this.retryCount.get(errorCode) || 0;
    return currentRetries < config.max_retries;
  }

  /**
   * 处理重试
   */
  async handleRetry(errorInfo: ErrorInfo): Promise<void> {
    const errorCode = errorInfo.error_code;
    const config = this.retryConfigs[errorCode];
    
    if (!config || !this.canRetry(errorCode)) {
      this.showError({
        ...errorInfo,
        title: '无法重试',
        message: '已达到最大重试次数',
        suggestion: '请稍后手动重试或联系技术支持'
      });
      return;
    }

    const currentRetries = this.retryCount.get(errorCode) || 0;
    this.retryCount.set(errorCode, currentRetries + 1);

    // 计算延迟时间
    let delay = config.delay;
    if (config.exponential_backoff) {
      delay = delay * Math.pow(2, currentRetries);
    }

    // 显示重试通知
    if (notification) {
      notification.info({
        message: '正在重试...',
        description: `${delay / 1000}秒后自动重试 (${currentRetries + 1}/${config.max_retries})`,
        duration: delay / 1000
      });
    }

    // 延迟后重试
    await new Promise(resolve => setTimeout(resolve, delay));
    
    // 触发重试事件
    const retryEvent = new CustomEvent('cloudcoder-retry', {
      detail: { errorInfo, attempt: currentRetries + 1 }
    });
    window.dispatchEvent(retryEvent);
  }

  /**
   * 打开技术支持
   */
  openSupport(errorInfo: ErrorInfo): void {
    const supportData = {
      error_code: errorInfo.error_code,
      timestamp: errorInfo.timestamp,
      user_agent: navigator.userAgent,
      url: window.location.href,
      context: errorInfo.context
    };

    const mailtoUrl = `mailto:${errorInfo.support_contact}?subject=CloudCoder错误报告&body=${encodeURIComponent(
      `错误信息：\n${JSON.stringify(supportData, null, 2)}\n\n请描述您遇到的问题：\n`
    )}`;

    window.open(mailtoUrl);
  }

  /**
   * 获取错误历史
   */
  getErrorHistory(): ErrorInfo[] {
    return [...this.errorHistory];
  }

  /**
   * 清除错误历史
   */
  clearErrorHistory(): void {
    this.errorHistory = [];
    this.retryCount.clear();
  }

  /**
   * 导出错误日志
   */
  exportErrorLog(): string {
    return JSON.stringify({
      timestamp: new Date().toISOString(),
      user_agent: navigator.userAgent,
      url: window.location.href,
      errors: this.errorHistory
    }, null, 2);
  }
}

// 全局错误管理器实例
window.cloudCoderErrorManager = new CloudCoderErrorManager();

// React错误边界组件
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

interface ErrorBoundaryProps {
  children: ReactNode;
}

class CloudCoderErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error
    };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('React Error Boundary caught an error:', error, errorInfo);
    
    // 记录错误到错误管理器
    const errorData = window.cloudCoderErrorManager.handleError({
      message: error.message,
      stack: error.stack
    }, {
      component_stack: errorInfo.componentStack,
      error_boundary: true
    });

    this.setState({
      hasError: true,
      error,
      errorInfo
    });

    // 显示用户友好的错误信息
    window.cloudCoderErrorManager.showError(errorData);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '40px 20px',
          textAlign: 'center',
          backgroundColor: '#fafafa',
          borderRadius: '8px',
          margin: '20px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>💥</div>
          <h2 style={{ color: '#ff4d4f', marginBottom: '16px' }}>
            页面遇到错误
          </h2>
          <p style={{ color: '#666', marginBottom: '24px' }}>
            页面组件发生了意外错误，请尝试刷新页面
          </p>
          <div style={{ marginTop: '20px' }}>
            <button
              onClick={() => window.location.reload()}
              style={{
                padding: '8px 16px',
                marginRight: '12px',
                backgroundColor: '#1890ff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              刷新页面
            </button>
            <button
              onClick={() => window.cloudCoderErrorManager.openSupport({
                success: false,
                error_code: 'REACT_ERROR_BOUNDARY',
                error_type: 'system_error',
                error_level: 'error',
                title: 'React组件错误',
                message: this.state.error?.message || '未知错误',
                suggestion: '请联系技术支持',
                timestamp: new Date().toISOString(),
                support_contact: 'support@cloudcoder.com',
                context: {
                  error_stack: this.state.error?.stack,
                  component_stack: this.state.errorInfo?.componentStack
                }
              })}
              style={{
                padding: '8px 16px',
                backgroundColor: '#52c41a',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              联系支持
            </button>
          </div>
          
          {process.env.NODE_ENV === 'development' && (
            <details style={{ marginTop: '20px', textAlign: 'left' }}>
              <summary style={{ cursor: 'pointer', color: '#1890ff' }}>
                查看错误详情 (开发模式)
              </summary>
              <pre style={{
                backgroundColor: '#f5f5f5',
                padding: '12px',
                borderRadius: '4px',
                overflow: 'auto',
                fontSize: '12px',
                marginTop: '8px'
              }}>
                {this.state.error?.stack}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

// HTTP请求错误处理中间件
const createErrorHandlingInterceptor = () => {
  return {
    // 请求拦截器
    request: (config: any) => {
      // 添加请求ID用于错误追踪
      config.metadata = {
        requestId: `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString()
      };
      return config;
    },

    // 响应错误拦截器
    responseError: (error: any) => {
      const errorInfo = window.cloudCoderErrorManager.handleError(error, {
        url: error.config?.url,
        method: error.config?.method,
        request_id: error.config?.metadata?.requestId
      });

      // 根据错误类型决定是否显示通知
      const shouldShowNotification = ['AUTHENTICATION_FAILED', 'TOKEN_EXPIRED'].indexOf(errorInfo.error_code) === -1;
      
      if (shouldShowNotification) {
        window.cloudCoderErrorManager.showError(errorInfo);
      }

      // 返回Promise.reject以保持错误传播
      return Promise.reject(errorInfo);
    }
  };
};

// 导出错误处理相关组件和函数
export {
  CloudCoderErrorManager,
  CloudCoderErrorBoundary,
  createErrorHandlingInterceptor,
  type ErrorInfo
};
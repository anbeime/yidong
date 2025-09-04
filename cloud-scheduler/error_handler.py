#!/usr/bin/env python3
"""
CloudCoder 错误处理优化模块
提供友好的错误处理和用户体验优化
"""

import json
import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ErrorLevel(Enum):
    """错误级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """错误分类"""
    USER_INPUT = "user_input"
    SYSTEM_ERROR = "system_error"
    NETWORK_ERROR = "network_error"
    API_ERROR = "api_error"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "auth_error"
    PERMISSION_ERROR = "permission_error"
    RESOURCE_ERROR = "resource_error"

class CloudCoderErrorHandler:
    """CloudCoder统一错误处理器"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.error_messages = self._load_error_messages()
        self.error_stats = {}
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('CloudCoderErrorHandler')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # 文件日志处理器
            file_handler = logging.FileHandler('cloudcoder_errors.log', encoding='utf-8')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            # 控制台日志处理器
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(levelname)s: %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def _load_error_messages(self) -> Dict[str, Dict[str, str]]:
        """加载错误信息模板"""
        return {
            # 用户输入错误
            "EMPTY_REQUIREMENT": {
                "title": "需求描述不能为空",
                "message": "请详细描述您想要开发的应用功能和需求",
                "suggestion": "例如：'我需要一个电商平台，包含用户管理、商品展示、订单处理'"
            },
            "INVALID_APP_TYPE": {
                "title": "不支持的应用类型",
                "message": "目前支持电商、教育、CRM、通用Web应用等类型",
                "suggestion": "请选择支持的应用类型，或联系我们添加新类型"
            },
            "REQUIREMENT_TOO_COMPLEX": {
                "title": "需求过于复杂",
                "message": "您的需求包含了太多功能模块，建议分阶段开发",
                "suggestion": "请先选择3-5个核心功能进行开发"
            },
            
            # 系统错误
            "CODE_GENERATION_FAILED": {
                "title": "代码生成失败",
                "message": "AI代码生成服务暂时不可用，请稍后重试",
                "suggestion": "如果问题持续存在，请联系技术支持"
            },
            "DATABASE_CONNECTION_ERROR": {
                "title": "数据库连接失败",
                "message": "系统正在进行维护，请稍后重试",
                "suggestion": "预计维护时间：5-10分钟"
            },
            "FILE_GENERATION_ERROR": {
                "title": "文件生成失败",
                "message": "项目文件生成过程中遇到问题",
                "suggestion": "请检查项目配置或重新生成"
            },
            
            # 网络和API错误
            "ECLOUD_API_ERROR": {
                "title": "移动云API调用失败",
                "message": "无法连接到移动云服务，请检查网络连接",
                "suggestion": "请稍后重试，或检查移动云服务状态"
            },
            "NETWORK_TIMEOUT": {
                "title": "网络连接超时",
                "message": "网络响应超时，请检查网络连接",
                "suggestion": "请刷新页面或稍后重试"
            },
            "API_RATE_LIMIT": {
                "title": "请求频率过高",
                "message": "您的请求过于频繁，请稍后再试",
                "suggestion": "请等待30秒后重新尝试"
            },
            
            # 认证和权限错误
            "AUTHENTICATION_FAILED": {
                "title": "用户认证失败",
                "message": "用户名或密码错误",
                "suggestion": "请检查用户名和密码，或点击'忘记密码'重置"
            },
            "TOKEN_EXPIRED": {
                "title": "登录已过期",
                "message": "您的登录状态已过期，请重新登录",
                "suggestion": "为了账户安全，请重新登录"
            },
            "PERMISSION_DENIED": {
                "title": "权限不足",
                "message": "您没有执行此操作的权限",
                "suggestion": "请联系管理员获取相应权限"
            },
            
            # 资源错误
            "STORAGE_QUOTA_EXCEEDED": {
                "title": "存储空间不足",
                "message": "您的项目存储空间已满",
                "suggestion": "请删除一些旧项目或升级到更高版本"
            },
            "PROJECT_NOT_FOUND": {
                "title": "项目不存在",
                "message": "找不到指定的项目",
                "suggestion": "请检查项目ID或重新创建项目"
            },
            "CLOUD_RESOURCE_INSUFFICIENT": {
                "title": "云资源不足",
                "message": "当前云资源配额不足以创建新实例",
                "suggestion": "请联系客服增加配额或选择较小的资源规格"
            }
        }
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None, 
                    user_id: Optional[str] = None) -> Dict[str, Any]:
        """统一错误处理入口"""
        error_code = self._classify_error(error)
        error_info = self._format_error_response(error, error_code, context)
        
        # 记录错误日志
        self._log_error(error, error_code, context, user_id)
        
        # 更新错误统计
        self._update_error_stats(error_code)
        
        return error_info
    
    def _classify_error(self, error: Exception) -> str:
        """错误分类"""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # 根据异常类型和消息内容分类
        if "requirement" in error_message and "empty" in error_message:
            return "EMPTY_REQUIREMENT"
        elif "app_type" in error_message:
            return "INVALID_APP_TYPE"
        elif "database" in error_message or "connection" in error_message:
            return "DATABASE_CONNECTION_ERROR"
        elif "ecloud" in error_message or "api" in error_message:
            return "ECLOUD_API_ERROR"
        elif "timeout" in error_message:
            return "NETWORK_TIMEOUT"
        elif "authentication" in error_message or "login" in error_message:
            return "AUTHENTICATION_FAILED"
        elif "token" in error_message and "expired" in error_message:
            return "TOKEN_EXPIRED"
        elif "permission" in error_message:
            return "PERMISSION_DENIED"
        elif "storage" in error_message or "quota" in error_message:
            return "STORAGE_QUOTA_EXCEEDED"
        elif "not found" in error_message:
            return "PROJECT_NOT_FOUND"
        elif "generation" in error_message:
            return "CODE_GENERATION_FAILED"
        else:
            return "SYSTEM_ERROR"
    
    def _format_error_response(self, error: Exception, error_code: str, 
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """格式化错误响应"""
        error_info = self.error_messages.get(error_code, {
            "title": "系统错误",
            "message": "系统遇到未知错误，请稍后重试",
            "suggestion": "如果问题持续存在，请联系技术支持"
        })
        
        return {
            "success": False,
            "error_code": error_code,
            "error_type": self._get_error_category(error_code).value,
            "error_level": self._get_error_level(error_code).value,
            "title": error_info["title"],
            "message": error_info["message"],
            "suggestion": error_info["suggestion"],
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
            "support_contact": "support@cloudcoder.com",
            "help_url": f"https://help.cloudcoder.com/errors/{error_code.lower()}"
        }
    
    def _get_error_category(self, error_code: str) -> ErrorCategory:
        """获取错误分类"""
        category_mapping = {
            "EMPTY_REQUIREMENT": ErrorCategory.USER_INPUT,
            "INVALID_APP_TYPE": ErrorCategory.USER_INPUT,
            "REQUIREMENT_TOO_COMPLEX": ErrorCategory.USER_INPUT,
            "CODE_GENERATION_FAILED": ErrorCategory.SYSTEM_ERROR,
            "DATABASE_CONNECTION_ERROR": ErrorCategory.SYSTEM_ERROR,
            "FILE_GENERATION_ERROR": ErrorCategory.SYSTEM_ERROR,
            "ECLOUD_API_ERROR": ErrorCategory.API_ERROR,
            "NETWORK_TIMEOUT": ErrorCategory.NETWORK_ERROR,
            "API_RATE_LIMIT": ErrorCategory.API_ERROR,
            "AUTHENTICATION_FAILED": ErrorCategory.AUTHENTICATION_ERROR,
            "TOKEN_EXPIRED": ErrorCategory.AUTHENTICATION_ERROR,
            "PERMISSION_DENIED": ErrorCategory.PERMISSION_ERROR,
            "STORAGE_QUOTA_EXCEEDED": ErrorCategory.RESOURCE_ERROR,
            "PROJECT_NOT_FOUND": ErrorCategory.VALIDATION_ERROR,
            "CLOUD_RESOURCE_INSUFFICIENT": ErrorCategory.RESOURCE_ERROR,
        }
        return category_mapping.get(error_code, ErrorCategory.SYSTEM_ERROR)
    
    def _get_error_level(self, error_code: str) -> ErrorLevel:
        """获取错误级别"""
        level_mapping = {
            "EMPTY_REQUIREMENT": ErrorLevel.WARNING,
            "INVALID_APP_TYPE": ErrorLevel.WARNING,
            "REQUIREMENT_TOO_COMPLEX": ErrorLevel.INFO,
            "CODE_GENERATION_FAILED": ErrorLevel.ERROR,
            "DATABASE_CONNECTION_ERROR": ErrorLevel.CRITICAL,
            "FILE_GENERATION_ERROR": ErrorLevel.ERROR,
            "ECLOUD_API_ERROR": ErrorLevel.ERROR,
            "NETWORK_TIMEOUT": ErrorLevel.WARNING,
            "API_RATE_LIMIT": ErrorLevel.WARNING,
            "AUTHENTICATION_FAILED": ErrorLevel.ERROR,
            "TOKEN_EXPIRED": ErrorLevel.WARNING,
            "PERMISSION_DENIED": ErrorLevel.ERROR,
            "STORAGE_QUOTA_EXCEEDED": ErrorLevel.WARNING,
            "PROJECT_NOT_FOUND": ErrorLevel.WARNING,
            "CLOUD_RESOURCE_INSUFFICIENT": ErrorLevel.ERROR,
        }
        return level_mapping.get(error_code, ErrorLevel.ERROR)
    
    def _log_error(self, error: Exception, error_code: str, 
                  context: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None):
        """记录错误日志"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "error_code": error_code,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "user_id": user_id,
            "context": context or {},
            "traceback": traceback.format_exc()
        }
        
        error_level = self._get_error_level(error_code)
        
        if error_level == ErrorLevel.CRITICAL:
            self.logger.critical(f"CRITICAL ERROR: {error_code} - {json.dumps(log_data, ensure_ascii=False)}")
        elif error_level == ErrorLevel.ERROR:
            self.logger.error(f"ERROR: {error_code} - {json.dumps(log_data, ensure_ascii=False)}")
        elif error_level == ErrorLevel.WARNING:
            self.logger.warning(f"WARNING: {error_code} - {json.dumps(log_data, ensure_ascii=False)}")
        else:
            self.logger.info(f"INFO: {error_code} - {json.dumps(log_data, ensure_ascii=False)}")
    
    def _update_error_stats(self, error_code: str):
        """更新错误统计"""
        if error_code not in self.error_stats:
            self.error_stats[error_code] = {
                "count": 0,
                "first_occurrence": datetime.now().isoformat(),
                "last_occurrence": datetime.now().isoformat()
            }
        
        self.error_stats[error_code]["count"] += 1
        self.error_stats[error_code]["last_occurrence"] = datetime.now().isoformat()
    
    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计信息"""
        return {
            "total_errors": sum(stat["count"] for stat in self.error_stats.values()),
            "error_breakdown": self.error_stats,
            "top_errors": sorted(
                self.error_stats.items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )[:10]
        }

class UserFriendlyValidator:
    """用户友好的输入验证器"""
    
    def __init__(self, error_handler: CloudCoderErrorHandler):
        self.error_handler = error_handler
    
    def validate_requirement(self, requirement: str) -> Dict[str, Any]:
        """验证用户需求输入"""
        if not requirement or not requirement.strip():
            return self.error_handler.handle_error(
                ValueError("requirement cannot be empty"),
                {"validation_field": "requirement"}
            )
        
        requirement = requirement.strip()
        
        # 检查需求长度
        if len(requirement) < 10:
            return {
                "success": False,
                "error_code": "REQUIREMENT_TOO_SHORT",
                "title": "需求描述过于简单",
                "message": "请提供更详细的需求描述，至少10个字符",
                "suggestion": "建议描述应用的主要功能、用户群体和技术要求"
            }
        
        if len(requirement) > 2000:
            return {
                "success": False,
                "error_code": "REQUIREMENT_TOO_LONG",
                "title": "需求描述过长",
                "message": "需求描述请控制在2000字符以内",
                "suggestion": "请精简需求描述，突出核心功能"
            }
        
        # 检查需求复杂度
        feature_keywords = ['管理', '系统', '平台', '支付', '用户', '订单', '数据', '分析', '报表', '接口']
        feature_count = sum(1 for keyword in feature_keywords if keyword in requirement)
        
        if feature_count > 8:
            return {
                "success": False,
                "error_code": "REQUIREMENT_TOO_COMPLEX",
                "title": "需求过于复杂",
                "message": f"检测到{feature_count}个功能模块，建议分阶段开发",
                "suggestion": "请先选择3-5个核心功能进行开发，后续可以迭代添加"
            }
        
        return {"success": True, "validated_requirement": requirement}
    
    def validate_app_type(self, app_type: str) -> Dict[str, Any]:
        """验证应用类型"""
        supported_types = ['ecommerce', 'education', 'crm', 'default']
        
        if app_type not in supported_types:
            return {
                "success": False,
                "error_code": "INVALID_APP_TYPE",
                "title": "不支持的应用类型",
                "message": f"应用类型'{app_type}'暂不支持",
                "suggestion": f"支持的类型：{', '.join(supported_types)}",
                "supported_types": supported_types
            }
        
        return {"success": True, "validated_app_type": app_type}

class RetryMechanism:
    """智能重试机制"""
    
    def __init__(self, error_handler: CloudCoderErrorHandler):
        self.error_handler = error_handler
        self.retry_configs = {
            "NETWORK_TIMEOUT": {"max_retries": 3, "delay": 2},
            "ECLOUD_API_ERROR": {"max_retries": 2, "delay": 5},
            "DATABASE_CONNECTION_ERROR": {"max_retries": 3, "delay": 1},
            "CODE_GENERATION_FAILED": {"max_retries": 1, "delay": 10}
        }
    
    def should_retry(self, error_code: str, attempt: int) -> bool:
        """判断是否应该重试"""
        config = self.retry_configs.get(error_code, {"max_retries": 0})
        return attempt < config["max_retries"]
    
    def get_retry_delay(self, error_code: str, attempt: int) -> int:
        """获取重试延迟时间"""
        config = self.retry_configs.get(error_code, {"delay": 5})
        # 指数退避策略
        return config["delay"] * (2 ** attempt)

# 全局错误处理器实例
error_handler = CloudCoderErrorHandler()
validator = UserFriendlyValidator(error_handler)
retry_mechanism = RetryMechanism(error_handler)

def handle_api_error(func):
    """API错误处理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = {
                "function": func.__name__,
                "args": str(args)[:200],  # 限制日志长度
                "kwargs": str(kwargs)[:200]
            }
            return error_handler.handle_error(e, context)
    return wrapper

# 使用示例
if __name__ == "__main__":
    # 测试错误处理
    try:
        raise ValueError("requirement cannot be empty")
    except Exception as e:
        error_response = error_handler.handle_error(e, {"test": True})
        print("错误响应:", json.dumps(error_response, ensure_ascii=False, indent=2))
    
    # 测试输入验证
    validation_result = validator.validate_requirement("")
    print("验证结果:", json.dumps(validation_result, ensure_ascii=False, indent=2))
    
    # 获取错误统计
    stats = error_handler.get_error_stats()
    print("错误统计:", json.dumps(stats, ensure_ascii=False, indent=2))
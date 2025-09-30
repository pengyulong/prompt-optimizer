"""
日志工具模块
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
from datetime import datetime

from config.settings import LogConfig, AppConfig

# 全局日志配置
_loggers = {}
_initialized = False

def _init_logging():
    """初始化日志系统"""
    global _initialized
    
    if _initialized:
        return
    
    # 创建日志目录
    log_dir = os.path.dirname(LogConfig.FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LogConfig.LEVEL))
    
    # 清除现有处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 创建格式器
    formatter = logging.Formatter(LogConfig.FORMAT)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO if not AppConfig.DEBUG else logging.DEBUG)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器
    if LogConfig.FILE_PATH:
        try:
            file_handler = RotatingFileHandler(
                LogConfig.FILE_PATH,
                maxBytes=_parse_size(LogConfig.MAX_FILE_SIZE),
                backupCount=LogConfig.BACKUP_COUNT,
                encoding='utf-8'
            )
            file_handler.setLevel(getattr(logging, LogConfig.LEVEL))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"创建文件日志处理器失败: {e}")
    
    _initialized = True

def _parse_size(size_str: str) -> int:
    """解析大小字符串，如 '10MB' -> 10485760"""
    size_str = size_str.upper()
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)

def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器"""
    global _loggers
    
    if not _initialized:
        _init_logging()
    
    if name not in _loggers:
        logger = logging.getLogger(name)
        _loggers[name] = logger
    
    return _loggers[name]

class APICallLogger:
    """API调用日志器"""
    
    def __init__(self, logger_name: str = "api_calls"):
        self.logger = get_logger(logger_name)
    
    def log_request(self, provider: str, model: str, prompt_length: int, **kwargs):
        """记录API请求"""
        if not LogConfig.LOG_API_CALLS:
            return
        
        self.logger.info(
            f"API请求 - 提供商: {provider}, 模型: {model}, "
            f"提示长度: {prompt_length}, 额外参数: {kwargs}"
        )
    
    def log_response(self, provider: str, model: str, success: bool, 
                    response_time: float, tokens_used: Optional[int] = None, **kwargs):
        """记录API响应"""
        if not LogConfig.LOG_API_CALLS:
            return
        
        status = "成功" if success else "失败"
        token_info = f", tokens: {tokens_used}" if tokens_used else ""
        
        self.logger.info(
            f"API响应 - 提供商: {provider}, 模型: {model}, "
            f"状态: {status}, 用时: {response_time:.2f}s{token_info}"
        )
    
    def log_error(self, provider: str, model: str, error: str, **kwargs):
        """记录API错误"""
        self.logger.error(
            f"API错误 - 提供商: {provider}, 模型: {model}, "
            f"错误: {error}, 额外信息: {kwargs}"
        )

class UserActionLogger:
    """用户行为日志器"""
    
    def __init__(self, logger_name: str = "user_actions"):
        self.logger = get_logger(logger_name)
    
    def log_optimization(self, user_id: Optional[str], optimization_type: str, 
                        model: str, prompt_length: int, success: bool):
        """记录优化操作"""
        if not LogConfig.LOG_USER_ACTIONS:
            return
        
        user_info = f"用户: {user_id or 'anonymous'}"
        status = "成功" if success else "失败"
        
        self.logger.info(
            f"优化操作 - {user_info}, 类型: {optimization_type}, "
            f"模型: {model}, 提示长度: {prompt_length}, 状态: {status}"
        )
    
    def log_test(self, user_id: Optional[str], model: str, test_length: int, success: bool):
        """记录测试操作"""
        if not LogConfig.LOG_USER_ACTIONS:
            return
        
        user_info = f"用户: {user_id or 'anonymous'}"
        status = "成功" if success else "失败"
        
        self.logger.info(
            f"测试操作 - {user_info}, 模型: {model}, "
            f"测试长度: {test_length}, 状态: {status}"
        )
    
    def log_session(self, session_id: str, action: str, **kwargs):
        """记录会话操作"""
        if not LogConfig.LOG_USER_ACTIONS:
            return
        
        self.logger.info(
            f"会话操作 - 会话ID: {session_id}, 动作: {action}, "
            f"额外信息: {kwargs}"
        )

class PerformanceLogger:
    """性能日志器"""
    
    def __init__(self, logger_name: str = "performance"):
        self.logger = get_logger(logger_name)
    
    def log_execution_time(self, operation: str, execution_time: float, **context):
        """记录执行时间"""
        self.logger.info(
            f"性能指标 - 操作: {operation}, 执行时间: {execution_time:.2f}s, "
            f"上下文: {context}"
        )
    
    def log_memory_usage(self, operation: str, memory_mb: float, **context):
        """记录内存使用"""
        self.logger.info(
            f"内存使用 - 操作: {operation}, 内存: {memory_mb:.2f}MB, "
            f"上下文: {context}"
        )
    
    def log_token_usage(self, provider: str, model: str, tokens_prompt: int, 
                       tokens_generated: int, cost: Optional[float] = None):
        """记录Token使用"""
        cost_info = f", 成本: ${cost:.4f}" if cost else ""
        
        self.logger.info(
            f"Token使用 - 提供商: {provider}, 模型: {model}, "
            f"输入: {tokens_prompt}, 输出: {tokens_generated}{cost_info}"
        )

class StructuredLogger:
    """结构化日志器"""
    
    def __init__(self, logger_name: str):
        self.logger = get_logger(logger_name)
    
    def log_structured(self, level: str, event: str, **data):
        """记录结构化日志"""
        import json
        
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            **data
        }
        
        message = json.dumps(log_data, ensure_ascii=False, default=str)
        
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, message)

def log_function_call(func):
    """函数调用装饰器"""
    def decorator(func_obj):
        def wrapper(*args, **kwargs):
            logger = get_logger(func_obj.__module__)
            func_name = func_obj.__name__
            
            # 函数调用日志
            
            try:
                start_time = datetime.now()
                result = func_obj(*args, **kwargs)
                end_time = datetime.now()
                
                execution_time = (end_time - start_time).total_seconds()
                # 函数执行完成
                
                return result
            except Exception as e:
                logger.error(f"函数 {func_name} 执行失败: {str(e)}")
                raise
        
        return wrapper
    
    return decorator(func) if callable(func) else decorator

def log_api_call(provider: str, model: str):
    """API调用装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            api_logger = APICallLogger()
            
            # 记录请求
            prompt_length = 0
            if args and isinstance(args[0], str):
                prompt_length = len(args[0])
            
            api_logger.log_request(provider, model, prompt_length)
            
            try:
                start_time = datetime.now()
                result = func(*args, **kwargs)
                end_time = datetime.now()
                
                response_time = (end_time - start_time).total_seconds()
                
                # 记录响应
                success = getattr(result, 'success', True)
                tokens_used = getattr(result, 'tokens_used', None)
                
                api_logger.log_response(
                    provider, model, success, response_time, tokens_used
                )
                
                return result
            except Exception as e:
                api_logger.log_error(provider, model, str(e))
                raise
        
        return wrapper
    return decorator

# 创建全局日志器实例
api_logger = APICallLogger()
user_logger = UserActionLogger()
performance_logger = PerformanceLogger()

# 导出主要类和函数
__all__ = [
    "get_logger",
    "APICallLogger",
    "UserActionLogger", 
    "PerformanceLogger",
    "StructuredLogger",
    "log_function_call",
    "log_api_call",
    "api_logger",
    "user_logger",
    "performance_logger"
]
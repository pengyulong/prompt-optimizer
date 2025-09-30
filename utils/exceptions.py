"""
自定义异常类
"""

class PromptOptimizerError(Exception):
    """提示词优化器基础异常"""
    pass

class ConfigurationError(PromptOptimizerError):
    """配置错误"""
    pass

class ModelError(PromptOptimizerError):
    """模型相关错误"""
    pass

class ConnectionError(PromptOptimizerError):
    """连接错误"""
    pass

class ValidationError(PromptOptimizerError):
    """验证错误"""
    pass

class TimeoutError(PromptOptimizerError):
    """超时错误"""
    pass

class RateLimitError(PromptOptimizerError):
    """限流错误"""
    pass

class AuthenticationError(PromptOptimizerError):
    """认证错误"""
    pass

class ResourceNotFoundError(PromptOptimizerError):
    """资源未找到错误"""
    pass

class TemplateError(PromptOptimizerError):
    """模板相关错误"""
    pass
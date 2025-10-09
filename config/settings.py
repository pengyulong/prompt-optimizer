"""
配置管理模块
"""

import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from enum import Enum

# 加载环境变量
load_dotenv()

from core.models import ModelProvider

class Environment(Enum):
    """环境枚举"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"

class AppConfig:
    """应用配置"""
    
    # 基础配置
    APP_NAME = "提示词优化器"
    VERSION = "2.0.0"
    DESCRIPTION = "AI提示词优化和测试工具 - 支持多种AI模型"
    
    # 环境配置
    ENV = Environment(os.getenv("APP_ENV", "development"))
    DEBUG = os.getenv("DEBUG_MODE", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))

class ModelConfig:
    """模型配置"""
    
    # 模型定义
    MODELS = {
        ModelProvider.OLLAMA: {
            "display_name": "Ollama (本地)",
            "description": "本地部署的开源模型",
            "models": [
                {
                    "name": "qwen2.5:latest",
                    "display_name": "通义千问 2.5 (最新)",
                    "description": "阿里巴巴的中文优化模型",
                    "category": "中文优化",
                    "context_length": 32768,
                    "parameters": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "top_k": 50,
                        "repeat_penalty": 1.05,
                        "max_tokens": 8192
                    }
                }
            ]
        },
        ModelProvider.OPENAI: {
            "display_name": "OpenAI",
            "description": "OpenAI 官方模型",
            "models": [
                {
                    "name": "gpt-4o",
                    "display_name": "GPT-4o",
                    "description": "OpenAI最新的多模态模型",
                    "category": "通用对话",
                    "context_length": 128000,
                    "parameters": {
                        "temperature": 0.7,
                        "top_p": 1.0,
                        "max_tokens": 4096,
                        "frequency_penalty": 0,
                        "presence_penalty": 0
                    }
                },
                {
                    "name": "gpt-4-turbo",
                    "display_name": "GPT-4 Turbo",
                    "description": "更快速的GPT-4版本",
                    "category": "通用对话",
                    "context_length": 128000,
                    "parameters": {
                        "temperature": 0.7,
                        "top_p": 1.0,
                        "max_tokens": 4096,
                        "frequency_penalty": 0,
                        "presence_penalty": 0
                    }
                },
                {
                    "name": "gpt-3.5-turbo",
                    "display_name": "GPT-3.5 Turbo",
                    "description": "经济实用的对话模型",
                    "category": "通用对话",
                    "context_length": 16385,
                    "parameters": {
                        "temperature": 0.7,
                        "top_p": 1.0,
                        "max_tokens": 4096,
                        "frequency_penalty": 0,
                        "presence_penalty": 0
                    }
                }
            ]
        },
        ModelProvider.ANTHROPIC: {
            "display_name": "Anthropic Claude",
            "description": "Anthropic 官方模型",
            "models": [
                {
                    "name": "claude-3-5-sonnet-20241022",
                    "display_name": "Claude 3.5 Sonnet",
                    "description": "Anthropic最新的高性能模型",
                    "category": "通用对话",
                    "context_length": 200000,
                    "parameters": {
                        "temperature": 0.7,
                        "top_p": 1.0,
                        "max_tokens": 4096
                    }
                },
                {
                    "name": "claude-3-opus-20240229",
                    "display_name": "Claude 3 Opus",
                    "description": "Anthropic最强大的模型",
                    "category": "通用对话",
                    "context_length": 200000,
                    "parameters": {
                        "temperature": 0.7,
                        "top_p": 1.0,
                        "max_tokens": 4096
                    }
                }
            ]
        },
        ModelProvider.DEEPSEEK: {
            "display_name": "DeepSeek",
            "description": "深度求索模型",
            "models": [
                {
                    "name": "deepseek-chat",
                    "display_name": "DeepSeek Chat",
                    "description": "深度求索的通用对话模型",
                    "category": "通用对话",
                    "context_length": 32768,
                    "parameters": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 4096,
                        "frequency_penalty": 0,
                        "presence_penalty": 0
                    }
                },
                {
                    "name": "deepseek-reasoner",
                    "display_name": "DeepSeek推理模型",
                    "description": "深度求索的推理模型",
                    "category": "推理类模型",
                    "context_length": 32768,
                    "parameters": {
                        "temperature": 0.1,
                        "top_p": 0.95,
                        "max_tokens": 16384,
                        "frequency_penalty": 0,
                        "presence_penalty": 0
                    }
                }
            ]
        },
        ModelProvider.VLLM: {
            "display_name": "vLLM (本地)",
            "description": "本地部署的vLLM推理引擎",
            "models": [
                {
                    "name": "qwen-7b-chat",
                    "display_name": "Qwen-7B-Chat",
                    "description": "通义千问7B对话模型",
                    "category": "通用对话",
                    "context_length": 32768,
                    "parameters": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 4096,
                        "frequency_penalty": 0,
                        "presence_penalty": 0
                    }
                },
                {
                    "name": "llama-3-8b-instruct",
                    "display_name": "Llama-3-8B-Instruct",
                    "description": "Meta Llama 3 8B指令模型",
                    "category": "通用对话",
                    "context_length": 8192,
                    "parameters": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 4096,
                        "frequency_penalty": 0,
                        "presence_penalty": 0
                    }
                },
                {
                    "name": "chatglm3-6b",
                    "display_name": "ChatGLM3-6B",
                    "description": "智谱AI ChatGLM3 6B模型",
                    "category": "中文优化",
                    "context_length": 8192,
                    "parameters": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 4096,
                        "frequency_penalty": 0,
                        "presence_penalty": 0
                    }
                }
            ]
        }
    }

class APIConfig:
    """API配置"""
    
    CONFIGS = {
        ModelProvider.OLLAMA: {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "timeout": int(os.getenv("OLLAMA_TIMEOUT", "60")),
            "api_key": None
        },
        ModelProvider.OPENAI: {
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "api_key": os.getenv("OPENAI_API_KEY"),
            "timeout": int(os.getenv("OPENAI_TIMEOUT", "60"))
        },
        ModelProvider.ANTHROPIC: {
            "base_url": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "timeout": int(os.getenv("ANTHROPIC_TIMEOUT", "60"))
        },
        ModelProvider.QWEN: {
            "base_url": os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1"),
            "api_key": os.getenv("QWEN_API_KEY"),
            "timeout": int(os.getenv("QWEN_TIMEOUT", "60"))
        },
        ModelProvider.CHATGLM: {
            "base_url": os.getenv("CHATGLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
            "api_key": os.getenv("CHATGLM_API_KEY"),
            "timeout": int(os.getenv("CHATGLM_TIMEOUT", "60"))
        },
        ModelProvider.DEEPSEEK: {
            "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "timeout": int(os.getenv("DEEPSEEK_TIMEOUT", "60"))
        },
        ModelProvider.MOONSHOT: {
            "base_url": os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1"),
            "api_key": os.getenv("MOONSHOT_API_KEY"),
            "timeout": int(os.getenv("MOONSHOT_TIMEOUT", "60"))
        },
        ModelProvider.QIANFAN: {
            "base_url": os.getenv("QIANFAN_BASE_URL", "https://qianfan.baidubce.com/v2"),
            "api_key": os.getenv("QIANFAN_API_KEY", ""),
            "timeout": int(os.getenv("ERNIE_TIMEOUT", "60"))
        },
        ModelProvider.VLLM: {
            "base_url": os.getenv("VLLM_BASE_URL", "http://localhost:8000/v1"),
            "api_key": os.getenv("VLLM_API_KEY", ""),
            "timeout": int(os.getenv("VLLM_TIMEOUT", "60"))
        }
    }

class OptimizationConfig:
    """优化配置"""
    
    OPTIMIZATION_TYPES = [
        {
            "name": "通用优化",
            "key": "general",
            "description": "适用于大多数场景的通用优化策略",
            "icon": "🔧"
        },
        {
            "name": "结构化优化",
            "key": "structured", 
            "description": "增加明确的结构和格式要求",
            "icon": "📋"
        },
        {
            "name": "角色导向优化",
            "key": "role_based",
            "description": "基于特定角色或身份进行优化",
            "icon": "🎭"
        },
        {
            "name": "任务导向优化",
            "key": "task_oriented",
            "description": "针对特定任务目标进行优化",
            "icon": "🎯"
        },
        {
            "name": "创意优化",
            "key": "creative",
            "description": "提升创意性和想象力的优化",
            "icon": "💡"
        },
        {
            "name": "逻辑优化",
            "key": "logical",
            "description": "增强逻辑推理和分析能力",
            "icon": "🧠"
        }
    ]
    
    MAX_PROMPT_LENGTH = 10000
    MAX_OUTPUT_LENGTH = 20000
    DEFAULT_PROVIDER = ModelProvider.DEEPSEEK
    DEFAULT_MODEL = "deepseek-chat"

class TestConfig:
    """测试配置"""
    
    METRICS = [
        {
            "name": "accuracy",
            "display_name": "准确性",
            "description": "回答的准确性和正确性",
            "icon": "🎯"
        },
        {
            "name": "relevance",
            "display_name": "相关性",
            "description": "回答与问题的相关程度",
            "icon": "🔗"
        },
        {
            "name": "completeness",
            "display_name": "完整性",
            "description": "回答的完整性和全面性",
            "icon": "📝"
        },
        {
            "name": "clarity",
            "display_name": "清晰度",
            "description": "回答的清晰度和易理解性",
            "icon": "💎"
        },
        {
            "name": "creativity",
            "display_name": "创意性",
            "description": "回答的创新性和独特性",
            "icon": "✨"
        }
    ]
    
    MAX_TEST_LENGTH = 5000
    ENABLE_BATCH_TESTING = True
    SHOW_DETAILED_METRICS = True
    SHOW_TOKEN_USAGE = True

class UIConfig:
    """UI配置"""
    
    THEME = {
        "primary_color": "#FF6B6B",
        "background_color": "#F8F9FA",
        "text_color": "#2C3E50",
        "success_color": "#27AE60",
        "error_color": "#E74C3C",
        "warning_color": "#F39C12",
        "info_color": "#3498DB"
    }
    
    LAYOUT = {
        "sidebar_width": 350,
        "main_content_width": 1000,
        "max_width": 1400
    }
    
    FEATURES = {
        "show_model_status": True,
        "show_connection_status": True,
        "enable_dark_mode": False,
        "show_advanced_options": True,
        "auto_save_history": True
    }

class CacheConfig:
    """缓存配置"""
    
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
    MAX_CACHE_SIZE = 100
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_PREFIX = "prompt_optimizer:"

class LogConfig:
    """日志配置"""
    
    LEVEL = os.getenv("LOG_LEVEL", "INFO")
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    FILE_PATH = "logs/app.log"
    MAX_FILE_SIZE = "10MB"
    BACKUP_COUNT = 5
    LOG_API_CALLS = True
    LOG_USER_ACTIONS = True

class DatabaseConfig:
    """数据库配置"""
    
    URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    ECHO = AppConfig.DEBUG
    POOL_SIZE = 10
    MAX_OVERFLOW = 20

# 配置验证和工具函数
class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def get_available_providers(require_api_key: bool = True) -> List[ModelProvider]:
        """获取可用的模型提供商
        Args:
            require_api_key: 是否要求必须配置API Key（Ollama除外）
        """
        available = []
        
        for provider in ModelProvider:
            config = APIConfig.CONFIGS.get(provider, {})
            
            if provider == ModelProvider.OLLAMA:
                # Ollama 只需要 base_url
                if config.get("base_url"):
                    available.append(provider)
            else:
                # 根据参数决定是否检查API Key
                if not require_api_key or config.get("api_key"):
                    available.append(provider)
        
        return available
    
    @staticmethod
    def get_model_config(provider: ModelProvider, model_name: str) -> Optional[Dict[str, Any]]:
        """获取指定模型的配置"""
        provider_config = ModelConfig.MODELS.get(provider, {})
        models = provider_config.get("models", [])
        
        for model in models:
            if model["name"] == model_name:
                return model
        
        return None
    
    @staticmethod
    def get_api_config(provider: ModelProvider) -> Optional[Dict[str, Any]]:
        """获取指定提供商的API配置"""
        return APIConfig.CONFIGS.get(provider)
    
    @staticmethod
    def validate_config() -> Dict[str, Any]:
        """验证配置完整性"""
        issues = []
        warnings = []
        
        # 检查可用提供商
        available_providers = ConfigValidator.get_available_providers()
        if not available_providers:
            issues.append("没有配置任何可用的模型提供商")
        
        # 检查默认提供商
        if OptimizationConfig.DEFAULT_PROVIDER not in available_providers:
            warnings.append(f"默认提供商 '{OptimizationConfig.DEFAULT_PROVIDER.value}' 不可用")
        
        # 检查日志目录
        log_dir = os.path.dirname(LogConfig.FILE_PATH)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception as e:
                warnings.append(f"无法创建日志目录: {e}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "available_providers": [p.value for p in available_providers]
        }

# 模块加载时验证配置
_validation_result = ConfigValidator.validate_config()

# 配置验证结果已静默处理

# 配置默认模型和模型提供商
DEFAULT_PROVIDER = ModelProvider.DEEPSEEK
DEFAULT_MODEL = "deepseek-chat"

# 导出主要配置类
__all__ = [
    "AppConfig",
    "ModelConfig", 
    "APIConfig",
    "OptimizationConfig",
    "TestConfig",
    "UIConfig",
    "CacheConfig",
    "LogConfig",
    "DatabaseConfig",
    "ConfigValidator",
    "ModelProvider",
    "Environment"
]
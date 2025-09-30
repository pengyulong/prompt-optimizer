"""
应用配置文件 - 使用环境变量管理敏感信息
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# 加载环境变量
load_dotenv()

# 应用基础配置
APP_CONFIG = {
    "app_title": "提示词优化器",
    "version": "1.0.0",
    "description": "AI提示词优化和测试工具 - 支持多种AI模型",
    "debug_mode": os.getenv("DEBUG_MODE", "false").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "max_concurrent_requests": int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
}

# 模型配置 - 统一管理所有支持的模型
MODEL_CONFIG = {
    "ollama": {
        "display_name": "本地部署",
        "models": [
            {
                "name": "Qwen3-32B", 
                "display_name": "千问Qwen3-32B",
                "description": "阿里巴巴的中文优化模型",
                "category": "中文优化",
                "parameters": {
                    "temperature": 0.6,
                    "top_p": 0.95,
                    "top_k": 20,
                    "max_tokens": 16384,
                    "chat_template_kwargs": {
                        "enable_thinking": True
                    }
                }
            }
        ]
    },
    "openai": {
        "display_name": "OpenAI",
        "models": [
            {
                "name": "gpt-4o",
                "display_name": "GPT-4o",
                "description": "OpenAI最新的多模态模型",
                "category": "通用对话",
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
    "anthropic": {
        "display_name": "Anthropic Claude",
        "models": [
            {
                "name": "claude-3-5-sonnet-20241022",
                "display_name": "Claude 3.5 Sonnet",
                "description": "Anthropic最新的高性能模型",
                "category": "通用对话",
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
                "parameters": {
                    "temperature": 0.7,
                    "top_p": 1.0,
                    "max_tokens": 4096
                }
            }
        ]
    }
}

# API配置 - 从环境变量获取
API_CONFIG = {
    "ollama": {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "timeout": int(os.getenv("OLLAMA_TIMEOUT", "60")),
        "api_key": None  # Ollama 不需要 API Key
    },
    "openai": {
        "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "timeout": 60
    },
    "anthropic": {
        "base_url": os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "timeout": 60
    },
    "qwen": {
        "base_url": os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/api/v1"),
        "api_key": os.getenv("QWEN_API_KEY"),
        "timeout": 60
    },
    "chatglm": {
        "base_url": os.getenv("CHATGLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
        "api_key": os.getenv("CHATGLM_API_KEY"),
        "timeout": 60
    },
    "deepseek": {
        "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "timeout": 60
    },
    "moonshot": {
        "base_url": os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1"),
        "api_key": os.getenv("MOONSHOT_API_KEY"),
        "timeout": 60
    }
}

# 优化配置
OPTIMIZATION_CONFIG = {
    "optimization_types": [
        {
            "name": "通用优化",
            "description": "适用于大多数场景的通用优化策略",
            "prompt_template": "general_optimization"
        },
        {
            "name": "结构化优化", 
            "description": "增加明确的结构和格式要求",
            "prompt_template": "structured_optimization"
        },
        {
            "name": "角色导向优化",
            "description": "基于特定角色或身份进行优化",
            "prompt_template": "role_based_optimization"
        },
        {
            "name": "任务导向优化",
            "description": "针对特定任务目标进行优化",
            "prompt_template": "task_oriented_optimization"
        },
        {
            "name": "创意优化",
            "description": "提升创意性和想象力的优化",
            "prompt_template": "creative_optimization"
        },
        {
            "name": "逻辑优化",
            "description": "增强逻辑推理和分析能力",
            "prompt_template": "logical_optimization"
        }
    ],
    "max_prompt_length": 10000,
    "timeout": 60,
    "use_real_models": True,
    "default_provider": "ollama"  # 默认使用的模型提供商
}

# 测试配置
TEST_CONFIG = {
    "max_test_length": 5000,
    "comparison_metrics": [
        {
            "name": "accuracy",
            "display_name": "准确性",
            "description": "回答的准确性和正确性"
        },
        {
            "name": "relevance",
            "display_name": "相关性", 
            "description": "回答与问题的相关程度"
        },
        {
            "name": "completeness",
            "display_name": "完整性",
            "description": "回答的完整性和全面性"
        },
        {
            "name": "creativity",
            "display_name": "创意性",
            "description": "回答的创新性和独特性"
        },
        {
            "name": "clarity",
            "display_name": "清晰度",
            "description": "回答的清晰度和易理解性"
        }
    ],
    "show_detailed_metrics": True,
    "show_token_usage": True,
    "enable_batch_testing": True
}

# UI配置
UI_CONFIG = {
    "theme": {
        "primary_color": "#FF6B6B",
        "background_color": "#F8F9FA",
        "text_color": "#2C3E50",
        "success_color": "#27AE60",
        "error_color": "#E74C3C",
        "warning_color": "#F39C12"
    },
    "layout": {
        "sidebar_width": 300,
        "main_content_width": 800,
        "max_width": 1200
    },
    "features": {
        "show_model_status": True,
        "show_connection_status": True,
        "enable_dark_mode": True,
        "show_advanced_options": False
    }
}

# 缓存配置
CACHE_CONFIG = {
    "enable_caching": os.getenv("ENABLE_CACHE", "true").lower() == "true",
    "cache_ttl": int(os.getenv("CACHE_TTL", "3600")),
    "max_cache_size": 100,
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    "cache_prefix": "prompt_optimizer:"
}

# 日志配置
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": "logs/app.log",
    "log_api_calls": True,
    "log_user_actions": True,
    "max_log_size": "10MB",
    "backup_count": 5
}

# 错误处理配置
ERROR_CONFIG = {
    "max_retries": 3,
    "retry_delay": 1,
    "show_error_details": APP_CONFIG["debug_mode"],
    "fallback_to_simulation": False,
    "error_notification": True
}

# 数据库配置 (如果需要)
DATABASE_CONFIG = {
    "url": os.getenv("DATABASE_URL", "sqlite:///app.db"),
    "echo": APP_CONFIG["debug_mode"],
    "pool_size": 10,
    "max_overflow": 20
}

def get_model_config(provider: str, model_name: str) -> Optional[Dict[str, Any]]:
    """获取指定模型的配置"""
    if provider not in MODEL_CONFIG:
        return None
    
    for model in MODEL_CONFIG[provider]["models"]:
        if model["name"] == model_name:
            return model
    
    return None

def get_api_config(provider: str) -> Optional[Dict[str, Any]]:
    """获取指定提供商的API配置"""
    return API_CONFIG.get(provider)

def get_available_providers() -> list:
    """获取可用的模型提供商列表"""
    available = []
    
    for provider, config in API_CONFIG.items():
        # 检查必要的配置是否存在
        if provider == "ollama":
            # Ollama 只需要 base_url
            if config.get("base_url"):
                available.append(provider)
        else:
            # 其他提供商需要 API Key
            if config.get("api_key"):
                available.append(provider)
    
    return available

def validate_config() -> Dict[str, Any]:
    """验证配置完整性"""
    issues = []
    warnings = []
    
    # 检查是否有可用的模型提供商
    available_providers = get_available_providers()
    if not available_providers:
        issues.append("没有配置任何可用的模型提供商")
    
    # 检查默认提供商是否可用
    default_provider = OPTIMIZATION_CONFIG.get("default_provider")
    if default_provider not in available_providers:
        warnings.append(f"默认提供商 '{default_provider}' 不可用")
    
    # 检查日志目录
    log_dir = os.path.dirname(LOGGING_CONFIG["file_path"])
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            warnings.append(f"无法创建日志目录: {e}")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "available_providers": available_providers
    }

# 在模块加载时验证配置
_config_validation = validate_config()
if not _config_validation["valid"]:
    print("⚠️ 配置验证失败:")
    for issue in _config_validation["issues"]:
        print(f"  - {issue}")

if _config_validation["warnings"]:
    print("⚠️ 配置警告:")
    for warning in _config_validation["warnings"]:
        print(f"  - {warning}")
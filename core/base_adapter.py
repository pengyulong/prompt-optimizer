"""
基础适配器基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from core.models import (
    ModelProvider, GenerationConfig, ModelResponse, ModelInfo, ConnectionStatus
)
from config.settings import ConfigValidator
from utils.exceptions import ConfigurationError
from utils.logger import get_logger

logger = get_logger(__name__)

class BaseModelAdapter(ABC):
    """模型适配器基类"""
    
    def __init__(self, provider: ModelProvider, model_name: str, config: Optional[Dict[str, Any]] = None):
        self.provider = provider
        self.model_name = model_name
        self.config = config or {}
        self.api_config = ConfigValidator.get_api_config(provider)
        self.model_config = ConfigValidator.get_model_config(provider, model_name)
        
        if not self.api_config:
            raise ConfigurationError(f"未找到 {provider.value} 的API配置")
    
    @abstractmethod
    def check_connection(self) -> ConnectionStatus:
        """检查连接状态"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """获取可用模型列表"""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> ModelResponse:
        """生成文本"""
        pass
    
    @abstractmethod
    async def generate_async(self, prompt: str, config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步生成文本"""
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> ModelResponse:
        """聊天对话"""
        pass
    
    @abstractmethod
    async def chat_async(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步聊天对话"""
        pass
    
    def _merge_config(self, config: Optional[GenerationConfig]) -> GenerationConfig:
        """合并配置"""
        # 从模型配置获取默认参数
        default_params = self.model_config.get("parameters", {}) if self.model_config else {}
        
        if config:
            # 使用传入的配置
            merged = GenerationConfig(**config.to_dict())
        else:
            # 使用默认配置
            merged = GenerationConfig()
        
        # 应用模型默认参数
        for key, value in default_params.items():
            if hasattr(merged, key) and getattr(merged, key) == getattr(GenerationConfig(), key):
                setattr(merged, key, value)
        
        return merged

# 导出主要类
__all__ = ["BaseModelAdapter"]
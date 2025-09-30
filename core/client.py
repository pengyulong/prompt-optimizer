"""
通用模型客户端 - 统一的模型调用接口
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod

from core.models import (
    ModelProvider, GenerationConfig, ModelResponse, ModelInfo, ConnectionStatus
)
from config.settings import ConfigValidator
from utils.exceptions import ModelError, ConfigurationError, ConnectionError
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

class UniversalModelClient:
    """通用模型客户端"""
    
    def __init__(self, 
                 default_provider: Optional[Union[str, ModelProvider]] = None,
                 default_model: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        初始化通用模型客户端
        
        Args:
            default_provider: 默认模型提供商
            default_model: 默认模型名称
            config: 额外配置
        """
        self.config = config or {}
        self.adapters: Dict[str, BaseModelAdapter] = {}
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
        
        # 设置默认适配器
        if default_provider and default_model:
            if isinstance(default_provider, str):
                default_provider = ModelProvider(default_provider)
            self.default_adapter = self._get_adapter(default_provider, default_model)
        else:
            self.default_adapter = None
    
    def _get_adapter_key(self, provider: ModelProvider, model_name: str) -> str:
        """生成适配器键"""
        return f"{provider.value}:{model_name}"
    
    def _get_adapter(self, provider: ModelProvider, model_name: str) -> BaseModelAdapter:
        """获取或创建适配器"""
        adapter_key = self._get_adapter_key(provider, model_name)
        
        if adapter_key not in self.adapters:
            self.adapters[adapter_key] = self._create_adapter(provider, model_name)
        
        return self.adapters[adapter_key]
    
    def _create_adapter(self, provider: ModelProvider, model_name: str) -> BaseModelAdapter:
        """创建模型适配器"""
        try:
            if provider == ModelProvider.OLLAMA:
                from services.adapters.ollama import OllamaAdapter
                return OllamaAdapter(model_name, self.config)
            elif provider == ModelProvider.OPENAI:
                from services.adapters.openai import OpenAIModelAdapter
                return OpenAIModelAdapter(model_name, self.config)
            elif provider == ModelProvider.DEEPSEEK:
                from services.adapters.openai import OpenAIModelAdapter
                return OpenAIModelAdapter(model_name, self.config)
            elif provider == ModelProvider.VLLM:
                from services.adapters.openai import OpenAIModelAdapter
                return OpenAIModelAdapter(model_name, self.config)
            else:
                raise ModelError(f"不支持的模型提供商: {provider.value}")
        except Exception as e:
            self.logger.error(f"创建适配器失败: {provider.value}:{model_name} - {str(e)}")
            raise ModelError(f"创建适配器失败: {str(e)}")
    
    def generate(self, 
                 prompt: str,
                 provider: Optional[Union[str, ModelProvider]] = None,
                 model_name: Optional[str] = None,
                 config: Optional[GenerationConfig] = None) -> ModelResponse:
        """
        生成文本
        
        Args:
            prompt: 输入提示
            provider: 模型提供商（可选，使用默认）
            model_name: 模型名称（可选，使用默认）
            config: 生成配置
        """
        adapter = self._resolve_adapter(provider, model_name)
        
        try:
            self.logger.info(f"开始生成文本: {adapter.provider.value}:{adapter.model_name}")
            result = adapter.generate(prompt, config)
            self.logger.info(f"文本生成完成: 用时 {result.response_time:.2f}s")
            return result
        except Exception as e:
            self.logger.error(f"文本生成失败: {str(e)}")
            raise ModelError(f"文本生成失败: {str(e)}")
    
    async def generate_async(self,
                           prompt: str,
                           provider: Optional[Union[str, ModelProvider]] = None,
                           model_name: Optional[str] = None,
                           config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步生成文本"""
        adapter = self._resolve_adapter(provider, model_name)
        
        try:
            self.logger.info(f"开始异步生成文本: {adapter.provider.value}:{adapter.model_name}")
            result = await adapter.generate_async(prompt, config)
            self.logger.info(f"异步文本生成完成: 用时 {result.response_time:.2f}s")
            return result
        except Exception as e:
            self.logger.error(f"异步文本生成失败: {str(e)}")
            raise ModelError(f"异步文本生成失败: {str(e)}")
    
    def chat(self,
             messages: List[Dict[str, str]],
             provider: Optional[Union[str, ModelProvider]] = None,
             model_name: Optional[str] = None,
             config: Optional[GenerationConfig] = None) -> ModelResponse:
        """
        聊天对话
        
        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "hello"}]
            provider: 模型提供商（可选）
            model_name: 模型名称（可选）
            config: 生成配置
        """
        adapter = self._resolve_adapter(provider, model_name)
        
        try:
            self.logger.info(f"开始聊天对话: {adapter.provider.value}:{adapter.model_name}")
            result = adapter.chat(messages, config)
            self.logger.info(f"聊天对话完成: 用时 {result.response_time:.2f}s")
            return result
        except Exception as e:
            self.logger.error(f"聊天对话失败: {str(e)}")
            raise ModelError(f"聊天对话失败: {str(e)}")
    
    async def chat_async(self,
                        messages: List[Dict[str, str]],
                        provider: Optional[Union[str, ModelProvider]] = None,
                        model_name: Optional[str] = None,
                        config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步聊天对话"""
        adapter = self._resolve_adapter(provider, model_name)
        
        try:
            self.logger.info(f"开始异步聊天对话: {adapter.provider.value}:{adapter.model_name}")
            result = await adapter.chat_async(messages, config)
            self.logger.info(f"异步聊天对话完成: 用时 {result.response_time:.2f}s")
            return result
        except Exception as e:
            self.logger.error(f"异步聊天对话失败: {str(e)}")
            raise ModelError(f"异步聊天对话失败: {str(e)}")
    
    def check_connection(self, 
                        provider: Optional[Union[str, ModelProvider]] = None,
                        model_name: Optional[str] = None) -> ConnectionStatus:
        """检查连接状态"""
        adapter = self._resolve_adapter(provider, model_name)
        
        try:
            return adapter.check_connection()
        except Exception as e:
            self.logger.error(f"连接检查失败: {str(e)}")
            from datetime import datetime
            return ConnectionStatus(
                provider=adapter.provider,
                connected=False,
                status_message="连接检查失败",
                last_check=datetime.now(),
                error_details=str(e)
            )
    
    def get_available_models(self, 
                           provider: Optional[Union[str, ModelProvider]] = None) -> List[ModelInfo]:
        """获取可用模型列表"""
        if provider:
            if isinstance(provider, str):
                provider = ModelProvider(provider)
            
            # 创建一个临时适配器来获取模型列表
            try:
                # 使用一个通用的模型名称来创建适配器
                temp_adapter = self._create_adapter(provider, "temp")
                return temp_adapter.get_available_models()
            except Exception as e:
                self.logger.error(f"获取模型列表失败: {provider.value} - {str(e)}")
                return []
        else:
            # 获取所有提供商的模型
            all_models = []
            available_providers = ConfigValidator.get_available_providers()
            
            for prov in available_providers:
                try:
                    models = self.get_available_models(prov)
                    all_models.extend(models)
                except Exception as e:
                    self.logger.warning(f"跳过提供商 {prov.value}: {str(e)}")
            
            return all_models
    
    def _resolve_adapter(self, 
                        provider: Optional[Union[str, ModelProvider]], 
                        model_name: Optional[str]) -> BaseModelAdapter:
        """解析适配器"""
        if provider and model_name:
            if isinstance(provider, str):
                provider = ModelProvider(provider)
            return self._get_adapter(provider, model_name)
        elif self.default_adapter:
            return self.default_adapter
        else:
            raise ConfigurationError("未指定模型提供商和模型名称，且没有默认适配器")
    
    def list_cached_adapters(self) -> List[str]:
        """列出已缓存的适配器"""
        return list(self.adapters.keys())
    
    def clear_adapter_cache(self):
        """清除适配器缓存"""
        self.adapters.clear()
        self.logger.info("已清除适配器缓存")
    
    def get_adapter_stats(self) -> Dict[str, Any]:
        """获取适配器统计信息"""
        stats = {
            "total_adapters": len(self.adapters),
            "adapters": {},
            "default_adapter": None
        }
        
        for key, adapter in self.adapters.items():
            stats["adapters"][key] = {
                "provider": adapter.provider.value,
                "model": adapter.model_name,
                "has_config": bool(adapter.model_config)
            }
        
        if self.default_adapter:
            stats["default_adapter"] = f"{self.default_adapter.provider.value}:{self.default_adapter.model_name}"
        
        return stats

# 便捷函数
def create_client(provider: str = "ollama", 
                 model: str = "llama3.2:latest", 
                 **config) -> UniversalModelClient:
    """创建模型客户端的便捷函数"""
    return UniversalModelClient(provider, model, config)

def quick_generate(prompt: str, 
                  provider: str = "ollama", 
                  model: str = "llama3.2:latest", 
                  **kwargs) -> str:
    """快速生成文本的便捷函数"""
    client = create_client(provider, model)
    config = GenerationConfig(**kwargs)
    response = client.generate(prompt, config=config)
    
    if not response.success:
        raise ModelError(f"生成失败: {response.error}")
    
    return response.content

def quick_chat(messages: List[Dict[str, str]], 
              provider: str = "ollama", 
              model: str = "llama3.2:latest", 
              **kwargs) -> str:
    """快速聊天的便捷函数"""
    client = create_client(provider, model)
    config = GenerationConfig(**kwargs)
    response = client.chat(messages, config=config)
    
    if not response.success:
        raise ModelError(f"聊天失败: {response.error}")
    
    return response.content

async def quick_generate_async(prompt: str, 
                             provider: str = "ollama", 
                             model: str = "llama3.2:latest", 
                             **kwargs) -> str:
    """快速异步生成文本的便捷函数"""
    client = create_client(provider, model)
    config = GenerationConfig(**kwargs)
    response = await client.generate_async(prompt, config=config)
    
    if not response.success:
        raise ModelError(f"异步生成失败: {response.error}")
    
    return response.content

async def quick_chat_async(messages: List[Dict[str, str]], 
                         provider: str = "ollama", 
                         model: str = "llama3.2:latest", 
                         **kwargs) -> str:
    """快速异步聊天的便捷函数"""
    client = create_client(provider, model)
    config = GenerationConfig(**kwargs)
    response = await client.chat_async(messages, config=config)
    
    if not response.success:
        raise ModelError(f"异步聊天失败: {response.error}")
    
    return response.content

# 导出主要类和函数
__all__ = [
    "BaseModelAdapter",
    "UniversalModelClient",
    "create_client",
    "quick_generate",
    "quick_chat",
    "quick_generate_async",
    "quick_chat_async"
]
import os
from typing import Any, Dict, List, Optional
import openai
from .base import BaseModelAdapter
from ..models import GenerationConfig, ModelProvider, ModelResponse, ConnectionStatus
from datetime import datetime


class OpenAIModelAdapter(BaseModelAdapter):
    """OpenAI模型适配器"""
    
    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_name, config)
        
        # 根据提供商设置不同的API配置
        if self.provider == ModelProvider.OPENAI:
            api_key = self.api_config.get("api_key") or os.getenv('OPENAI_API_KEY')
            base_url = self.api_config.get("base_url") or "https://api.openai.com/v1"
        elif self.provider == ModelProvider.DEEPSEEK:
            api_key = self.api_config.get("api_key") or os.getenv('DEEPSEEK_API_KEY')
            base_url = self.api_config.get("base_url") or "https://api.deepseek.com"
        elif self.provider == ModelProvider.VLLM:
            api_key = self.api_config.get("api_key") or os.getenv('VLLM_API_KEY', "")
            base_url = self.api_config.get("base_url") or "http://localhost:8000/v1"
        else:
            api_key = self.api_config.get("api_key", "")
            base_url = self.api_config.get("base_url", "")
        
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    async def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> str:
        """使用OpenAI生成文本"""
        if not config:
            config = GenerationConfig()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")
    
    async def chat(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> str:
        """使用OpenAI进行聊天对话"""
        if not config:
            config = GenerationConfig()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")
    
    def check_connection(self) -> ConnectionStatus:
        """检查连接状态"""
        try:
            import time
            start_time = time.time()
            
            # 尝试列出模型来测试连接
            models = self.client.models.list()
            response_time = time.time() - start_time
            
            model_names = [model.id for model in models.data]
            
            return ConnectionStatus(
                provider=self.provider,
                connected=True,
                status_message="连接正常",
                last_check=datetime.now(),
                models_available=model_names,
                response_time=response_time
            )
        except Exception as e:
            return ConnectionStatus(
                provider=self.provider,
                connected=False,
                status_message=f"连接失败: {str(e)}",
                last_check=datetime.now(),
                error_details=str(e)
            )
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            # 如果无法获取模型列表，返回配置中的模型
            from config.settings import ModelConfig
            provider_config = ModelConfig.MODELS.get(self.provider, {})
            models = provider_config.get("models", [])
            return [model["name"] for model in models]
    
    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> ModelResponse:
        """生成文本"""
        import time
        start_time = time.time()
        
        if not config:
            config = GenerationConfig()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p
            )
            
            response_time = time.time() - start_time
            
            return ModelResponse(
                content=response.choices[0].message.content,
                model=self.model_name,
                provider=self.provider.value,
                success=True,
                response_time=response_time,
                tokens_used=response.usage.total_tokens if response.usage else None,
                tokens_prompt=response.usage.prompt_tokens if response.usage else None
            )
        except Exception as e:
            response_time = time.time() - start_time
            return ModelResponse(
                content="",
                model=self.model_name,
                provider=self.provider.value,
                success=False,
                response_time=response_time,
                error=str(e)
            )
    
    async def generate_async(self, prompt: str, config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步生成文本"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate, prompt, config)
    
    def chat(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> ModelResponse:
        """聊天对话"""
        import time
        start_time = time.time()
        
        if not config:
            config = GenerationConfig()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p
            )
            
            response_time = time.time() - start_time
            
            return ModelResponse(
                content=response.choices[0].message.content,
                model=self.model_name,
                provider=self.provider.value,
                success=True,
                response_time=response_time,
                tokens_used=response.usage.total_tokens if response.usage else None,
                tokens_prompt=response.usage.prompt_tokens if response.usage else None
            )
        except Exception as e:
            response_time = time.time() - start_time
            return ModelResponse(
                content="",
                model=self.model_name,
                provider=self.provider.value,
                success=False,
                response_time=response_time,
                error=str(e)
            )
    
    async def chat_async(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步聊天对话"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.chat, messages, config)
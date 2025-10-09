import os
from typing import Any, Dict, List, Optional
import openai
from core.base_adapter import BaseModelAdapter
from core.models import GenerationConfig, ModelProvider, ModelResponse, ConnectionStatus, ModelInfo
from datetime import datetime


class OpenAIModelAdapter(BaseModelAdapter):
    """OpenAI模型适配器"""
    
    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        # 确保传入的配置覆盖默认provider
        if config and 'provider' in config:
            provider = ModelProvider(config['provider'])
        else:
            provider = ModelProvider.OPENAI
            
        super().__init__(provider, model_name, config)
        
        # 确保环境变量已加载
        from utils.config import load_dotenv
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'utils', '.env')
        load_dotenv(env_path)
        
        # 根据提供商设置不同的API配置
        if self.provider == ModelProvider.OPENAI:
            api_key = self.api_config.get("api_key") or os.getenv('OPENAI_API_KEY')
            base_url = self.api_config.get("base_url") or "https://api.openai.com/v1"
        elif self.provider == ModelProvider.DEEPSEEK:
            api_key = self.api_config.get("api_key") or os.getenv('DEEPSEEK_API_KEY')
            base_url = self.api_config.get("base_url") or os.getenv('DEEPSEEK_BASE_URL') or "https://api.deepseek.com/v1"
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
    
    async def generate_async(self, prompt: str, config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步生成文本"""
        return await self.generate(prompt, config)
    
    async def chat_async(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步聊天对话"""
        return await self.chat(messages, config)
    
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
    
    def get_available_models(self) -> List[ModelInfo]:
        """获取可用的模型列表"""
        try:
            models = self.client.models.list()
            return [
                ModelInfo(
                    name=model.id,
                    display_name=model.id,
                    provider=self.provider,
                    description=f"OpenAI {model.id} model",
                    category="通用对话",
                    context_length=0,
                    parameters={},
                    available=True
                )
                for model in models.data
            ]
        except Exception as e:
            # 如果无法获取模型列表，返回配置中的模型
            from config.settings import ModelConfig
            provider_config = ModelConfig.MODELS.get(self.provider, {})
            models = provider_config.get("models", [])
            return [
                ModelInfo(
                    name=model["name"],
                    display_name=model["display_name"],
                    provider=self.provider,
                    description=model.get("description", ""),
                    category=model.get("category", "通用对话"),
                    context_length=model.get("context_length", 0),
                    parameters=model.get("parameters", {}),
                    available=False
                )
                for model in models
            ]
    
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
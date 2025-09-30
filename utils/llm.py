import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union, AsyncGenerator, Generator
from dataclasses import dataclass, asdict
from enum import Enum
import requests

# 尝试导入可选依赖
try:
    from langchain_core.language_models.llms import LLM
    from langchain_core.callbacks.manager import CallbackManagerForLLMRun
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from utils.config import get_api_config, get_model_config, MODEL_CONFIG

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    """模型提供商枚举"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"
    CHATGLM = "chatglm"
    DEEPSEEK = "deepseek"
    MOONSHOT = "moonshot"

@dataclass
class ModelResponse:
    """模型响应数据类"""
    content: str
    model: str
    provider: str
    success: bool
    response_time: float
    tokens_used: Optional[int] = None
    tokens_prompt: Optional[int] = None
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class GenerationConfig:
    """生成配置数据类"""
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: Optional[int] = None
    max_tokens: int = 4096
    stop_sequences: Optional[List[str]] = None
    stream: bool = False
    system_prompt: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，过滤None值"""
        return {k: v for k, v in asdict(self).items() if v is not None}

class BaseModelAdapter(ABC):
    """模型适配器基类"""
    
    def __init__(self, provider: ModelProvider, model_name: str, config: Optional[Dict[str, Any]] = None):
        self.provider = provider
        self.model_name = model_name
        self.config = config or {}
        self.api_config = get_api_config(provider.value)
        self.model_config = get_model_config(provider.value, model_name)
    
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
    
    def check_availability(self) -> bool:
        """检查模型可用性"""
        return self.api_config is not None

class OllamaAdapter(BaseModelAdapter):
    """Ollama模型适配器"""
    
    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(ModelProvider.OLLAMA, model_name, config)
        if not self.api_config:
            raise ValueError("Ollama API配置未找到")
        
        self.base_url = self.api_config["base_url"]
        self.api_url = f"{self.base_url}/api"
        self.timeout = self.api_config.get("timeout", 60)
    
    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> ModelResponse:
        """生成文本"""
        start_time = time.time()
        
        try:
            # 合并配置
            gen_config = self._merge_config(config)
            
            # 构建请求
            data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": self._build_ollama_options(gen_config)
            }
            
            if gen_config.system_prompt:
                data["system"] = gen_config.system_prompt
            
            # 发送请求
            response = requests.post(
                f"{self.api_url}/generate",
                json=data,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return ModelResponse(
                    content=result.get("response", ""),
                    model=self.model_name,
                    provider=self.provider.value,
                    success=True,
                    response_time=response_time,
                    tokens_used=result.get("eval_count"),
                    tokens_prompt=result.get("prompt_eval_count"),
                    metadata={
                        "eval_duration": result.get("eval_duration"),
                        "total_duration": result.get("total_duration")
                    }
                )
            else:
                return ModelResponse(
                    content="",
                    model=self.model_name,
                    provider=self.provider.value,
                    success=False,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return ModelResponse(
                content="",
                model=self.model_name,
                provider=self.provider.value,
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def generate_async(self, prompt: str, config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步生成文本"""
        # 在实际项目中，这里应该使用 aiohttp 等异步HTTP库
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate, prompt, config)
    
    def chat(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> ModelResponse:
        """聊天对话"""
        start_time = time.time()
        
        try:
            gen_config = self._merge_config(config)
            
            data = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": self._build_ollama_options(gen_config)
            }
            
            response = requests.post(
                f"{self.api_url}/chat",
                json=data,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return ModelResponse(
                    content=result.get("message", {}).get("content", ""),
                    model=self.model_name,
                    provider=self.provider.value,
                    success=True,
                    response_time=response_time,
                    metadata=result
                )
            else:
                return ModelResponse(
                    content="",
                    model=self.model_name,
                    provider=self.provider.value,
                    success=False,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return ModelResponse(
                content="",
                model=self.model_name,
                provider=self.provider.value,
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def chat_async(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步聊天对话"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.chat, messages, config)
    
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
    
    def _build_ollama_options(self, config: GenerationConfig) -> Dict[str, Any]:
        """构建Ollama选项"""
        options = {
            "temperature": config.temperature,
            "top_p": config.top_p,
            "num_predict": config.max_tokens
        }
        
        if config.top_k is not None:
            options["top_k"] = config.top_k
        
        if config.stop_sequences:
            options["stop"] = config.stop_sequences
        
        return options

class OpenAIAdapter(BaseModelAdapter):
    """OpenAI模型适配器"""
    
    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(ModelProvider.OPENAI, model_name, config)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("openai 包未安装，请运行: pip install openai")
        
        if not self.api_config or not self.api_config.get("api_key"):
            raise ValueError("OpenAI API配置或API密钥未找到")
        
        self.client = openai.OpenAI(
            api_key=self.api_config["api_key"],
            base_url=self.api_config.get("base_url")
        )
    
    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> ModelResponse:
        """生成文本"""
        # OpenAI没有直接的completion API，使用chat格式
        messages = [{"role": "user", "content": prompt}]
        if config and config.system_prompt:
            messages.insert(0, {"role": "system", "content": config.system_prompt})
        
        return self.chat(messages, config)
    
    async def generate_async(self, prompt: str, config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步生成文本"""
        messages = [{"role": "user", "content": prompt}]
        if config and config.system_prompt:
            messages.insert(0, {"role": "system", "content": config.system_prompt})
        
        return await self.chat_async(messages, config)
    
    def chat(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> ModelResponse:
        """聊天对话"""
        start_time = time.time()
        
        try:
            gen_config = self._merge_config(config)
            
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": gen_config.temperature,
                "top_p": gen_config.top_p,
                "max_tokens": gen_config.max_tokens,
                "stream": gen_config.stream
            }
            
            if gen_config.stop_sequences:
                kwargs["stop"] = gen_config.stop_sequences
            
            response = self.client.chat.completions.create(**kwargs)
            
            response_time = time.time() - start_time
            
            return ModelResponse(
                content=response.choices[0].message.content,
                model=self.model_name,
                provider=self.provider.value,
                success=True,
                response_time=response_time,
                tokens_used=response.usage.completion_tokens,
                tokens_prompt=response.usage.prompt_tokens,
                metadata={
                    "usage": response.usage.dict(),
                    "finish_reason": response.choices[0].finish_reason
                }
            )
            
        except Exception as e:
            return ModelResponse(
                content="",
                model=self.model_name,
                provider=self.provider.value,
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    async def chat_async(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步聊天对话"""
        # 使用异步客户端
        async_client = openai.AsyncOpenAI(
            api_key=self.api_config["api_key"],
            base_url=self.api_config.get("base_url")
        )
        
        start_time = time.time()
        
        try:
            gen_config = self._merge_config(config)
            
            kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": gen_config.temperature,
                "top_p": gen_config.top_p,
                "max_tokens": gen_config.max_tokens,
                "stream": gen_config.stream
            }
            
            if gen_config.stop_sequences:
                kwargs["stop"] = gen_config.stop_sequences
            
            response = await async_client.chat.completions.create(**kwargs)
            
            response_time = time.time() - start_time
            
            return ModelResponse(
                content=response.choices[0].message.content,
                model=self.model_name,
                provider=self.provider.value,
                success=True,
                response_time=response_time,
                tokens_used=response.usage.completion_tokens,
                tokens_prompt=response.usage.prompt_tokens,
                metadata={
                    "usage": response.usage.dict(),
                    "finish_reason": response.choices[0].finish_reason
                }
            )
            
        except Exception as e:
            return ModelResponse(
                content="",
                model=self.model_name,
                provider=self.provider.value,
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def _merge_config(self, config: Optional[GenerationConfig]) -> GenerationConfig:
        """合并配置"""
        default_params = self.model_config.get("parameters", {}) if self.model_config else {}
        
        if config:
            merged = GenerationConfig(**config.to_dict())
        else:
            merged = GenerationConfig()
        
        for key, value in default_params.items():
            if hasattr(merged, key) and getattr(merged, key) == getattr(GenerationConfig(), key):
                setattr(merged, key, value)
        
        return merged

class UniversalModelClient:
    """通用模型客户端"""
    
    def __init__(self, 
                 provider: Optional[Union[str, ModelProvider]] = None,
                 model_name: Optional[str] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        初始化通用模型客户端
        
        Args:
            provider: 模型提供商
            model_name: 模型名称
            config: 额外配置
        """
        self.config = config or {}
        self.adapters = {}
        
        # 如果指定了默认模型，创建适配器
        if provider and model_name:
            self.default_adapter = self._create_adapter(provider, model_name)
        else:
            self.default_adapter = None
    
    def _create_adapter(self, provider: Union[str, ModelProvider], model_name: str) -> BaseModelAdapter:
        """创建模型适配器"""
        if isinstance(provider, str):
            provider = ModelProvider(provider)
        
        adapter_key = f"{provider.value}:{model_name}"
        
        if adapter_key not in self.adapters:
            if provider == ModelProvider.OLLAMA:
                self.adapters[adapter_key] = OllamaAdapter(model_name, self.config)
            elif provider == ModelProvider.OPENAI:
                self.adapters[adapter_key] = OpenAIAdapter(model_name, self.config)
            # 可以继续添加其他提供商的适配器
            else:
                raise ValueError(f"不支持的提供商: {provider}")
        
        return self.adapters[adapter_key]
    
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
        adapter = self._get_adapter(provider, model_name)
        return adapter.generate(prompt, config)
    
    async def generate_async(self,
                           prompt: str,
                           provider: Optional[Union[str, ModelProvider]] = None,
                           model_name: Optional[str] = None,
                           config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步生成文本"""
        adapter = self._get_adapter(provider, model_name)
        return await adapter.generate_async(prompt, config)
    
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
        adapter = self._get_adapter(provider, model_name)
        return adapter.chat(messages, config)
    
    async def chat_async(self,
                        messages: List[Dict[str, str]],
                        provider: Optional[Union[str, ModelProvider]] = None,
                        model_name: Optional[str] = None,
                        config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步聊天对话"""
        adapter = self._get_adapter(provider, model_name)
        return await adapter.chat_async(messages, config)
    
    def _get_adapter(self, provider: Optional[Union[str, ModelProvider]], model_name: Optional[str]) -> BaseModelAdapter:
        """获取适配器"""
        if provider and model_name:
            return self._create_adapter(provider, model_name)
        elif self.default_adapter:
            return self.default_adapter
        else:
            raise ValueError("未指定模型提供商和模型名称，且没有默认适配器")
    
    def list_available_models(self, provider: Optional[Union[str, ModelProvider]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """列出可用模型"""
        if provider:
            if isinstance(provider, str):
                provider = ModelProvider(provider)
            return {provider.value: MODEL_CONFIG.get(provider.value, {}).get("models", [])}
        else:
            return {p.value: MODEL_CONFIG.get(p.value, {}).get("models", []) for p in ModelProvider}
    
    def check_model_availability(self, provider: Union[str, ModelProvider], model_name: str) -> bool:
        """检查模型可用性"""
        try:
            adapter = self._create_adapter(provider, model_name)
            return adapter.check_availability()
        except Exception:
            return False

# LangChain 集成
if LANGCHAIN_AVAILABLE:
    class UniversalLangChainLLM(LLM):
        """LangChain LLM 适配器"""
        
        client: UniversalModelClient
        provider: str
        model_name: str
        generation_config: GenerationConfig
        
        def __init__(self, client: UniversalModelClient, provider: str, model_name: str, **kwargs):
            super().__init__(**kwargs)
            self.client = client
            self.provider = provider
            self.model_name = model_name
            self.generation_config = GenerationConfig(**kwargs)
        
        @property
        def _llm_type(self) -> str:
            return f"universal-{self.provider}"
        
        def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs) -> str:
            config = GenerationConfig(**{**self.generation_config.to_dict(), **kwargs})
            if stop:
                config.stop_sequences = stop
            
            response = self.client.generate(prompt, self.provider, self.model_name, config)
            
            if not response.success:
                raise ValueError(f"模型调用失败: {response.error}")
            
            return response.content
    
    class UniversalLangChainChatModel(BaseChatModel):
        """LangChain ChatModel 适配器"""
        
        client: UniversalModelClient
        provider: str
        model_name: str
        generation_config: GenerationConfig
        
        def __init__(self, client: UniversalModelClient, provider: str, model_name: str, **kwargs):
            super().__init__(**kwargs)
            self.client = client
            self.provider = provider
            self.model_name = model_name
            self.generation_config = GenerationConfig(**kwargs)
        
        @property
        def _llm_type(self) -> str:
            return f"universal-chat-{self.provider}"
        
        def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs) -> Any:
            # 转换消息格式
            formatted_messages = []
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    formatted_messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    formatted_messages.append({"role": "assistant", "content": msg.content})
                elif isinstance(msg, SystemMessage):
                    formatted_messages.append({"role": "system", "content": msg.content})
            
            config = GenerationConfig(**{**self.generation_config.to_dict(), **kwargs})
            if stop:
                config.stop_sequences = stop
            
            response = self.client.chat(formatted_messages, self.provider, self.model_name, config)
            
            if not response.success:
                raise ValueError(f"模型调用失败: {response.error}")
            
            # 这里需要返回适当的LangChain格式，简化示例
            return response.content

# 便捷函数
def create_client(provider: str = "ollama", model: str = "llama3.2:latest", **config) -> UniversalModelClient:
    """创建模型客户端的便捷函数"""
    return UniversalModelClient(provider, model, config)

def quick_generate(prompt: str, provider: str = "ollama", model: str = "llama3.2:latest", **kwargs) -> str:
    """快速生成文本的便捷函数"""
    client = create_client(provider, model)
    config = GenerationConfig(**kwargs)
    response = client.generate(prompt, config=config)
    
    if not response.success:
        raise RuntimeError(f"生成失败: {response.error}")
    
    return response.content

def quick_chat(messages: List[Dict[str, str]], provider: str = "ollama", model: str = "llama3.2:latest", **kwargs) -> str:
    """快速聊天的便捷函数"""
    client = create_client(provider, model)
    config = GenerationConfig(**kwargs)
    response = client.chat(messages, config=config)
    
    if not response.success:
        raise RuntimeError(f"聊天失败: {response.error}")
    
    return response.content
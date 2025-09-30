"""
Ollama模型适配器
"""

import asyncio
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

from core.client import BaseModelAdapter
from core.models import (
    ModelProvider, GenerationConfig, ModelResponse, ModelInfo, ConnectionStatus
)
from config.settings import ConfigValidator, ModelConfig
from utils.exceptions import ConnectionError, ModelError, TimeoutError
from utils.logger import get_logger, log_api_call

logger = get_logger(__name__)

class OllamaAdapter(BaseModelAdapter):
    """Ollama模型适配器"""
    
    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(ModelProvider.OLLAMA, model_name, config)
        
        if not self.api_config:
            raise ConnectionError("Ollama API配置未找到")
        
        self.base_url = self.api_config["base_url"]
        self.api_url = f"{self.base_url}/api"
        self.timeout = self.api_config.get("timeout", 60)
        
        logger.info(f"Ollama适配器初始化: {self.base_url}, 模型: {model_name}")
    
    def check_connection(self) -> ConnectionStatus:
        """检查Ollama连接状态"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/tags", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                
                return ConnectionStatus(
                    provider=self.provider,
                    connected=True,
                    status_message="连接正常",
                    last_check=datetime.now(),
                    models_available=models,
                    response_time=response_time
                )
            else:
                return ConnectionStatus(
                    provider=self.provider,
                    connected=False,
                    status_message=f"HTTP {response.status_code}",
                    last_check=datetime.now(),
                    error_details=f"服务响应异常: {response.status_code}",
                    response_time=response_time
                )
                
        except requests.exceptions.ConnectionError:
            return ConnectionStatus(
                provider=self.provider,
                connected=False,
                status_message="连接失败",
                last_check=datetime.now(),
                error_details="无法连接到Ollama服务，请确保服务已启动"
            )
        except requests.exceptions.Timeout:
            return ConnectionStatus(
                provider=self.provider,
                connected=False,
                status_message="连接超时",
                last_check=datetime.now(),
                error_details="连接超时，请检查网络状态"
            )
        except Exception as e:
            return ConnectionStatus(
                provider=self.provider,
                connected=False,
                status_message="未知错误",
                last_check=datetime.now(),
                error_details=f"连接检查失败: {str(e)}"
            )
    
    def get_available_models(self) -> List[ModelInfo]:
        """获取可用模型列表"""
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=10)
            if response.status_code != 200:
                logger.error(f"获取模型列表失败: HTTP {response.status_code}")
                return []
            
            data = response.json()
            ollama_models = data.get("models", [])
            
            # 合并配置中的模型信息
            enhanced_models = []
            config_models = ModelConfig.MODELS[ModelProvider.OLLAMA]["models"]
            
            for ollama_model in ollama_models:
                model_name = ollama_model["name"]
                
                # 查找配置中的对应模型
                config_model = None
                for config in config_models:
                    if (config["name"] == model_name or 
                        model_name.startswith(config["name"].split(":")[0])):
                        config_model = config
                        break
                
                model_info = ModelInfo(
                    name=model_name,
                    display_name=config_model["display_name"] if config_model else model_name,
                    provider=self.provider,
                    description=config_model["description"] if config_model else "本地模型",
                    category=config_model["category"] if config_model else "通用对话",
                    context_length=config_model.get("context_length", 4096) if config_model else 4096,
                    parameters=config_model["parameters"] if config_model else self._get_default_parameters(),
                    available=True,
                    size=ollama_model.get("size", 0),
                    modified_at=ollama_model.get("modified_at", "")
                )
                
                enhanced_models.append(model_info)
            
            logger.info(f"获取到 {len(enhanced_models)} 个可用模型")
            return enhanced_models
            
        except Exception as e:
            logger.error(f"获取模型列表异常: {str(e)}")
            return []
    
    @log_api_call("ollama", "model_name")
    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> ModelResponse:
        """生成文本"""
        start_time = time.time()
        
        try:
            # 合并配置
            gen_config = self._merge_config(config)
            
            # 构建请求数据
            data = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": self._build_ollama_options(gen_config)
            }
            
            if gen_config.system_prompt:
                data["system"] = gen_config.system_prompt
            
            # 请求数据日志已移除
            
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
                        "prompt_eval_duration": result.get("prompt_eval_duration"),
                        "total_duration": result.get("total_duration"),
                        "load_duration": result.get("load_duration")
                    }
                )
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json().get("error", response.text)
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text}"
                
                return ModelResponse(
                    content="",
                    model=self.model_name,
                    provider=self.provider.value,
                    success=False,
                    response_time=response_time,
                    error=error_msg
                )
                
        except requests.exceptions.Timeout:
            return ModelResponse(
                content="",
                model=self.model_name,
                provider=self.provider.value,
                success=False,
                response_time=self.timeout,
                error=f"请求超时 ({self.timeout}s)，请检查模型是否正在运行"
            )
        except requests.exceptions.ConnectionError:
            return ModelResponse(
                content="",
                model=self.model_name,
                provider=self.provider.value,
                success=False,
                response_time=time.time() - start_time,
                error="无法连接到Ollama服务，请确保服务已启动"
            )
        except Exception as e:
            return ModelResponse(
                content="",
                model=self.model_name,
                provider=self.provider.value,
                success=False,
                response_time=time.time() - start_time,
                error=f"请求失败: {str(e)}"
            )
    
    async def generate_async(self, prompt: str, config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步生成文本"""
        # 在实际项目中，这里应该使用aiohttp等异步HTTP库
        # 这里为简单起见，使用run_in_executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate, prompt, config)
    
    @log_api_call("ollama", "model_name")
    def chat(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> ModelResponse:
        """聊天对话"""
        start_time = time.time()
        
        try:
            gen_config = self._merge_config(config)
            
            # 构建请求数据
            data = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": self._build_ollama_options(gen_config)
            }
            
            # 聊天请求数据日志已移除
            
            # 发送请求
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
                    tokens_used=result.get("eval_count"),
                    tokens_prompt=result.get("prompt_eval_count"),
                    metadata={
                        "eval_duration": result.get("eval_duration"),
                        "prompt_eval_duration": result.get("prompt_eval_duration"),
                        "total_duration": result.get("total_duration"),
                        "message": result.get("message", {})
                    }
                )
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json().get("error", response.text)
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text}"
                
                return ModelResponse(
                    content="",
                    model=self.model_name,
                    provider=self.provider.value,
                    success=False,
                    response_time=response_time,
                    error=error_msg
                )
                
        except requests.exceptions.Timeout:
            return ModelResponse(
                content="",
                model=self.model_name,
                provider=self.provider.value,
                success=False,
                response_time=self.timeout,
                error=f"聊天请求超时 ({self.timeout}s)"
            )
        except requests.exceptions.ConnectionError:
            return ModelResponse(
                content="",
                model=self.model_name,
                provider=self.provider.value,
                success=False,
                response_time=time.time() - start_time,
                error="无法连接到Ollama服务"
            )
        except Exception as e:
            return ModelResponse(
                content="",
                model=self.model_name,
                provider=self.provider.value,
                success=False,
                response_time=time.time() - start_time,
                error=f"聊天请求失败: {str(e)}"
            )
    
    async def chat_async(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> ModelResponse:
        """异步聊天对话"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.chat, messages, config)
    
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
        
        # 添加Ollama特有的参数
        if hasattr(config, 'repeat_penalty'):
            options["repeat_penalty"] = getattr(config, 'repeat_penalty', 1.1)
        
        return options
    
    def _get_default_parameters(self) -> Dict[str, Any]:
        """获取默认参数"""
        return {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "max_tokens": 4096
        }
    
    def get_model_info(self, model_name: Optional[str] = None) -> Optional[ModelInfo]:
        """获取特定模型的详细信息"""
        target_model = model_name or self.model_name
        
        try:
            # 首先从配置中获取基础信息
            config_model = ConfigValidator.get_model_config(self.provider, target_model)
            
            # 从Ollama API获取运行时信息
            response = requests.post(
                f"{self.api_url}/show",
                json={"name": target_model},
                timeout=10
            )
            
            if response.status_code == 200:
                api_info = response.json()
                
                return ModelInfo(
                    name=target_model,
                    display_name=config_model["display_name"] if config_model else target_model,
                    provider=self.provider,
                    description=config_model["description"] if config_model else "本地模型",
                    category=config_model["category"] if config_model else "通用对话",
                    context_length=config_model.get("context_length", 4096) if config_model else 4096,
                    parameters=config_model["parameters"] if config_model else self._get_default_parameters(),
                    available=True
                )
            else:
                return ModelInfo(
                    name=target_model,
                    display_name=config_model["display_name"] if config_model else target_model,
                    provider=self.provider,
                    description=config_model["description"] if config_model else "本地模型",
                    category=config_model["category"] if config_model else "通用对话",
                    context_length=config_model.get("context_length", 4096) if config_model else 4096,
                    parameters=config_model["parameters"] if config_model else self._get_default_parameters(),
                    available=False
                ) if config_model else None
                
        except Exception as e:
            logger.error(f"获取模型信息失败: {str(e)}")
            return None

# 导出适配器类
__all__ = ["OllamaAdapter"]
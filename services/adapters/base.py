from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..models import GenerationConfig


class BaseModelAdapter(ABC):
    """基础模型适配器抽象类"""
    
    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        self.model_name = model_name
        self.config = config or {}
    
    @abstractmethod
    async def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> str:
        """生成文本"""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], config: Optional[GenerationConfig] = None) -> str:
        """聊天对话"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        pass
    
    def validate_config(self, config: GenerationConfig) -> bool:
        """验证配置参数"""
        if config.temperature < 0 or config.temperature > 2:
            return False
        if config.max_tokens <= 0:
            return False
        if config.top_p < 0 or config.top_p > 1:
            return False
        return True
"""
核心数据模型
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
import json

class ModelProvider(Enum):
    """模型提供商枚举"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"
    CHATGLM = "chatglm"
    DEEPSEEK = "deepseek"
    MOONSHOT = "moonshot"
    ERNIE = "ernie"

class OptimizationType(Enum):
    """优化类型枚举"""
    GENERAL = "general"
    STRUCTURED = "structured"
    ROLE_BASED = "role_based"
    TASK_ORIENTED = "task_oriented"
    CREATIVE = "creative"
    LOGICAL = "logical"

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

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
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，过滤None值"""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GenerationConfig':
        """从字典创建配置"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})

@dataclass
class ModelInfo:
    """模型信息数据类"""
    name: str
    display_name: str
    provider: ModelProvider
    description: str = ""
    category: str = "通用对话"
    context_length: int = 4096
    parameters: Dict[str, Any] = field(default_factory=dict)
    available: bool = True
    size: Optional[int] = None
    modified_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        result["provider"] = self.provider.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelInfo':
        """从字典创建模型信息"""
        if isinstance(data.get("provider"), str):
            data["provider"] = ModelProvider(data["provider"])
        return cls(**data)

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
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelResponse':
        """从字典创建响应"""
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)

@dataclass
class OptimizationRequest:
    """优化请求数据类"""
    original_prompt: str
    optimization_type: OptimizationType
    model_provider: ModelProvider
    model_name: str
    generation_config: Optional[GenerationConfig] = None
    custom_instructions: Optional[str] = None
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "original_prompt": self.original_prompt,
            "optimization_type": self.optimization_type.value,
            "model_provider": self.model_provider.value,
            "model_name": self.model_name,
            "custom_instructions": self.custom_instructions,
            "user_id": self.user_id
        }
        
        if self.generation_config:
            result["generation_config"] = self.generation_config.to_dict()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptimizationRequest':
        """从字典创建请求"""
        if isinstance(data.get("optimization_type"), str):
            data["optimization_type"] = OptimizationType(data["optimization_type"])
        if isinstance(data.get("model_provider"), str):
            data["model_provider"] = ModelProvider(data["model_provider"])
        if data.get("generation_config"):
            data["generation_config"] = GenerationConfig.from_dict(data["generation_config"])
        
        return cls(**data)

@dataclass
class OptimizationResult:
    """优化结果数据类"""
    request: OptimizationRequest
    optimized_prompt: str
    suggestions: List[str]
    response: ModelResponse
    metrics: Dict[str, float] = field(default_factory=dict)
    task_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "request": self.request.to_dict(),
            "optimized_prompt": self.optimized_prompt,
            "suggestions": self.suggestions,
            "response": self.response.to_dict(),
            "metrics": self.metrics,
            "task_id": self.task_id,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OptimizationResult':
        """从字典创建结果"""
        data["request"] = OptimizationRequest.from_dict(data["request"])
        data["response"] = ModelResponse.from_dict(data["response"])
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        
        return cls(**data)

@dataclass
class TestRequest:
    """测试请求数据类"""
    original_prompt: str
    optimized_prompt: str
    test_content: str
    model_provider: ModelProvider
    model_name: str
    generation_config: Optional[GenerationConfig] = None
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "original_prompt": self.original_prompt,
            "optimized_prompt": self.optimized_prompt,
            "test_content": self.test_content,
            "model_provider": self.model_provider.value,
            "model_name": self.model_name,
            "user_id": self.user_id
        }
        
        if self.generation_config:
            result["generation_config"] = self.generation_config.to_dict()
        
        return result

@dataclass
class TestResult:
    """测试结果数据类"""
    request: TestRequest
    original_response: ModelResponse
    optimized_response: ModelResponse
    comparison_metrics: Dict[str, Dict[str, float]]
    improvement_summary: Dict[str, float]
    task_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "request": self.request.to_dict(),
            "original_response": self.original_response.to_dict(),
            "optimized_response": self.optimized_response.to_dict(),
            "comparison_metrics": self.comparison_metrics,
            "improvement_summary": self.improvement_summary,
            "task_id": self.task_id,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        """从字典创建结果"""
        data["request"] = TestRequest.from_dict(data["request"])
        data["original_response"] = ModelResponse.from_dict(data["original_response"])
        data["optimized_response"] = ModelResponse.from_dict(data["optimized_response"])
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        
        return cls(**data)

@dataclass
class Task:
    """任务数据类"""
    task_id: str
    task_type: str  # 'optimization' 或 'testing'
    status: TaskStatus
    progress: float = 0.0
    message: str = ""
    result: Optional[Union[OptimizationResult, TestResult]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        if self.result:
            result["result"] = self.result.to_dict()
        
        return result
    
    def update_status(self, status: TaskStatus, message: str = "", progress: float = None):
        """更新任务状态"""
        self.status = status
        self.message = message
        if progress is not None:
            self.progress = progress
        self.updated_at = datetime.now()

@dataclass
class UserSession:
    """用户会话数据类"""
    session_id: str
    user_id: Optional[str] = None
    optimization_history: List[OptimizationResult] = field(default_factory=list)
    test_history: List[TestResult] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    def add_optimization(self, result: OptimizationResult):
        """添加优化结果"""
        self.optimization_history.append(result)
        self.last_active = datetime.now()
        
        # 限制历史记录数量
        if len(self.optimization_history) > 50:
            self.optimization_history = self.optimization_history[-50:]
    
    def add_test(self, result: TestResult):
        """添加测试结果"""
        self.test_history.append(result)
        self.last_active = datetime.now()
        
        # 限制历史记录数量
        if len(self.test_history) > 50:
            self.test_history = self.test_history[-50:]
    
    def get_recent_optimizations(self, limit: int = 10) -> List[OptimizationResult]:
        """获取最近的优化记录"""
        return sorted(self.optimization_history, 
                     key=lambda x: x.created_at, reverse=True)[:limit]
    
    def get_recent_tests(self, limit: int = 10) -> List[TestResult]:
        """获取最近的测试记录"""
        return sorted(self.test_history, 
                     key=lambda x: x.created_at, reverse=True)[:limit]

@dataclass
class ConnectionStatus:
    """连接状态数据类"""
    provider: ModelProvider
    connected: bool
    status_message: str
    last_check: datetime
    models_available: List[str] = field(default_factory=list)
    error_details: Optional[str] = None
    response_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "provider": self.provider.value,
            "connected": self.connected,
            "status_message": self.status_message,
            "last_check": self.last_check.isoformat(),
            "models_available": self.models_available,
            "error_details": self.error_details,
            "response_time": self.response_time
        }

@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    accuracy: float = 0.0
    relevance: float = 0.0
    completeness: float = 0.0
    clarity: float = 0.0
    creativity: float = 0.0
    coherence: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'PerformanceMetrics':
        """从字典创建指标"""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})
    
    def average(self) -> float:
        """计算平均分"""
        metrics = [self.accuracy, self.relevance, self.completeness, 
                  self.clarity, self.creativity, self.coherence]
        return sum(metrics) / len(metrics)

# 工具函数
def create_task_id() -> str:
    """创建任务ID"""
    import uuid
    return str(uuid.uuid4())

def serialize_dataclass(obj: Any) -> Dict[str, Any]:
    """序列化数据类"""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return {k: serialize_dataclass(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_dataclass(item) for item in obj]
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

def deserialize_dataclass(data: Dict[str, Any], target_class: type) -> Any:
    """反序列化数据类"""
    if hasattr(target_class, 'from_dict'):
        return target_class.from_dict(data)
    else:
        return target_class(**data)

# 导出所有数据类
__all__ = [
    "ModelProvider",
    "OptimizationType", 
    "TaskStatus",
    "GenerationConfig",
    "ModelInfo",
    "ModelResponse",
    "OptimizationRequest",
    "OptimizationResult",
    "TestRequest", 
    "TestResult",
    "Task",
    "UserSession",
    "ConnectionStatus",
    "PerformanceMetrics",
    "create_task_id",
    "serialize_dataclass",
    "deserialize_dataclass"
]
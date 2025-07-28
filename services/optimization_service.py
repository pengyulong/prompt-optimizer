import time
import random
from typing import Dict, Any

class OptimizationService:
    """提示词优化服务"""
    
    def __init__(self):
        self.optimization_strategies = {
            "通用优化": self._general_optimization,
            "结构化优化": self._structured_optimization,
            "角色导向优化": self._role_based_optimization,
            "任务导向优化": self._task_oriented_optimization,
        }
    
    def optimize_prompt(self, original_prompt: str, model: str, optimization_type: str) -> Dict[str, Any]:
        """
        优化提示词
        
        Args:
            original_prompt: 原始提示词
            model: 使用的模型
            optimization_type: 优化类型
            
        Returns:
            优化结果字典
        """
        # 模拟API调用延迟
        time.sleep(1)
        
        # 根据优化类型选择策略
        optimization_strategy = self.optimization_strategies.get(
            optimization_type, 
            self._general_optimization
        )
        
        # 执行优化
        optimized_prompt = optimization_strategy(original_prompt, model)
        
        # 生成优化建议
        suggestions = self._generate_suggestions(original_prompt, optimized_prompt, optimization_type)
        
        return {
            "optimized_prompt": optimized_prompt,
            "suggestions": suggestions,
            "optimization_type": optimization_type,
            "model_used": model
        }
    
    def _general_optimization(self, prompt: str, model: str) -> str:
        """通用优化策略"""
        optimization_rules = [
            "请作为一个专业的AI助手",
            "请按照以下步骤思考",
            "请提供详细和准确的回答",
            "请确保回答的逻辑性和条理性"
        ]
        
        # 简单的优化逻辑
        optimized = f"{random.choice(optimization_rules)}:\n\n{prompt}\n\n请注意:\n- 保持回答的准确性\n- 提供具体的例子或解释\n- 如果不确定，请说明"
        
        return optimized
    
    def _structured_optimization(self, prompt: str, model: str) -> str:
        """结构化优化策略"""
        structured_template = f"""
## 任务描述
{prompt}

## 要求
1. 请按照逻辑顺序组织回答
2. 使用清晰的段落结构
3. 提供具体的示例说明
4. 总结关键要点

## 输出格式
请按照以下格式回答:
- 概述: [简要说明]
- 详细内容: [具体展开]
- 示例: [相关例子]
- 总结: [关键要点]
"""
        return structured_template.strip()
    
    def _role_based_optimization(self, prompt: str, model: str) -> str:
        """角色导向优化策略"""
        role_template = f"""
请以专业领域专家的身份回答以下问题:

**专家角色设定:**
- 你是该领域的资深专家
- 具有丰富的实践经验
- 能够提供权威且实用的建议

**任务:**
{prompt}

**回答要求:**
- 基于专业知识和经验
- 提供实用的建议和解决方案
- 举例说明关键概念
- 避免过于理论化的表述
"""
        return role_template.strip()
    
    def _task_oriented_optimization(self, prompt: str, model: str) -> str:
        """任务导向优化策略"""
        task_template = f"""
**目标任务:** {prompt}

**执行步骤:**
1. 理解任务需求
2. 分析关键要素
3. 制定解决方案
4. 提供具体实施建议

**输出要求:**
- 直接针对任务目标
- 提供可操作的步骤
- 包含必要的注意事项
- 预期结果说明

请按照上述框架完成任务。
"""
        return task_template.strip()
    
    def _generate_suggestions(self, original: str, optimized: str, optimization_type: str) -> list:
        """生成优化建议"""
        suggestions = [
            f"采用了{optimization_type}策略",
            "增加了结构化的提示格式",
            "明确了任务要求和输出格式",
            "提高了提示词的清晰度和准确性"
        ]
        
        # 根据原始提示词长度给出建议
        if len(original) < 50:
            suggestions.append("原始提示词较短，已增加更详细的指导")
        
        if "例子" not in original and "示例" not in original:
            suggestions.append("建议在实际使用中添加具体示例")
        
        return suggestions
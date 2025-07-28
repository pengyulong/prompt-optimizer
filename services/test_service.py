import time
import random
from typing import Dict, Any

class TestService:
    """提示词测试服务"""
    
    def __init__(self):
        pass
    
    def compare_prompts(self, original_prompt: str, optimized_prompt: str, 
                       test_content: str, model: str) -> Dict[str, Any]:
        """
        对比两个提示词的效果
        
        Args:
            original_prompt: 原始提示词
            optimized_prompt: 优化后的提示词
            test_content: 测试内容
            model: 使用的模型
            
        Returns:
            对比测试结果
        """
        # 模拟API调用
        original_result = self._simulate_model_response(original_prompt, test_content, model)
        optimized_result = self._simulate_model_response(optimized_prompt, test_content, model)
        
        # 计算性能指标
        metrics = self._calculate_metrics(original_result, optimized_result)
        
        return {
            "original_result": original_result["content"],
            "optimized_result": optimized_result["content"],
            "metrics": metrics,
            "model_used": model
        }
    
    def _simulate_model_response(self, prompt: str, content: str, model: str) -> Dict[str, Any]:
        """模拟模型响应"""
        # 模拟不同的响应时间
        response_time = random.uniform(0.5, 3.0)
        time.sleep(min(response_time, 1.0))  # 实际演示中缩短等待时间
        
        # 模拟响应内容生成
        if "专家" in prompt or "专业" in prompt:
            response_content = f"作为专业领域的专家，针对您的问题'{content}'，我提供以下详细分析：\n\n"
            response_content += self._generate_expert_response(content)
        elif "步骤" in prompt or "格式" in prompt:
            response_content = f"按照结构化格式回答'{content}'：\n\n"
            response_content += self._generate_structured_response(content)
        else:
            response_content = f"关于'{content}'的回答：\n\n"
            response_content += self._generate_basic_response(content)
        
        # 计算质量分数（模拟）
        quality_score = self._calculate_quality_score(prompt, content, response_content)
        
        return {
            "content": response_content,
            "response_time": response_time,
            "quality_score": quality_score,
            "word_count": len(response_content)
        }
    
    def _generate_expert_response(self, content: str) -> str:
        """生成专家风格的回答"""
        return f"""
**专业分析:**
基于我在相关领域的经验，{content}涉及以下几个核心要点：

1. **理论基础**: 从理论角度来看，这个问题需要考虑...
2. **实践应用**: 在实际应用中，我们通常采用...
3. **最佳实践**: 根据行业标准和最佳实践...
4. **注意事项**: 需要特别注意的是...

**总结建议:**
综合以上分析，我建议采取以下措施...
        """.strip()
    
    def _generate_structured_response(self, content: str) -> str:
        """生成结构化回答"""
        return f"""
## 概述
{content}是一个需要系统性分析的问题。

## 详细分析
### 主要方面
- 方面一：相关的基础概念和定义
- 方面二：实际应用和操作方法
- 方面三：可能遇到的挑战和解决方案

### 具体建议
1. 首先，需要明确目标和需求
2. 其次，制定详细的实施计划
3. 最后，建立监控和评估机制

## 示例说明
以实际案例为例，展示如何应用相关方法...

## 关键要点
- 要点一：注重系统性思考
- 要点二：关注实践可行性
- 要点三：建立反馈机制
        """.strip()
    
    def _generate_basic_response(self, content: str) -> str:
        """生成基础回答"""
        responses = [
            f"根据您提到的{content}，这确实是一个值得关注的问题。一般来说，我们可以从几个角度来考虑这个问题...",
            f"关于{content}，这涉及多个方面的考虑。让我为您详细解释一下...",
            f"您提出的{content}问题很有价值。从经验来看，通常可以通过以下方式来处理..."
        ]
        return random.choice(responses)
    
    def _calculate_quality_score(self, prompt: str, content: str, response: str) -> Dict[str, float]:
        """计算回答质量分数（模拟）"""
        base_score = random.uniform(7.0, 9.5)
        
        # 根据提示词特征调整分数
        if "专家" in prompt:
            base_score += 0.5
        if "步骤" in prompt or "格式" in prompt:
            base_score += 0.3
        if len(response) > 200:
            base_score += 0.2
        
        return {
            "accuracy": min(base_score, 10.0),
            "relevance": min(base_score + random.uniform(-0.5, 0.5), 10.0),
            "completeness": min(base_score + random.uniform(-0.3, 0.7), 10.0)
        }
    
    def _calculate_metrics(self, original_result: Dict, optimized_result: Dict) -> Dict[str, float]:
        """计算性能对比指标"""
        original_quality = original_result["quality_score"]
        optimized_quality = optimized_result["quality_score"]
        
        return {
            "original_time": original_result["response_time"],
            "optimized_time": optimized_result["response_time"],
            "time_improvement": optimized_result["response_time"] - original_result["response_time"],
            
            "original_accuracy": original_quality["accuracy"],
            "optimized_accuracy": optimized_quality["accuracy"],
            "accuracy_improvement": optimized_quality["accuracy"] - original_quality["accuracy"],
            
            "original_relevance": original_quality["relevance"],
            "optimized_relevance": optimized_quality["relevance"],
            "relevance_improvement": optimized_quality["relevance"] - original_quality["relevance"],
            
            "original_completeness": original_quality["completeness"],
            "optimized_completeness": optimized_quality["completeness"],
            "completeness_improvement": optimized_quality["completeness"] - original_quality["completeness"]
        }
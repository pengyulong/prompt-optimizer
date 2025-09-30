"""
提示词优化服务 - 使用模板管理器
"""

from typing import Dict, Any, List
import time
from datetime import datetime

from core.models import (
    OptimizationRequest, OptimizationResult, OptimizationType, 
    ModelResponse, GenerationConfig
)
from core.client import UniversalModelClient
from templates.template_manager import template_manager, create_template_context
from utils.logger import get_logger, api_logger
from utils.exceptions import ModelError, ValidationError, TemplateError

logger = get_logger(__name__)


class OptimizationService:
    """提示词优化服务"""
    
    def __init__(self):
        self.client = UniversalModelClient()
        self.template_manager = template_manager
        
    def optimize_prompt(self, request: OptimizationRequest) -> OptimizationResult:
        """
        优化提示词
        
        Args:
            request: 优化请求
            
        Returns:
            优化结果
        """
        try:
            # 验证请求
            self._validate_request(request)
            
            # 记录API调用
            api_logger.log_request(
                provider=request.model_provider.value,
                model=request.model_name,
                prompt_length=len(request.original_prompt)
            )
            
            # 创建模板上下文
            context = create_template_context(
                original_prompt=request.original_prompt,
                custom_instructions=request.custom_instructions
            )
            
            # 获取优化提示词模板
            optimization_prompt = self.template_manager.get_optimization_template(
                optimization_type=request.optimization_type.value,
                context=context
            )
            
            # 优化提示词生成完成
            
            # 调用模型进行优化
            start_time = time.time()
            
            response = self.client.generate(
                prompt=optimization_prompt,
                provider=request.model_provider,
                model_name=request.model_name,
                config=request.generation_config
            )
            
            # 记录API响应
            api_logger.log_response(
                provider=request.model_provider.value,
                model=request.model_name,
                success=response.success,
                response_time=response.response_time,
                tokens_used=response.tokens_used
            )
            
            if not response.success:
                raise ModelError(f"模型调用失败: {response.error}")
            
            # 处理优化结果
            optimized_prompt = self._extract_optimized_prompt(response.content)
            suggestions = self._generate_suggestions(
                request.original_prompt,
                optimized_prompt,
                request.optimization_type
            )
            
            # 计算性能指标
            metrics = self._calculate_metrics(
                original=request.original_prompt,
                optimized=optimized_prompt,
                optimization_type=request.optimization_type
            )
            
            # 创建结果对象
            result = OptimizationResult(
                request=request,
                optimized_prompt=optimized_prompt,
                suggestions=suggestions,
                response=response,
                metrics=metrics,
                template_used=f"optimization/{request.optimization_type.value}.md",
                created_at=datetime.now()
            )
            
            logger.info(f"提示词优化完成: {request.optimization_type.value}")
            return result
            
        except TemplateError as e:
            logger.error(f"模板处理失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"提示词优化失败: {str(e)}")
            
            # 记录错误
            api_logger.log_error(
                provider=request.model_provider.value,
                model=request.model_name,
                error=str(e)
            )
            
            # 返回失败结果
            error_response = ModelResponse(
                content="",
                model=request.model_name,
                provider=request.model_provider.value,
                success=False,
                response_time=0.0,
                error=str(e)
            )
            
            return OptimizationResult(
                request=request,
                optimized_prompt="",
                suggestions=[],
                response=error_response,
                metrics={},
                template_used="",
                created_at=datetime.now()
            )
    
    def evaluate_optimization(self, 
                            original_prompt: str,
                            optimized_prompt: str,
                            evaluation_type: str = "comparison") -> str:
        """
        评估优化效果
        
        Args:
            original_prompt: 原始提示词
            optimized_prompt: 优化后提示词
            evaluation_type: 评估类型
            
        Returns:
            评估提示词
        """
        try:
            context = create_template_context(
                original_prompt=original_prompt,
                optimized_prompt=optimized_prompt
            )
            
            evaluation_prompt = self.template_manager.get_evaluation_template(
                evaluation_type=evaluation_type,
                context=context
            )
            
            logger.info(f"评估提示词生成完成: {evaluation_type}")
            return evaluation_prompt
            
        except Exception as e:
            logger.error(f"生成评估提示词失败: {str(e)}")
            raise TemplateError(f"生成评估提示词失败: {str(e)}")
    
    def create_test_prompt(self,
                          prompt_to_test: str,
                          test_content: str,
                          testing_type: str = "simple") -> str:
        """
        创建测试提示词
        
        Args:
            prompt_to_test: 要测试的提示词
            test_content: 测试内容
            testing_type: 测试类型
            
        Returns:
            测试提示词
        """
        try:
            context = create_template_context(
                original_prompt=prompt_to_test,
                test_content=test_content
            )
            
            test_prompt = self.template_manager.get_testing_template(
                testing_type=testing_type,
                context=context
            )
            
            logger.info(f"测试提示词生成完成: {testing_type}")
            return test_prompt
            
        except Exception as e:
            logger.error(f"生成测试提示词失败: {str(e)}")
            raise TemplateError(f"生成测试提示词失败: {str(e)}")
    
    def get_role_suggestions(self, content_analysis: str) -> Dict[str, Any]:
        """
        获取角色建议
        
        Args:
            content_analysis: 内容分析结果
            
        Returns:
            角色建议
        """
        # 简单的内容类型检测
        content_type = self._detect_content_type(content_analysis)
        return self.template_manager.get_role_suggestions(content_type)
    
    def _detect_content_type(self, content: str) -> str:
        """检测内容类型"""
        content_lower = content.lower()
        
        code_keywords = ["代码", "编程", "算法", "函数", "code", "programming"]
        writing_keywords = ["写作", "文章", "文案", "创作", "writing", "article"]
        analysis_keywords = ["分析", "数据", "研究", "评估", "analysis", "research"]
        
        if any(keyword in content_lower for keyword in code_keywords):
            return "code"
        elif any(keyword in content_lower for keyword in writing_keywords):
            return "writing"
        elif any(keyword in content_lower for keyword in analysis_keywords):
            return "analysis"
        else:
            return "general"
    
    def get_available_optimization_types(self) -> List[Dict[str, Any]]:
        """获取可用的优化类型"""
        templates = self.template_manager.get_available_templates()
        return templates.get("optimization", [])
    
    def get_available_evaluation_types(self) -> List[Dict[str, Any]]:
        """获取可用的评估类型"""
        templates = self.template_manager.get_available_templates()
        return templates.get("evaluation", [])
    
    def get_available_testing_types(self) -> List[Dict[str, Any]]:
        """获取可用的测试类型"""
        templates = self.template_manager.get_available_templates()
        return templates.get("testing", [])
    
    def _validate_request(self, request: OptimizationRequest):
        """验证优化请求"""
        if not request.original_prompt.strip():
            raise ValidationError("原始提示词不能为空")
        
        if len(request.original_prompt) > 10000:
            raise ValidationError("提示词长度超过限制")
        
        if not request.model_name:
            raise ValidationError("必须指定模型名称")
        
        # 验证模板是否存在
        template_path = f"optimization/{request.optimization_type.value}.md"
        if not self.template_manager.validate_template(template_path):
            raise TemplateError(f"优化模板不存在: {template_path}")
    
    def _extract_optimized_prompt(self, response_content: str) -> str:
        """从响应中提取优化后的提示词"""
        content = response_content.strip()
        
        # 查找常见的分隔符
        separators = [
            "优化后的提示词：",
            "优化后：",
            "Optimized prompt:",
            "优化结果：",
            "改进后：",
            "---"
        ]
        
        for sep in separators:
            if sep in content:
                parts = content.split(sep, 1)
                if len(parts) > 1:
                    extracted = parts[1].strip()
                    # 移除可能的代码块标记
                    if extracted.startswith("```") and extracted.endswith("```"):
                        lines = extracted.split('\n')
                        if len(lines) > 2:
                            extracted = '\n'.join(lines[1:-1])
                    # 移除引号
                    if extracted.startswith('"') and extracted.endswith('"'):
                        extracted = extracted[1:-1]
                    elif extracted.startswith("'") and extracted.endswith("'"):
                        extracted = extracted[1:-1]
                    return extracted
        
        return content
    
    def _generate_suggestions(self, original: str, optimized: str, 
                             optimization_type: OptimizationType) -> List[str]:
        """生成优化建议"""
        suggestions = []
        
        # 基于优化类型的建议
        type_suggestions = {
            OptimizationType.GENERAL: [
                "提升了整体表达的清晰度和准确性",
                "增加了必要的上下文信息"
            ],
            OptimizationType.STRUCTURED: [
                "采用了结构化的组织形式",
                "明确了任务步骤和输出格式"
            ],
            OptimizationType.ROLE_BASED: [
                "引入了专业角色设定",
                "强化了专业背景和能力描述"
            ],
            OptimizationType.TASK_ORIENTED: [
                "明确了任务目标和期望结果",
                "增加了具体的执行指导"
            ],
            OptimizationType.CREATIVE: [
                "增强了创意性和想象力引导",
                "鼓励多元化的思考角度"
            ],
            OptimizationType.LOGICAL: [
                "强化了逻辑推理结构",
                "增加了分析思考的指导"
            ]
        }
        
        suggestions.extend(type_suggestions.get(optimization_type, []))
        
        # 基于内容变化的建议
        original_len = len(original)
        optimized_len = len(optimized)
        
        if optimized_len > original_len * 1.5:
            suggestions.append("显著扩展了提示词的详细程度")
        elif optimized_len > original_len * 1.2:
            suggestions.append("适度增加了指导信息")
        
        # 检查结构化元素
        if "##" in optimized or "**" in optimized:
            suggestions.append("使用了Markdown格式增强可读性")
        
        if "步骤" in optimized or "Step" in optimized:
            suggestions.append("添加了步骤化的执行指导")
        
        if "例如" in optimized or "比如" in optimized:
            suggestions.append("提供了具体的示例说明")
        
        return suggestions if suggestions else ["应用了基于模板的智能优化策略"]
    
    def _calculate_metrics(self, original: str, optimized: str, 
                          optimization_type: OptimizationType) -> Dict[str, float]:
        """计算优化指标"""
        metrics = {}
        
        # 长度变化比例
        length_ratio = len(optimized) / max(len(original), 1)
        metrics["length_improvement"] = (length_ratio - 1) * 100
        
        # 结构化程度
        structure_score = 0
        structure_indicators = ["##", "**", "1.", "2.", "-", "步骤", "要求"]
        for indicator in structure_indicators:
            if indicator in optimized:
                structure_score += 1
        
        metrics["structure_score"] = min(structure_score / len(structure_indicators) * 10, 10)
        
        # 详细程度
        detail_indicators = ["具体", "详细", "例如", "比如", "包括", "需要", "应该"]
        detail_score = sum(1 for indicator in detail_indicators if indicator in optimized)
        metrics["detail_score"] = min(detail_score / len(detail_indicators) * 10, 10)
        
        # 专业性
        professional_indicators = ["专业", "专家", "分析", "评估", "考虑", "建议"]
        professional_score = sum(1 for indicator in professional_indicators if indicator in optimized)
        metrics["professional_score"] = min(professional_score / len(professional_indicators) * 10, 10)
        
        # 综合改进分数
        metrics["overall_improvement"] = (
            metrics["structure_score"] * 0.3 +
            metrics["detail_score"] * 0.3 +
            metrics["professional_score"] * 0.4
        )
        
        return metrics


# 导出服务类
__all__ = ["OptimizationService"]
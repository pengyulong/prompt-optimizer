"""
模板管理器 - 使用Jinja2渲染Markdown模板
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, Template
from dataclasses import dataclass, asdict

from utils.logger import get_logger
from utils.exceptions import TemplateError

logger = get_logger(__name__)


@dataclass
class TemplateContext:
    """模板上下文数据类"""
    original_prompt: Optional[str] = None
    optimized_prompt: Optional[str] = None
    test_content: Optional[str] = None
    custom_instructions: Optional[str] = None
    optimization_type: Optional[str] = None
    additional_vars: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = asdict(self)
        if self.additional_vars:
            result.update(self.additional_vars)
        return result


class TemplateManager:
    """模板管理器"""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        初始化模板管理器
        
        Args:
            templates_dir: 模板目录路径
        """
        self.templates_dir = Path(templates_dir)
        self.config_path = self.templates_dir / "config" / "template_config.yaml"
        self.variables_path = self.templates_dir / "config" / "variables.yaml"
        
        # 初始化Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # 加载配置
        self.config = self._load_config()
        self.global_variables = self._load_global_variables()
        
        logger.info(f"模板管理器初始化完成，模板目录: {self.templates_dir}")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载模板配置"""
        try:
            if not self.config_path.exists():
                logger.warning(f"配置文件不存在: {self.config_path}")
                return {}
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info("模板配置加载成功")
                return config
        except Exception as e:
            logger.error(f"加载模板配置失败: {e}")
            return {}
    
    def _load_global_variables(self) -> Dict[str, Any]:
        """加载全局变量"""
        try:
            if not self.variables_path.exists():
                logger.info("全局变量文件不存在，使用默认配置")
                return {}
            
            with open(self.variables_path, 'r', encoding='utf-8') as f:
                variables = yaml.safe_load(f)
                logger.info("全局变量加载成功")
                return variables
        except Exception as e:
            logger.error(f"加载全局变量失败: {e}")
            return {}
    
    def get_optimization_template(self, 
                                 optimization_type: str,
                                 context: TemplateContext) -> str:
        """
        获取优化模板
        
        Args:
            optimization_type: 优化类型
            context: 模板上下文
            
        Returns:
            渲染后的模板内容
        """
        try:
            # 获取模板配置
            opt_config = self.config.get("optimization_types", {}).get(optimization_type)
            if not opt_config:
                raise TemplateError(f"未找到优化类型配置: {optimization_type}")
            
            template_path = opt_config["template"]
            
            # 合并变量
            template_vars = self._merge_variables(
                context,
                opt_config.get("default_variables", {}),
                {"optimization_type": optimization_type}
            )
            
            # 渲染模板
            return self._render_template(template_path, template_vars)
            
        except Exception as e:
            logger.error(f"获取优化模板失败: {optimization_type} - {e}")
            raise TemplateError(f"获取优化模板失败: {e}")
    
    def get_evaluation_template(self,
                               evaluation_type: str,
                               context: TemplateContext) -> str:
        """
        获取评估模板
        
        Args:
            evaluation_type: 评估类型
            context: 模板上下文
            
        Returns:
            渲染后的模板内容
        """
        try:
            eval_config = self.config.get("evaluation_types", {}).get(evaluation_type)
            if not eval_config:
                raise TemplateError(f"未找到评估类型配置: {evaluation_type}")
            
            template_path = eval_config["template"]
            
            # 添加默认评估标准
            additional_vars = {
                "evaluation_type": evaluation_type,
                "additional_criteria": self.config.get("default_evaluation_criteria", [])
            }
            
            template_vars = self._merge_variables(
                context,
                eval_config.get("default_variables", {}),
                additional_vars
            )
            
            return self._render_template(template_path, template_vars)
            
        except Exception as e:
            logger.error(f"获取评估模板失败: {evaluation_type} - {e}")
            raise TemplateError(f"获取评估模板失败: {e}")
    
    def get_testing_template(self,
                            testing_type: str,
                            context: TemplateContext) -> str:
        """
        获取测试模板
        
        Args:
            testing_type: 测试类型
            context: 模板上下文
            
        Returns:
            渲染后的模板内容
        """
        try:
            test_config = self.config.get("testing_types", {}).get(testing_type)
            if not test_config:
                raise TemplateError(f"未找到测试类型配置: {testing_type}")
            
            template_path = test_config["template"]
            
            template_vars = self._merge_variables(
                context,
                test_config.get("default_variables", {}),
                {"testing_type": testing_type}
            )
            
            return self._render_template(template_path, template_vars)
            
        except Exception as e:
            logger.error(f"获取测试模板失败: {testing_type} - {e}")
            raise TemplateError(f"获取测试模板失败: {e}")
    
    def _render_template(self, template_path: str, variables: Dict[str, Any]) -> str:
        """
        渲染模板
        
        Args:
            template_path: 模板路径
            variables: 模板变量
            
        Returns:
            渲染后的内容
        """
        try:
            # 检查是否是Python模板
            if template_path.startswith("python:"):
                template_key = template_path.replace("python:", "")
                return self._render_python_template(template_key, variables)
            else:
                # 使用Jinja2渲染markdown模板
                template = self.env.get_template(template_path)
                rendered = template.render(**variables)
                
                # 模板渲染成功
                return rendered
            
        except Exception as e:
            logger.error(f"模板渲染失败: {template_path} - {e}")
            raise TemplateError(f"模板渲染失败: {e}")
    
    def _render_python_template(self, template_key: str, variables: Dict[str, Any]) -> str:
        """渲染Python模板"""
        try:
            from .prompts import get_optimization_template
            
            # 获取模板内容
            template_content = get_optimization_template(template_key)
            
            # 简单的变量替换
            rendered = template_content
            for key, value in variables.items():
                placeholder = "{" + key + "}"
                if placeholder in rendered:
                    rendered = rendered.replace(placeholder, str(value))
            
            return rendered
            
        except Exception as e:
            logger.error(f"Python模板渲染失败: {template_key} - {e}")
            raise TemplateError(f"Python模板渲染失败: {e}")
    
    def _merge_variables(self, 
                        context: TemplateContext,
                        default_vars: Dict[str, Any],
                        additional_vars: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并模板变量
        
        Args:
            context: 模板上下文
            default_vars: 默认变量
            additional_vars: 额外变量
            
        Returns:
            合并后的变量字典
        """
        # 按优先级合并：additional_vars > context > default_vars > global_variables
        merged = {}
        
        # 1. 全局变量（最低优先级）
        merged.update(self.global_variables)
        
        # 2. 默认变量
        merged.update(default_vars)
        
        # 3. 上下文变量
        merged.update(context.to_dict())
        
        # 4. 额外变量（最高优先级）
        merged.update(additional_vars)
        
        # 过滤None值
        return {k: v for k, v in merged.items() if v is not None}
    
    def get_available_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取可用模板列表"""
        templates = {
            "optimization": [],
            "evaluation": [],
            "testing": []
        }
        
        for category in templates.keys():
            config_key = f"{category}_types"
            category_config = self.config.get(config_key, {})
            
            for type_key, type_config in category_config.items():
                templates[category].append({
                    "key": type_key,
                    "name": type_config.get("name", type_key),
                    "description": type_config.get("description", ""),
                    "icon": type_config.get("icon", "📄"),
                    "template": type_config.get("template", "")
                })
        
        return templates
    
    def validate_template(self, template_path: str) -> bool:
        """
        验证模板是否存在且有效
        
        Args:
            template_path: 模板路径
            
        Returns:
            是否有效
        """
        try:
            full_path = self.templates_dir / template_path
            if not full_path.exists():
                logger.warning(f"模板文件不存在: {full_path}")
                return False
            
            # 尝试加载模板
            self.env.get_template(template_path)
            return True
            
        except Exception as e:
            logger.error(f"模板验证失败: {template_path} - {e}")
            return False
    
    def get_role_suggestions(self, content_type: str) -> Dict[str, Any]:
        """
        获取角色建议
        
        Args:
            content_type: 内容类型（如 'code', 'writing', 'analysis'）
            
        Returns:
            角色建议信息
        """
        role_suggestions = self.config.get("role_suggestions", {})
        return role_suggestions.get(content_type, {
            "suggested_roles": ["通用专家"],
            "traits": ["丰富的专业经验", "优秀的分析能力"]
        })
    
    def get_output_format_template(self, format_type: str) -> str:
        """
        获取输出格式模板
        
        Args:
            format_type: 格式类型
            
        Returns:
            格式模板
        """
        output_formats = self.config.get("output_formats", {})
        format_config = output_formats.get(format_type, {})
        return format_config.get("example", "")
    
    def reload_config(self):
        """重新加载配置"""
        logger.info("重新加载模板配置")
        self.config = self._load_config()
        self.global_variables = self._load_global_variables()


# 便捷函数
def create_template_context(original_prompt: str = None,
                           optimized_prompt: str = None,
                           test_content: str = None,
                           custom_instructions: str = None,
                           **kwargs) -> TemplateContext:
    """创建模板上下文的便捷函数"""
    return TemplateContext(
        original_prompt=original_prompt,
        optimized_prompt=optimized_prompt,
        test_content=test_content,
        custom_instructions=custom_instructions,
        additional_vars=kwargs
    )


# 全局模板管理器实例
template_manager = TemplateManager()


# 导出主要类和函数
__all__ = [
    "TemplateManager",
    "TemplateContext", 
    "create_template_context",
    "template_manager"
]
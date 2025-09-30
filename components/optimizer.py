"""
提示词优化组件
"""

import streamlit as st
from typing import Optional, Dict, Any
import time

from core.models import (
    OptimizationRequest, OptimizationType, ModelProvider, GenerationConfig
)
from services.optimization import OptimizationService
from config.settings import OptimizationConfig, UIConfig
from utils.logger import get_logger, user_logger
from utils.exceptions import ModelError, ValidationError

logger = get_logger(__name__)

class OptimizerComponent:
    """提示词优化组件"""
    
    def __init__(self):
        self.optimization_service = OptimizationService()
    
    def render(self):
        """渲染优化组件"""
        try:
            self._render_input_section()
            self._render_config_section()
            self._render_optimization_button()
            self._render_results_section()
        except Exception as e:
            logger.error(f"渲染优化组件失败: {str(e)}")
            st.error(f"组件渲染失败: {str(e)}")
    
    def _render_input_section(self):
        """渲染输入区域"""
        st.subheader("📝 输入提示词")
        
        # 原始提示词输入
        original_prompt = st.text_area(
            "请输入需要优化的原始提示词",
            height=150,
            key="original_prompt",
            placeholder="在此输入您的原始提示词...\n\n例如：\n- 请介绍一下Python编程语言\n- 帮我写一个排序算法\n- 分析这篇文章的主要观点",
            help="输入您想要优化的提示词，支持多行文本"
        )
        
        # 输入验证
        if original_prompt:
            char_count = len(original_prompt)
            max_length = OptimizationConfig.MAX_PROMPT_LENGTH
            
            # 显示字符计数
            if char_count > max_length:
                st.error(f"⚠️ 提示词长度超出限制: {char_count}/{max_length} 字符")
            else:
                progress = char_count / max_length
                st.progress(progress, text=f"字符数: {char_count}/{max_length}")
        
        return original_prompt
    
    def _render_config_section(self):
        """渲染配置区域"""
        st.subheader("⚙️ 优化配置")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # 模型选择
            available_models = self._get_available_models()
            if not available_models:
                st.error("❌ 没有可用的模型，请检查配置")
                return None, None, None
            
            model_options = [f"{info['provider']} / {info['display_name']}" 
                           for info in available_models]
            
            selected_model_index = st.selectbox(
                "选择模型",
                range(len(model_options)),
                format_func=lambda x: model_options[x],
                key="selected_model_index",
                help="选择用于优化的AI模型"
            )
            
            selected_model = available_models[selected_model_index]
        
        with col2:
            # 优化类型选择
            optimization_options = OptimizationConfig.OPTIMIZATION_TYPES
            
            opt_display = [f"{opt['icon']} {opt['name']}" for opt in optimization_options]
            
            selected_opt_index = st.selectbox(
                "优化策略",
                range(len(opt_display)),
                format_func=lambda x: opt_display[x],
                key="selected_optimization_type",
                help="选择适合您需求的优化策略"
            )
            
            selected_opt = optimization_options[selected_opt_index]
            
            # 显示策略描述
            st.info(f"💡 {selected_opt['description']}")
        
        # 高级选项
        if st.checkbox("🔧 高级选项", key="show_advanced_options"):
            self._render_advanced_options()
        
        return selected_model, selected_opt, self._get_generation_config()
    
    def _render_advanced_options(self):
        """渲染高级选项"""
        st.markdown("**生成参数调整**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            temperature = st.slider(
                "创造性 (Temperature)",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                key="temperature",
                help="较高值使输出更随机，较低值使输出更确定"
            )
        
        with col2:
            max_tokens = st.slider(
                "最大输出长度",
                min_value=100,
                max_value=8192,
                value=4096,
                step=100,
                key="max_tokens",
                help="限制生成的最大token数量"
            )
        
        with col3:
            top_p = st.slider(
                "核采样 (Top-p)",
                min_value=0.1,
                max_value=1.0,
                value=0.9,
                step=0.1,
                key="top_p",
                help="控制词汇多样性的参数"
            )
        
        # 系统提示词
        system_prompt = st.text_area(
            "系统提示词 (可选)",
            key="system_prompt",
            placeholder="为AI设定角色或行为规范...",
            help="可以为AI设定特定的角色或行为准则"
        )
    
    def _render_optimization_button(self):
        """渲染优化按钮"""
        original_prompt = st.session_state.get("original_prompt", "")
        
        # 检查是否有输入
        if not original_prompt.strip():
            st.warning("⚠️ 请先输入需要优化的提示词")
            return
        
        # 检查模型可用性
        if not self._check_model_availability():
            st.error("❌ 所选模型不可用，请检查配置或选择其他模型")
            return
        
        # 优化按钮
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button(
                "🚀 开始优化",
                type="primary",
                use_container_width=True,
                key="optimize_button"
            ):
                self._execute_optimization()
    
    def _execute_optimization(self):
        """执行优化"""
        try:
            original_prompt = st.session_state.get("original_prompt", "")
            
            # 获取配置
            model_info, opt_type, gen_config = self._render_config_section()
            
            if not all([model_info, opt_type, gen_config]):
                st.error("配置信息不完整")
                return
            
            # 创建优化请求
            request = OptimizationRequest(
                original_prompt=original_prompt,
                optimization_type=OptimizationType(opt_type["key"]),
                model_provider=ModelProvider(model_info["provider"]),
                model_name=model_info["name"],
                generation_config=gen_config,
                user_id=st.session_state.get("session_id")
            )
            
            # 显示进度
            with st.spinner("🔄 正在优化中，请稍候..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # 更新进度
                progress_bar.progress(0.3)
                status_text.text("正在分析原始提示词...")
                time.sleep(0.5)
                
                progress_bar.progress(0.6)
                status_text.text("正在生成优化建议...")
                
                # 执行优化
                result = self.optimization_service.optimize_prompt(request)
                
                progress_bar.progress(1.0)
                status_text.text("优化完成！")
                time.sleep(0.5)
                
                # 清除进度显示
                progress_bar.empty()
                status_text.empty()
            
            if result and result.response.success:
                # 保存结果到session state
                st.session_state.current_optimization = result
                
                # 添加到用户会话历史
                st.session_state.user_session.add_optimization(result)
                
                # 记录用户操作
                user_logger.log_optimization(
                    user_id=st.session_state.get("session_id"),
                    optimization_type=opt_type["name"],
                    model=f"{model_info['provider']}/{model_info['name']}",
                    prompt_length=len(original_prompt),
                    success=True
                )
                
                # 显示成功消息
                st.success(f"✅ 优化完成！用时 {result.response.response_time:.2f} 秒")
                
                # 自动滚动到结果区域
                st.rerun()
                
            else:
                error_msg = result.response.error if result else "未知错误"
                st.error(f"❌ 优化失败: {error_msg}")
                
                # 记录失败的操作
                user_logger.log_optimization(
                    user_id=st.session_state.get("session_id"),
                    optimization_type=opt_type["name"],
                    model=f"{model_info['provider']}/{model_info['name']}",
                    prompt_length=len(original_prompt),
                    success=False
                )
                
        except ValidationError as e:
            st.error(f"❌ 输入验证失败: {str(e)}")
        except ModelError as e:
            st.error(f"❌ 模型调用失败: {str(e)}")
        except Exception as e:
            logger.error(f"优化执行失败: {str(e)}")
            st.error(f"❌ 优化过程中发生错误: {str(e)}")
    
    def _render_results_section(self):
        """渲染结果区域"""
        st.subheader("📋 优化结果")
        
        if "current_optimization" not in st.session_state or not st.session_state.current_optimization:
            st.info("💡 优化后的提示词将在此显示...")
            return
        
        result = st.session_state.current_optimization
        original_prompt = st.session_state.get("original_prompt", "")
        
        # 创建标签页
        tab1, tab2, tab3 = st.tabs(["📋 对比结果", "💡 优化建议", "📊 详细信息"])
        
        with tab1:
            self._render_comparison_tab(result, original_prompt)
        
        with tab2:
            self._render_suggestions_tab(result)
        
        with tab3:
            self._render_details_tab(result)
    
    def _render_comparison_tab(self, result, original_prompt):
        """渲染对比标签页"""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("**🔧 优化后**")
            st.text_area(
                "优化后的提示词",
                value=result.optimized_prompt,
                height=300,
                key="optimized_display",
                label_visibility="collapsed"
            )
            
            # 复制按钮
            if st.button("📋 复制优化后", key="copy_optimized", use_container_width=True):
                st.info("💡 请手动复制上方文本")
            
            # 字符统计
            optimized_length = len(result.optimized_prompt)
            st.caption(f"字符数: {optimized_length}")
        
        with col2:
            st.markdown("**📝 原始**")
            st.text_area(
                "原始提示词",
                value=original_prompt,
                height=300,
                key="original_display",
                disabled=True,
                label_visibility="collapsed"
            )
            
            # 复制按钮
            if st.button("📋 复制原始", key="copy_original", use_container_width=True):
                st.info("💡 请手动复制上方文本")
            
            # 字符统计和对比
            original_length = len(original_prompt)
            length_diff = optimized_length - original_length
            st.caption(f"字符数: {original_length}")
            
            if length_diff > 0:
                st.caption(f"🔺 增加了 {length_diff} 个字符")
            elif length_diff < 0:
                st.caption(f"🔻 减少了 {abs(length_diff)} 个字符")
            else:
                st.caption("➡️ 字符数无变化")
    
    def _render_suggestions_tab(self, result):
        """渲染建议标签页"""
        st.markdown("**🎯 优化要点**")
        
        for i, suggestion in enumerate(result.suggestions, 1):
            st.markdown(f"{i}. {suggestion}")
        
        # 优化类型说明
        st.markdown("---")
        st.markdown(f"**📋 使用的优化策略**: {result.request.optimization_type.value}")
        
        # 模型信息
        st.markdown(f"**🤖 使用的模型**: {result.request.model_provider.value} / {result.request.model_name}")
        
        # 性能指标
        if result.metrics:
            st.markdown("**📊 性能指标**")
            cols = st.columns(len(result.metrics))
            for i, (metric, value) in enumerate(result.metrics.items()):
                with cols[i]:
                    st.metric(metric.title(), f"{value:.2f}")
    
    def _render_details_tab(self, result):
        """渲染详细信息标签页"""
        st.markdown("**⏱️ 执行信息**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("响应时间", f"{result.response.response_time:.2f}s")
        
        with col2:
            if result.response.tokens_used:
                st.metric("生成Tokens", result.response.tokens_used)
            else:
                st.metric("生成Tokens", "N/A")
        
        with col3:
            if result.response.tokens_prompt:
                st.metric("输入Tokens", result.response.tokens_prompt)
            else:
                st.metric("输入Tokens", "N/A")
        
        with col4:
            total_tokens = 0
            if result.response.tokens_used and result.response.tokens_prompt:
                total_tokens = result.response.tokens_used + result.response.tokens_prompt
            st.metric("总Tokens", total_tokens if total_tokens > 0 else "N/A")
        
        # 元数据信息
        if result.response.metadata:
            st.markdown("**🔍 元数据**")
            
            # 格式化显示元数据
            metadata_display = {}
            for key, value in result.response.metadata.items():
                if isinstance(value, (int, float)):
                    if 'duration' in key.lower():
                        # 转换纳秒为毫秒
                        if value > 1000000:
                            metadata_display[key] = f"{value / 1000000:.2f} ms"
                        else:
                            metadata_display[key] = f"{value:.2f} ns"
                    else:
                        metadata_display[key] = str(value)
                else:
                    metadata_display[key] = str(value)
            
            for key, value in metadata_display.items():
                st.text(f"{key}: {value}")
        
        # 时间戳
        st.markdown("---")
        st.caption(f"创建时间: {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _get_available_models(self):
        """获取可用模型列表"""
        try:
            if not st.session_state.model_client:
                return []
            
            models = st.session_state.model_client.get_available_models()
            
            # 转换为显示格式
            model_list = []
            for model in models:
                model_list.append({
                    "name": model.name,
                    "display_name": model.display_name,
                    "provider": model.provider.value,
                    "description": model.description,
                    "category": model.category
                })
            
            return model_list
            
        except Exception as e:
            logger.error(f"获取可用模型失败: {str(e)}")
            return []
    
    def _check_model_availability(self):
        """检查所选模型可用性"""
        try:
            if not st.session_state.model_client:
                return False
            
            # 这里可以添加具体的模型可用性检查逻辑
            return True
            
        except Exception as e:
            logger.error(f"检查模型可用性失败: {str(e)}")
            return False
    
    def _get_generation_config(self) -> GenerationConfig:
        """获取生成配置"""
        config = GenerationConfig()
        
        # 如果启用了高级选项，使用用户设置
        if st.session_state.get("show_advanced_options", False):
            config.temperature = st.session_state.get("temperature", 0.7)
            config.max_tokens = st.session_state.get("max_tokens", 4096)
            config.top_p = st.session_state.get("top_p", 0.9)
            config.system_prompt = st.session_state.get("system_prompt", "")
        
        return config

# 导出组件类
__all__ = ["OptimizerComponent"]
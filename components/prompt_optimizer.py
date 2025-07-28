import streamlit as st
from services.optimization_service import OptimizationService
from utils.config import OPTIMIZATION_CONFIG

class PromptOptimizerComponent:
    def __init__(self):
        self.optimization_service = OptimizationService()
    
    def render(self):
        """渲染提示词优化器界面"""
        
        # 输入原始提示词
        original_prompt = st.text_area(
            "请输入需要优化的原始提示词...",
            height=150,
            key="original_prompt",
            placeholder="在此输入您的原始提示词..."
        )
        
        # 优化配置选项
        col1, col2 = st.columns([1, 2])
        
        with col1:
            optimization_model = st.selectbox(
                "优化模型",
                options=OPTIMIZATION_CONFIG["models"],
                key="optimization_model"
            )
        
        with col2:
            optimization_type = st.selectbox(
                "请选择优化类型",
                options=OPTIMIZATION_CONFIG["optimization_types"],
                key="optimization_type"
            )
        
        # 优化按钮
        optimize_button = st.button(
            "开始优化",
            type="primary",
            use_container_width=True,
            key="optimize_button"
        )
        
        # 显示优化结果
        st.subheader("优化后的提示词")
        
        if optimize_button and original_prompt:
            with st.spinner("正在优化中..."):
                try:
                    optimized_result = self.optimization_service.optimize_prompt(
                        original_prompt,
                        optimization_model,
                        optimization_type
                    )
                    
                    # 存储到session state
                    st.session_state.optimized_prompt = optimized_result["optimized_prompt"]
                    st.session_state.optimization_suggestions = optimized_result["suggestions"]
                    
                except Exception as e:
                    st.error(f"优化失败: {str(e)}")
        
        # 显示优化结果
        if "optimized_prompt" in st.session_state:
            # 创建两列用于显示结果
            result_col1, result_col2 = st.columns([1, 1])
            
            with result_col1:
                st.text_area(
                    "优化后",
                    value=st.session_state.optimized_prompt,
                    height=200,
                    key="optimized_display"
                )
                
                if st.button("📋 复制", key="copy_optimized"):
                    st.success("已复制到剪贴板!")
                    # 这里可以添加复制到剪贴板的功能
            
            with result_col2:
                st.text_area(
                    "原文",
                    value=original_prompt,
                    height=200,
                    key="original_display",
                    disabled=True
                )
                
                if st.button("📋 复制", key="copy_original"):
                    st.success("已复制到剪贴板!")
        
        else:
            # 空状态
            st.info("优化后的提示词将在此显示...")
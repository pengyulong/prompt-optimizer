import streamlit as st
from typing import Dict, Any
from core.client import create_client


class TesterComponent:
    """测试组件"""
    
    def __init__(self):
        self.test_results = {}
    
    def render(self):
        """渲染测试界面"""
        st.header("🧪 提示词效果测试")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("原始提示词效果")
            original_prompt = st.text_area(
                "原始提示词",
                placeholder="输入原始提示词...",
                height=100
            )
            test_input = st.text_area(
                "测试输入内容",
                placeholder="输入要测试的内容...",
                height=150
            )
        
        with col2:
            st.subheader("优化后提示词效果")
            optimized_prompt = st.text_area(
                "优化后提示词",
                placeholder="优化后的提示词将显示在这里...",
                height=100,
                disabled=True
            )
            test_output_original = st.text_area(
                "原始提示词结果",
                placeholder="原始提示词的测试结果将显示在这里...",
                height=150,
                disabled=True
            )
            test_output_optimized = st.text_area(
                "优化后提示词结果",
                placeholder="优化后提示词的测试结果将显示在这里...",
                height=150,
                disabled=True
            )
        
        # 测试按钮
        if st.button("🚀 开始测试", use_container_width=True):
            if not test_input.strip():
                st.error("请输入测试内容")
                return
            
            if not original_prompt.strip():
                st.error("请输入原始提示词")
                return
            
            self.run_comparison_test(original_prompt, optimized_prompt, test_input)
    
    def run_comparison_test(self, original_prompt: str, optimized_prompt: str, test_input: str):
        """运行对比测试"""
        try:
            # 获取当前选择的模型
            model_provider = st.session_state.get('model_provider', 'ollama')
            model_name = st.session_state.get('model_name', 'llama3.2:latest')
            
            client = create_client(model_provider, model_name)
            
            # 测试原始提示词
            with st.spinner("测试原始提示词..."):
                original_result = client.generate(f"{original_prompt}\n\n{test_input}")
            
            # 测试优化后提示词
            with st.spinner("测试优化后提示词..."):
                optimized_result = client.generate(f"{optimized_prompt}\n\n{test_input}")
            
            # 显示结果
            st.success("测试完成！")
            
            # 性能分析
            self.analyze_results(original_result, optimized_result)
            
        except Exception as e:
            st.error(f"测试失败: {str(e)}")
    
    def analyze_results(self, original_result: str, optimized_result: str):
        """分析测试结果"""
        st.subheader("📊 性能分析")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("原始结果长度", len(original_result))
        
        with col2:
            st.metric("优化结果长度", len(optimized_result))
        
        with col3:
            improvement = len(optimized_result) - len(original_result)
            st.metric("长度差异", improvement, delta=f"{improvement}字符")
        
        with col4:
            # 简单的质量评估（可以根据需要扩展）
            quality_score = min(100, len(optimized_result) / max(len(original_result), 1) * 100)
            st.metric("质量评分", f"{quality_score:.1f}%")
        
        # 详细对比
        with st.expander("详细对比分析"):
            tab1, tab2 = st.tabs(["原始结果", "优化结果"])
            
            with tab1:
                st.text_area("原始提示词结果", original_result, height=200)
            
            with tab2:
                st.text_area("优化后提示词结果", optimized_result, height=200)
import streamlit as st
from typing import Dict, Any
from core.client import create_client


class TesterComponent:
    """测试组件"""
    
    def __init__(self):
        self.test_results = {}
    
    def render(self):
        """统一风格的测试界面"""
        # st.header("🧪 效果测试")
        
        # 输入区域
        st.markdown("####  📝 测试内容")
        test_input = st.text_area(
            "输入测试内容",
            placeholder="输入要测试的内容...",
            height=150,
            help="输入您想要测试的内容，可以是问题、文本片段等"
        )
        # 自动填充优化前后的提示词
        if "current_optimization" not in st.session_state or not st.session_state.current_optimization:
            st.warning("请先完成提示词优化")
            return
            
        original_prompt = st.session_state.get("original_prompt", "")
        optimized_prompt = st.session_state.current_optimization.optimized_prompt
        
        st.markdown("####   ?? 对比测试")
        tab1, tab2 = st.tabs(["原始提示词", "优化后提示词"])
        
        with tab1:
            st.text_area(
                "原始提示词",
                value=original_prompt,
                height=150,
                disabled=True,
                label_visibility="collapsed"
            )
        
        with tab2:
            st.text_area(
                "优化后提示词",
                value=optimized_prompt,
                height=150,
                disabled=True,
                label_visibility="collapsed"
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
        """统一风格的结果分析"""
        st.markdown("####  📋 测试结果对比")
        
        # 结果展示
        tab1, tab2 = st.tabs(["原始结果", "优化结果"])
        
        with tab1:
            st.text_area(
                "原始提示词结果", 
                original_result,
                height=200,
                label_visibility="collapsed"
            )
        
        with tab2:
            st.text_area(
                "优化后提示词结果",
                optimized_result,
                height=200,
                label_visibility="collapsed"
            )
        
        # 性能指标
        st.markdown("####  📊 性能指标")
        cols = st.columns(3)
        
        with cols[0]:
            st.metric("原始结果长度", f"{len(original_result)} 字符")
        
        with cols[1]:
            st.metric("优化结果长度", f"{len(optimized_result)} 字符")
        
        with cols[2]:
            improvement = len(optimized_result) - len(original_result)
            st.metric(
                "长度差异", 
                f"{abs(improvement)} 字符",
                delta=f"{'+' if improvement > 0 else ''}{improvement} 字符"
            )
        
        # 复制按钮
        copy_cols = st.columns(2)
        with copy_cols[0]:
            if st.button("📋 复制原始结果", use_container_width=True):
                st.session_state.copied_text = original_result
                st.toast("已复制原始结果", icon="📋")
        
        with copy_cols[1]:
            if st.button("📋 复制优化结果", type="primary", use_container_width=True):
                st.session_state.copied_text = optimized_result
                st.toast("已复制优化结果", icon="📋")
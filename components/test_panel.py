import streamlit as st
from services.test_service import TestService
from utils.config import TEST_CONFIG

class TestPanelComponent:
    def __init__(self):
        self.test_service = TestService()
    
    def render(self):
        """渲染测试面板界面"""
        
        # 测试内容输入
        test_content = st.text_area(
            "请输入要测试的内容...",
            height=150,
            key="test_content",
            placeholder="输入测试内容以验证优化效果..."
        )
        
        # 模型选择
        test_model = st.selectbox(
            "模型",
            options=TEST_CONFIG["models"],
            key="test_model"
        )
        
        # 对比测试按钮
        test_button = st.button(
            "开始对比",
            type="primary",
            use_container_width=True,
            key="test_button"
        )
        
        # 显示测试结果
        if test_button and test_content:
            if "optimized_prompt" in st.session_state:
                self._run_comparison_test(test_content)
            else:
                st.warning("请先优化提示词后再进行测试")
        
        # 结果显示区域
        self._render_test_results()
    
    def _run_comparison_test(self, test_content):
        """运行对比测试"""
        with st.spinner("正在进行对比测试..."):
            try:
                # 获取原始提示词和优化后提示词的结果
                original_prompt = st.session_state.get("original_prompt", "")
                optimized_prompt = st.session_state.get("optimized_prompt", "")
                
                # 调用测试服务
                test_results = self.test_service.compare_prompts(
                    original_prompt=original_prompt,
                    optimized_prompt=optimized_prompt,
                    test_content=test_content,
                    model=st.session_state.test_model
                )
                
                # 存储测试结果
                st.session_state.test_results = test_results
                
            except Exception as e:
                st.error(f"测试失败: {str(e)}")
    
    def _render_test_results(self):
        """渲染测试结果"""
        st.subheader("原始提示词结果")
        st.subheader("优化后提示词结果")
        
        if "test_results" in st.session_state:
            results = st.session_state.test_results
            
            # 创建两列显示对比结果
            result_col1, result_col2 = st.columns([1, 1])
            
            with result_col1:
                st.text_area(
                    "原始",
                    value=results.get("original_result", ""),
                    height=300,
                    key="original_result_display"
                )
                
                if st.button("📋 复制", key="copy_original_result"):
                    st.success("已复制!")
            
            with result_col2:
                st.text_area(
                    "原文",
                    value=results.get("optimized_result", ""),
                    height=300,
                    key="optimized_result_display"
                )
                
                if st.button("📋 复制", key="copy_optimized_result"):
                    st.success("已复制!")
            
            # 显示性能指标对比
            self._render_performance_metrics(results)
        
        else:
            st.info("测试结果将在此显示...")
    
    def _render_performance_metrics(self, results):
        """渲染性能指标对比"""
        st.subheader("📊 性能对比")
        
        metrics = results.get("metrics", {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "响应时间", 
                f"{metrics.get('original_time', 0):.2f}s",
                f"{metrics.get('time_improvement', 0):+.2f}s"
            )
        
        with col2:
            st.metric(
                "准确性评分", 
                f"{metrics.get('original_accuracy', 0):.1f}",
                f"{metrics.get('accuracy_improvement', 0):+.1f}"
            )
        
        with col3:
            st.metric(
                "相关性", 
                f"{metrics.get('original_relevance', 0):.1f}",
                f"{metrics.get('relevance_improvement', 0):+.1f}"
            )
        
        with col4:
            st.metric(
                "完整性", 
                f"{metrics.get('original_completeness', 0):.1f}",
                f"{metrics.get('completeness_improvement', 0):+.1f}"
            )
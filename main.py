import streamlit as st
from components.prompt_optimizer import PromptOptimizerComponent
from components.test_panel import TestPanelComponent
from utils.config import APP_CONFIG
from utils.helpers import init_session_state

def main():
    # 设置页面配置
    st.set_page_config(
        page_title=APP_CONFIG["app_title"],
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 初始化会话状态
    init_session_state()
    
    # 应用标题和导航
    st.title("🤖 提示词优化器")
    
    # 创建两列布局
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("原始提示词")
        prompt_optimizer = PromptOptimizerComponent()
        prompt_optimizer.render()
    
    with col2:
        st.header("测试内容")
        test_panel = TestPanelComponent()
        test_panel.render()

if __name__ == "__main__":
    main()
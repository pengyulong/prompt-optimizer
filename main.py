"""
提示词优化器主应用
"""

import streamlit as st
import traceback
from typing import Optional

# 导入配置和核心模块
from config.settings import AppConfig, UIConfig, ConfigValidator
from core.client import UniversalModelClient
from core.models import UserSession, create_task_id
from utils.logger import get_logger, user_logger
from utils.exceptions import PromptOptimizerError

# 导入组件
from components.sidebar import SidebarComponent
from components.optimizer import OptimizerComponent
from components.tester import TesterComponent

# 配置日志
logger = get_logger(__name__)

def setup_page_config():
    """设置页面配置"""
    st.set_page_config(
        page_title=AppConfig.APP_NAME,
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'About': f"{AppConfig.APP_NAME} v{AppConfig.VERSION}\n\n{AppConfig.DESCRIPTION}"
        }
    )
    
    # 自定义CSS
    st.markdown(f"""
    <style>
    .main {{
        max-width: {UIConfig.LAYOUT['max_width']}px;
        margin: 0 auto;
    }}
    
    .stButton > button {{
        width: 100%;
        background-color: {UIConfig.THEME['primary_color']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }}
    
    .stButton > button:hover {{
        background-color: {UIConfig.THEME['primary_color']}dd;
        border: none;
    }}
    
    .success-message {{
        color: {UIConfig.THEME['success_color']};
        font-weight: 500;
    }}
    
    .error-message {{
        color: {UIConfig.THEME['error_color']};
        font-weight: 500;
    }}
    
    .metric-card {{
        background-color: {UIConfig.THEME['background_color']};
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }}
    
    .model-status-connected {{
        color: {UIConfig.THEME['success_color']};
    }}
    
    .model-status-disconnected {{
        color: {UIConfig.THEME['error_color']};
    }}
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """初始化会话状态"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = create_task_id()
        
    if "user_session" not in st.session_state:
        st.session_state.user_session = UserSession(
            session_id=st.session_state.session_id
        )
        
    if "model_client" not in st.session_state:
        try:
            # 创建模型客户端，确保传入正确的默认配置
            from config.settings import OptimizationConfig
            st.session_state.model_client = UniversalModelClient(
                default_provider=OptimizationConfig.DEFAULT_PROVIDER,
                default_model=OptimizationConfig.DEFAULT_MODEL,
                config={}
            )
            logger.info("模型客户端初始化成功")
        except Exception as e:
            logger.error(f"模型客户端初始化失败: {str(e)}")
            st.session_state.model_client = None
    
    # 初始化其他状态
    if "current_optimization" not in st.session_state:
        st.session_state.current_optimization = None
        
    if "current_test" not in st.session_state:
        st.session_state.current_test = None
        
    if "show_advanced" not in st.session_state:
        st.session_state.show_advanced = False

def show_header():
    """统一标题和版本号的页面头部"""
    # 单行紧凑布局
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 1rem;">
            <h1 style="margin: 0;">🤖 AI提示词优化器</h1>
            <span style="color: {UIConfig.THEME['text_color']}99; font-size: 0.9rem;">
                v1.0.0
            </span>
        </div>
        <p style="color: {UIConfig.THEME['text_color']}99; margin-top: 0.5rem;">
            专业AI提示词优化与测试工具
        </p>
        """, unsafe_allow_html=True)
        
    with col2:
        # 仅在有配置问题时显示
        validation = ConfigValidator.validate_config()
        if not validation["valid"]:
            with st.expander("⚠️ 配置问题", expanded=False):
                for issue in validation["issues"]:
                    st.error(f"• {issue}")
                for warning in validation["warnings"]:
                    st.warning(f"• {warning}")

def show_main_content():
    """显示主要内容"""
    # 创建主要布局
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.header("🔧 提示词优化")
        optimizer = OptimizerComponent()
        optimizer.render()
    
    with col2:
        st.header("🧪 效果测试")
        tester = TesterComponent()
        tester.render()

def show_footer():
    """显示页面底部"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🗑️ 清除历史"):
            st.session_state.user_session.optimization_history.clear()
            st.session_state.user_session.test_history.clear()
            st.success("历史记录已清除")
            st.rerun()
    
    with col2:
        # 显示统计信息
        session = st.session_state.user_session
        opt_count = len(session.optimization_history)
        test_count = len(session.test_history)
        
        st.markdown(f"""
        <div style="text-align: center; color: {UIConfig.THEME['text_color']}99;">
            本次会话: {opt_count} 次优化, {test_count} 次测试 | 
            会话ID: {session.session_id[:8]}...
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("📊 查看统计"):
            show_statistics()

def show_statistics():
    """显示统计信息"""
    session = st.session_state.user_session
    
    with st.expander("📊 会话统计", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("优化次数", len(session.optimization_history))
        
        with col2:
            st.metric("测试次数", len(session.test_history))
        
        with col3:
            if session.optimization_history:
                avg_time = sum(opt.response.response_time 
                             for opt in session.optimization_history) / len(session.optimization_history)
                st.metric("平均优化时间", f"{avg_time:.2f}s")
            else:
                st.metric("平均优化时间", "0s")
        
        with col4:
            if session.test_history:
                avg_improvement = sum(result.improvement_summary.get('overall', 0) 
                                    for result in session.test_history) / len(session.test_history)
                st.metric("平均提升", f"{avg_improvement:.1f}%")
            else:
                st.metric("平均提升", "0%")
        
        # 最近活动
        if session.optimization_history or session.test_history:
            st.subheader("最近活动")
            
            recent_opts = session.get_recent_optimizations(5)
            recent_tests = session.get_recent_tests(5)
            
            if recent_opts:
                st.write("**最近优化:**")
                for opt in recent_opts:
                    st.write(f"• {opt.created_at.strftime('%H:%M:%S')} - "
                           f"{opt.request.optimization_type.value} "
                           f"({opt.request.model_name})")
            
            if recent_tests:
                st.write("**最近测试:**")
                for test in recent_tests:
                    improvement = test.improvement_summary.get('overall', 0)
                    st.write(f"• {test.created_at.strftime('%H:%M:%S')} - "
                           f"提升 {improvement:.1f}% ({test.request.model_name})")

def handle_error(error: Exception):
    """处理错误"""
    logger.error(f"应用错误: {str(error)}\n{traceback.format_exc()}")
    
    if isinstance(error, PromptOptimizerError):
        st.error(f"❌ {str(error)}")
    else:
        st.error(f"❌ 发生未知错误: {str(error)}")
        
        # 错误详情已简化处理
        st.code(traceback.format_exc())

def main():
    """主函数"""
    try:
        # 设置页面配置
        setup_page_config()
        
        # 初始化会话状态
        initialize_session_state()
        
        # 记录会话开始
        user_logger.log_session(
            st.session_state.session_id, 
            "session_start",
            user_agent=st.context.headers.get("User-Agent", "Unknown")
        )
        
        # 显示侧边栏
        sidebar = SidebarComponent()
        sidebar.render()
        
        # 显示页面头部
        show_header()
        
        # 显示主要内容
        show_main_content()
        
        # 显示页面底部
        show_footer()
        
        # 检查是否有错误状态需要显示
        if "last_error" in st.session_state and st.session_state.last_error:
            st.error(st.session_state.last_error)
            st.session_state.last_error = None
        
        logger.info("页面渲染完成")
        
    except Exception as e:
        handle_error(e)

if __name__ == "__main__":
    main()
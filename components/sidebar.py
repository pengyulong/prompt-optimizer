import streamlit as st
from typing import Dict, List
from config.settings import ConfigValidator, OptimizationConfig, ModelProvider
from config.settings import DEFAULT_PROVIDER, DEFAULT_MODEL
from core.client import create_client


class SidebarComponent:
    """侧边栏组件"""
    
    def __init__(self):
        self.config_validator = ConfigValidator
        self.optimization_config = OptimizationConfig
    
    def render(self):
        """渲染精简版侧边栏"""
        with st.sidebar:
            # 统一标题
            st.markdown("""
            <div style="text-align:center; margin-bottom:1.5rem;">
                <h2 style="margin-bottom:0;">🤖 AI提示词优化器</h2>
                <p style="color:#666; font-size:0.9rem; margin-top:0;">v1.0.0</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 模型选择(折叠版)
            with st.expander("🔧 模型设置", expanded=True):
                self._render_model_selection()
            
            # 优化策略(折叠版)
            with st.expander("🎯 优化策略", expanded=False):
                self._render_optimization_strategy()
            
            # 生成参数(折叠版)
            with st.expander("⚙️ 生成参数", expanded=False):
                self._render_generation_config()
            
            # 精简的应用信息
            st.markdown("---")
            self._render_app_info()
    
    def _render_model_selection(self):
        """精简版模型选择组件"""
        from services.adapters.openai import OpenAIModelAdapter
        from core.models import ModelProvider
        
        # 初始化默认值
        if 'model_provider' not in st.session_state:
            st.session_state['model_provider'] = ModelProvider.DEEPSEEK
        if 'model_name' not in st.session_state:
            st.session_state['model_name'] = 'deepseek-chat'

        # 紧凑的模型选择布局
        cols = st.columns([1, 1])
        with cols[0]:
            provider = st.selectbox(
                "提供商",
                [ModelProvider.DEEPSEEK, ModelProvider.OPENAI],
                format_func=lambda x: x.value,
                key='model_provider'
            )
        
        with cols[1]:
            adapter = OpenAIModelAdapter('', {'provider': provider})
            models = [m for m in adapter.get_available_models() if m.available]
            model = st.selectbox(
                "模型",
                [m.name for m in models],
                index=0,
                key='model_name'
            )

        # 简洁的状态指示器
        if st.button("🔄 测试连接", use_container_width=True):
            try:
                adapter = OpenAIModelAdapter(model, {'provider': provider})
                status = adapter.check_connection()
                st.session_state['model_client'] = adapter
                
                if status.connected:
                    st.success(f"连接正常 ({status.response_time:.2f}s)")
                else:
                    st.error("连接失败")
            except Exception as e:
                st.error(f"连接错误: {str(e)}")
    
    def _get_available_models(self, provider: ModelProvider) -> List[Dict]:
        """获取可用模型列表"""
        from config.settings import ModelConfig
        
        provider_config = ModelConfig.MODELS.get(provider, {})
        return provider_config.get("models", [])
    
    def _render_optimization_strategy(self):
        """精简版优化策略选择"""
        strategies = self.optimization_config.OPTIMIZATION_TYPES
        
        # 初始化默认策略
        if 'optimization_strategy' not in st.session_state:
            st.session_state['optimization_strategy'] = "general"
        
        # 紧凑的选择器布局
        strategy = st.selectbox(
            "选择优化类型",
            strategies,
            format_func=lambda x: f"{x['icon']} {x['name']}",
            index=next((i for i, s in enumerate(strategies) 
                       if s['key'] == st.session_state['optimization_strategy']), 0)
        )
        
        # 显示策略描述
        st.caption(strategy['description'])
        
        # 更新会话状态
        st.session_state['optimization_strategy'] = strategy['key']
    
    def _render_generation_config(self):
        """精简版生成参数配置"""
        # 初始化默认值
        defaults = {
            'temperature': 0.7,
            'top_p': 0.9
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
         
        cols = st.columns(2)
        with cols[0]:
            st.session_state['temperature'] = st.slider(
                "温度", 0.0, 2.0, st.session_state['temperature'], 0.1,
                help="控制输出的随机性(0-2)"
            )
        
        with cols[1]:
            st.session_state['top_p'] = st.slider(
                "多样性", 0.0, 1.0, st.session_state['top_p'], 0.05,
                help="控制输出的多样性(0-1)"
            )
        
        # 快速预设按钮
        preset_cols = st.columns(3)
        with preset_cols[0]:
            if st.button("保守", help="低随机性，高准确度"):
                st.session_state.update({
                    'temperature': 0.3,
                    'top_p': 0.7
                })
                st.rerun()
        
        with preset_cols[1]:
            if st.button("平衡", help="适中的随机性和准确度"):
                st.session_state.update({
                    'temperature': 0.7,
                    'top_p': 0.9
                })
                st.rerun()
        
        with preset_cols[2]:
            if st.button("创意", help="高随机性，创意输出"):
                st.session_state.update({
                    'temperature': 1.2,
                    'top_p': 1.0
                })
                st.rerun()
    
    def _render_app_info(self):
        """精简版应用信息"""
        cols = st.columns([1, 1])
        with cols[0]:
            st.markdown("""
            **版本**: 1.0.0  
            **更新**: 2025-10-06
            """)
            
            if st.button("📋 复制配置", help="复制当前配置到剪贴板"):
                config = {
                    'model': f"{st.session_state.get('model_provider', '')}/{st.session_state.get('model_name', '')}",
                    'strategy': st.session_state.get('optimization_strategy', ''),
                    'params': {
                        'temperature': st.session_state.get('temperature', 0),
                        'max_tokens': st.session_state.get('max_tokens', 0),
                        'top_p': st.session_state.get('top_p', 0)
                    }
                }
                st.session_state['copied_config'] = config
                st.toast("配置已复制", icon="✓")
        
        with cols[1]:
            st.markdown("""
            [📚 文档](https://github.com/your-repo/docs)  
            [🐞 反馈](https://github.com/your-repo/issues)
            """)
            
            if st.button("🔄 重置会话", help="清除所有会话状态", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key not in ['_pages', '_last_page']:
                        del st.session_state[key]
                st.rerun()
        
        # 简洁的性能指标
        if 'api_calls' in st.session_state:
            st.caption(f"API调用: {st.session_state['api_calls']}次")
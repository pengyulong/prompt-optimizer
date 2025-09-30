import streamlit as st
from typing import Dict, List
from config.settings import ConfigValidator, OptimizationConfig, ModelProvider
from core.client import create_client


class SidebarComponent:
    """侧边栏组件"""
    
    def __init__(self):
        self.config_validator = ConfigValidator
        self.optimization_config = OptimizationConfig
    
    def render(self):
        """渲染侧边栏"""
        with st.sidebar:
            st.title("🤖 AI提示词优化器")
            st.markdown("---")
            
            # 模型选择
            self._render_model_selection()
            st.markdown("---")
            
            # 优化策略选择
            self._render_optimization_strategy()
            st.markdown("---")
            
            # 生成参数配置
            self._render_generation_config()
            st.markdown("---")
            
            # 应用信息
            self._render_app_info()
    
    def _render_model_selection(self):
        """渲染模型选择部分"""
        st.subheader("🔧 模型配置")
        
        # 模型提供商选择
        available_providers = self.config_validator.get_available_providers()
        provider_names = [p.value for p in available_providers]
        
        # 初始化会话状态
        if 'model_provider' not in st.session_state:
            st.session_state['model_provider'] = provider_names[0] if provider_names else "ollama"
        
        selected_provider_name = st.selectbox(
            "选择模型提供商",
            provider_names,
            key="model_provider"
        )
        
        # 模型选择
        selected_provider = ModelProvider(selected_provider_name)
        models_config = self._get_available_models(selected_provider)
        model_names = [model["name"] for model in models_config]
        
        # 初始化会话状态
        if 'model_name' not in st.session_state:
            st.session_state['model_name'] = model_names[0] if model_names else "llama3.2:latest"
        
        selected_model = st.selectbox(
            "选择模型",
            model_names,
            key="model_name"
        )
    
    def _get_available_models(self, provider: ModelProvider) -> List[Dict]:
        """获取可用模型列表"""
        from config.settings import ModelConfig
        
        provider_config = ModelConfig.MODELS.get(provider, {})
        return provider_config.get("models", [])
    
    def _render_optimization_strategy(self):
        """渲染优化策略选择"""
        st.subheader("🎯 优化策略")
        
        strategies = self.optimization_config.OPTIMIZATION_TYPES
        strategy_names = [f"{strategy['icon']} {strategy['name']}" for strategy in strategies]
        
        # 初始化会话状态
        if 'optimization_strategy' not in st.session_state:
            st.session_state['optimization_strategy'] = "general"
        
        # 确保当前会话状态值在选项列表中
        current_strategy = st.session_state['optimization_strategy']
        if current_strategy not in [strategy['key'] for strategy in strategies]:
            st.session_state['optimization_strategy'] = "general"
        
        # 获取当前策略的显示名称
        current_display_name = "🔧 通用优化"
        for strategy in strategies:
            if strategy['key'] == st.session_state['optimization_strategy']:
                current_display_name = f"{strategy['icon']} {strategy['name']}"
                break
        
        selected_strategy_name = st.radio(
            "选择优化类型",
            strategy_names,
            index=strategy_names.index(current_display_name) if current_display_name in strategy_names else 0
        )
        
        # 获取策略对应的key
        strategy_key = "general"
        for strategy in strategies:
            if f"{strategy['icon']} {strategy['name']}" == selected_strategy_name:
                strategy_key = strategy['key']
                break
        
        # 更新会话状态
        st.session_state['optimization_strategy'] = strategy_key
    
    def _render_generation_config(self):
        """渲染生成参数配置"""
        st.subheader("⚙️ 生成参数")
        
        col1, col2 = st.columns(2)
        
        # 初始化会话状态
        if 'temperature' not in st.session_state:
            st.session_state['temperature'] = 0.7
        if 'max_tokens' not in st.session_state:
            st.session_state['max_tokens'] = 1024
        if 'top_p' not in st.session_state:
            st.session_state['top_p'] = 0.9
        
        with col1:
            temperature = st.slider(
                "温度 (Temperature)",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state['temperature'],
                step=0.1,
                key="temperature",
                help="控制输出的随机性，值越高输出越随机"
            )
            
            max_tokens = st.slider(
                "最大Token数",
                min_value=100,
                max_value=4096,
                value=st.session_state['max_tokens'],
                step=100,
                key="max_tokens",
                help="限制生成文本的最大长度"
            )
        
        with col2:
            top_p = st.slider(
                "核采样 (Top-p)",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state['top_p'],
                step=0.05,
                key="top_p",
                help="控制输出的多样性，值越小输出越集中"
            )
    
    def _render_app_info(self):
        """渲染应用信息"""
        st.subheader("ℹ️ 应用信息")
        
        st.markdown("""
        **版本**: 1.0.0  
        **作者**: Comate团队  
        **许可证**: MIT
        
        [📖 使用指南](https://github.com/your-repo/docs)  
        [🐛 报告问题](https://github.com/your-repo/issues)
        """)
        
        # 性能监控
        if 'api_calls' in st.session_state:
            st.metric("API调用次数", st.session_state['api_calls'])
        
        # 清空会话状态按钮
        if st.button("🔄 重置会话", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['_pages', '_last_page']:
                    del st.session_state[key]
            st.rerun()
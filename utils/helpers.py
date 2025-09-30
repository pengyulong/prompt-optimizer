"""
辅助函数模块
"""

import streamlit as st
import re
from datetime import datetime
from typing import Optional, Dict, Any

def init_session_state():
    """初始化Streamlit会话状态"""
    if "optimized_prompt" not in st.session_state:
        st.session_state.optimized_prompt = ""
    
    if "optimization_suggestions" not in st.session_state:
        st.session_state.optimization_suggestions = []
    
    if "test_results" not in st.session_state:
        st.session_state.test_results = {}
    
    if "optimization_history" not in st.session_state:
        st.session_state.optimization_history = []

def validate_prompt(prompt: str, max_length: int = 10000) -> Dict[str, Any]:
    """
    验证提示词输入
    
    Args:
        prompt: 提示词内容
        max_length: 最大长度限制
        
    Returns:
        验证结果字典
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    if not prompt or not prompt.strip():
        result["valid"] = False
        result["errors"].append("提示词不能为空")
        return result
    
    if len(prompt) > max_length:
        result["valid"] = False
        result["errors"].append(f"提示词长度不能超过{max_length}个字符")
    
    # 检查是否包含敏感内容（简单示例）
    sensitive_patterns = [
        r'密码|password',
        r'个人信息|personal.*info',
    ]
    
    for pattern in sensitive_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            result["warnings"].append("检测到可能的敏感信息，请谨慎使用")
            break
    
    return result

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """格式化时间戳"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def calculate_improvement_percentage(original: float, improved: float) -> float:
    """计算改进百分比"""
    if original == 0:
        return 0
    return ((improved - original) / original) * 100

def save_optimization_history(original_prompt: str, optimized_prompt: str, 
                             optimization_type: str, model: str):
    """保存优化历史记录"""
    history_entry = {
        "timestamp": format_timestamp(),
        "original_prompt": truncate_text(original_prompt, 200),
        "optimized_prompt": truncate_text(optimized_prompt, 200),
        "optimization_type": optimization_type,
        "model": model
    }
    
    st.session_state.optimization_history.append(history_entry)
    
    # 限制历史记录数量
    if len(st.session_state.optimization_history) > 50:
        st.session_state.optimization_history = st.session_state.optimization_history[-50:]

def export_results_to_text(results: Dict[str, Any]) -> str:
    """导出结果为文本格式"""
    export_text = f"""
提示词优化结果导出
==================

导出时间: {format_timestamp()}

原始提示词:
{results.get('original_prompt', 'N/A')}

优化后提示词:
{results.get('optimized_prompt', 'N/A')}

优化类型: {results.get('optimization_type', 'N/A')}
使用模型: {results.get('model_used', 'N/A')}

优化建议:
{chr(10).join(f"- {suggestion}" for suggestion in results.get('suggestions', []))}

测试结果:
{results.get('test_summary', '暂无测试结果')}
"""
    return export_text.strip()

def create_download_link(content: str, filename: str, link_text: str = "下载") -> str:
    """创建下载链接"""
    import base64
    
    b64_content = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:text/plain;base64,{b64_content}" download="{filename}">{link_text}</a>'
    return href

def display_metric_card(title: str, value: str, delta: Optional[str] = None):
    """显示指标卡片"""
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown(f"**{title}**")
    
    with col2:
        st.markdown(f"`{value}`")
    
    with col3:
        if delta:
            if delta.startswith("+"):
                st.markdown(f"🔺 {delta}")
            elif delta.startswith("-"):
                st.markdown(f"🔻 {delta}")
            else:
                st.markdown(delta)

def show_success_message(message: str, duration: int = 3):
    """显示成功消息"""
    success_placeholder = st.empty()
    success_placeholder.success(message)
    
    # 这里可以添加自动消失的逻辑
    # 在实际应用中可能需要使用JavaScript

def show_error_message(message: str, details: Optional[str] = None):
    """显示错误消息"""
    st.error(message)
    if details:
        with st.expander("错误详情"):
            st.text(details)

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"
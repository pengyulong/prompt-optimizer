"""
应用配置文件
"""

# 应用基础配置
APP_CONFIG = {
    "app_title": "提示词优化器",
    "version": "1.0.0",
    "description": "AI提示词优化和测试工具"
}

# 优化配置
OPTIMIZATION_CONFIG = {
    "models": [
        "qwen3",
        "gpt-4",
        "claude-3",
        "gemini-pro",
        "chatglm"
    ],
    "optimization_types": [
        "通用优化",
        "结构化优化", 
        "角色导向优化",
        "任务导向优化",
        "创意优化",
        "逻辑优化"
    ],
    "max_prompt_length": 10000,
    "timeout": 30
}

# 测试配置
TEST_CONFIG = {
    "models": [
        "请选择模型",
        "qwen3",
        "gpt-4", 
        "claude-3",
        "gemini-pro",
        "chatglm"
    ],
    "max_test_length": 5000,
    "comparison_metrics": [
        "accuracy",      # 准确性
        "relevance",     # 相关性
        "completeness",  # 完整性
        "creativity",    # 创意性
        "clarity"        # 清晰度
    ]
}

# UI配置
UI_CONFIG = {
    "primary_color": "#FF6B6B",
    "background_color": "#F8F9FA",
    "sidebar_width": 300,
    "main_content_width": 800
}

# API配置（预留）
API_CONFIG = {
    "base_url": "https://api.example.com",
    "timeout": 30,
    "max_retries": 3,
    "rate_limit": 60  # 每分钟请求数限制
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": "logs/app.log"
}
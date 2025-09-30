"""提示词模板管理"""

# 通用优化模板
GENERAL_OPTIMIZATION_TEMPLATE = """
你是一个专业的提示词优化专家。请对以下提示词进行优化，使其更加清晰、有效和易于理解。

原始提示词：
{prompt}

请按照以下要求进行优化：
1. 明确目标和意图
2. 改善语言表达和结构
3. 增加必要的上下文信息
4. 确保指令清晰明确
5. 优化格式和可读性

请提供：
1. 优化后的提示词
2. 优化说明和改进点
3. 使用建议
"""

# 结构化优化模板
STRUCTURED_OPTIMIZATION_TEMPLATE = """
你是一个结构化思维专家。请对以下提示词进行结构化优化，增加明确的格式要求和输出规范。

原始提示词：
{prompt}

请按照以下要求进行结构化优化：
1. 添加明确的输出格式要求（如JSON、Markdown、表格等）
2. 定义清晰的步骤和流程
3. 增加输入输出规范
4. 添加错误处理要求
5. 明确成功标准和验证方法

请提供结构化的优化版本。
"""

# 角色导向优化模板
ROLE_BASED_OPTIMIZATION_TEMPLATE = """
你是一个角色扮演专家。请为以下提示词添加合适的角色设定，使其更具专业性和针对性。

原始提示词：
{prompt}

请按照以下要求进行角色导向优化：
1. 定义明确的角色身份（如专家、助手、导师等）
2. 设定适当的语气和风格
3. 增加专业背景和知识领域
4. 优化交互方式和响应模式
5. 确保角色一致性

请提供角色化的优化版本。
"""

# 任务导向优化模板
TASK_ORIENTED_OPTIMIZATION_TEMPLATE = """
你是一个任务分解专家。请对以下提示词进行任务导向优化，使其更适合具体的任务执行。

原始提示词：
{prompt}

请按照以下要求进行任务导向优化：
1. 明确任务目标和交付物
2. 分解任务步骤和里程碑
3. 增加时间管理和优先级
4. 添加质量标准和验收条件
5. 优化资源需求和依赖关系

请提供任务导向的优化版本。
"""

# 创意优化模板
CREATIVE_OPTIMIZATION_TEMPLATE = """
你是一个创意激发专家。请对以下提示词进行创意优化，提升其创新性和想象力。

原始提示词：
{prompt}

请按照以下要求进行创意优化：
1. 增加创意元素和想象力
2. 优化故事性和吸引力
3. 添加情感共鸣点
4. 提升视觉和感官描述
5. 增强独特性和新颖性

请提供创意优化的版本。
"""

# 逻辑优化模板
LOGICAL_OPTIMIZATION_TEMPLATE = """
你是一个逻辑思维专家。请对以下提示词进行逻辑优化，增强其推理和分析能力。

原始提示词：
{prompt}

请按照以下要求进行逻辑优化：
1. 增强逻辑推理链条
2. 添加分析和论证结构
3. 优化因果关系表达
4. 增加证据和数据支持
5. 提升批判性思维要素

请提供逻辑优化的版本。
"""

# 测试评估模板
TEST_EVALUATION_TEMPLATE = """
请评估以下两个提示词在相同输入下的表现差异：

原始提示词：
{original_prompt}

优化后提示词：
{optimized_prompt}

测试输入：
{test_input}

请从以下维度进行评估：
1. 响应质量
2. 相关性
3. 完整性
4. 准确性
5. 创新性

提供详细的对比分析。
"""

# 获取优化模板的函数
def get_optimization_template(strategy: str) -> str:
    """根据策略获取对应的优化模板"""
    templates = {
        "general": GENERAL_OPTIMIZATION_TEMPLATE,
        "structured": STRUCTURED_OPTIMIZATION_TEMPLATE,
        "role_based": ROLE_BASED_OPTIMIZATION_TEMPLATE,
        "task_oriented": TASK_ORIENTED_OPTIMIZATION_TEMPLATE,
        "creative": CREATIVE_OPTIMIZATION_TEMPLATE,
        "logical": LOGICAL_OPTIMIZATION_TEMPLATE,
    }
    return templates.get(strategy, GENERAL_OPTIMIZATION_TEMPLATE)

# 模板配置
TEMPLATE_CONFIG = {
    "strategies": [
        {"name": "🔧 通用优化", "key": "general", "description": "适用于大多数场景的通用优化"},
        {"name": "📋 结构化优化", "key": "structured", "description": "增加明确的结构和格式要求"},
        {"name": "🎭 角色导向优化", "key": "role_based", "description": "基于特定角色或身份进行优化"},
        {"name": "🎯 任务导向优化", "key": "task_oriented", "description": "针对特定任务目标进行优化"},
        {"name": "💡 创意优化", "key": "creative", "description": "提升创意性和想象力的优化"},
        {"name": "🧠 逻辑优化", "key": "logical", "description": "增强逻辑推理和分析能力"},
    ]
}
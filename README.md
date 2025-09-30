# 🤖 AI提示词优化器

一个基于Streamlit的智能提示词优化和测试平台，支持多种AI模型，帮助用户优化提示词并评估其效果。

## ✨ 主要特性

- 🚀 **多模型支持**: 统一接口支持Ollama、OpenAI、Anthropic等多种AI模型
- 🔧 **智能优化**: 提供6种不同的优化策略，适应各种使用场景
- 🧪 **效果测试**: 实时对比原始提示词和优化后提示词的效果
- 📊 **性能分析**: 多维度评估指标，包括准确性、相关性、完整性等
- 🎨 **友好界面**: 基于Streamlit的现代化Web界面
- ⚙️ **环境配置**: 使用.env文件安全管理API密钥和配置
- 🔄 **异步支持**: 支持同步和异步模型调用
- 📝 **详细日志**: 完整的操作日志和性能监控
- 🏗️ **模块化架构**: 清晰的代码结构，便于扩展和维护

## 🏗️ 项目结构

```
prompt-optimizer/
├── .env                        # 环境变量配置
├── .env.example               # 环境变量示例
├── requirements.txt           # 项目依赖
├── main.py                    # 主应用入口
├── config/
│   └── settings.py           # 配置管理
├── core/
│   ├── models.py             # 数据模型
│   └── client.py             # 通用模型客户端
├── services/
│   ├── optimization.py       # 优化服务
│   ├── testing.py           # 测试服务
│   └── adapters/            # 模型适配器
│       ├── base.py          # 基础适配器
│       ├── ollama.py        # Ollama适配器
│       └── openai.py        # OpenAI适配器
├── components/
│   ├── optimizer.py         # 优化组件
│   ├── tester.py           # 测试组件
│   └── sidebar.py          # 侧边栏组件
├── utils/
│   ├── helpers.py          # 辅助函数
│   ├── logger.py           # 日志工具
│   └── exceptions.py       # 自定义异常
├── templates/
│   └── prompts.py          # 提示词模板
└── logs/                   # 日志目录
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd prompt-optimizer

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑.env文件，填入你的配置
# 至少需要配置一个模型提供商
```

#### Ollama配置（推荐本地使用）

```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 启动Ollama服务
ollama serve

# 下载模型（例如）
ollama pull llama3.2
ollama pull qwen2.5
```

在.env文件中配置：
```
OLLAMA_BASE_URL=http://localhost:11434
```

#### OpenAI配置

在.env文件中配置：
```
OPENAI_API_KEY=sk-your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 3. 运行应用

```bash
streamlit run main.py
```

应用将在浏览器中打开，默认地址：`http://localhost:8501`

## 📋 使用指南

### 基础使用流程

1. **选择模型**: 在侧边栏选择要使用的AI模型
2. **输入提示词**: 在左侧输入需要优化的原始提示词
3. **选择优化类型**: 选择适合的优化策略
4. **执行优化**: 点击"开始优化"按钮
5. **查看结果**: 查看优化后的提示词和改进建议
6. **测试效果**: 在右侧输入测试内容，对比两个提示词的效果
7. **分析结果**: 查看详细的性能指标和改进分析

### 优化策略说明

- **🔧 通用优化**: 适用于大多数场景的通用优化策略
- **📋 结构化优化**: 增加明确的结构和格式要求
- **🎭 角色导向优化**: 基于特定角色或身份进行优化
- **🎯 任务导向优化**: 针对特定任务目标进行优化
- **💡 创意优化**: 提升创意性和想象力的优化
- **🧠 逻辑优化**: 增强逻辑推理和分析能力

### 支持的模型

#### 本地模型（Ollama）
- Llama 3.2 - Meta的开源对话模型
- 通义千问 2.5 - 阿里巴巴的中文优化模型
- Mistral - 欧洲开源的高效模型
- Code Llama - 专门用于代码的模型
- DeepSeek Coder - 代码专用模型

#### 云端模型
- OpenAI GPT-4o/GPT-4 Turbo/GPT-3.5 Turbo
- Anthropic Claude 3.5 Sonnet/Claude 3 Opus
- 更多模型持续集成中...

## 🔧 高级配置

### 自定义模型参数

在代码中可以自定义生成参数：

```python
from core.client import create_client, GenerationConfig

# 创建客户端
client = create_client("ollama", "llama3.2:latest")

# 自定义配置
config = GenerationConfig(
    temperature=0.1,      # 降低随机性
    max_tokens=2048,      # 限制输出长度
    top_p=0.9,           # 核采样
    system_prompt="你是一个专业的AI助手"
)

# 生成文本
response = client.generate("你的提示词", config=config)
```

### 编程接口使用

```python
# 快速使用
from core.client import quick_generate, quick_chat

# 快速生成
result = quick_generate(
    "请介绍Python编程语言",
    provider="ollama",
    model="llama3.2:latest",
    temperature=0.7
)

# 快速聊天
messages = [
    {"role": "user", "content": "你好！"}
]
result = quick_chat(messages, provider="ollama", model="qwen2.5:latest")
```

### 异步使用

```python
import asyncio
from core.client import quick_generate_async

async def main():
    result = await quick_generate_async(
        "请介绍机器学习",
        provider="ollama", 
        model="llama3.2:latest"
    )
    print(result)

asyncio.run(main())
```

## 🛠️ 开发指南

### 添加新的模型提供商

1. 在`services/adapters/`目录下创建新的适配器文件
2. 继承`BaseModelAdapter`类
3. 实现必要的方法
4. 在`config/settings.py`中添加配置
5. 在`core/client.py`中注册新的适配器

### 添加新的优化策略

1. 在`templates/prompts.py`中添加新的提示词模板
2. 在`services/optimization.py`中实现优化逻辑
3. 在`config/settings.py`中注册新的优化类型

### 自定义UI组件

所有UI组件都在`components/`目录下，可以根据需要进行修改和扩展。

## 📊 监控和日志

### 日志配置

日志配置在`config/settings.py`中的`LogConfig`类中定义：

- 支持文件和控制台输出
- 可配置日志级别
- 支持日志轮转
- 记录API调用和用户操作

### 性能监控

应用内置了性能监控功能：

- API调用时间统计
- Token使用统计
- 内存使用监控
- 错误率统计

## 🔒 安全考虑

1. **API密钥安全**: 所有敏感信息都通过环境变量管理
2. **输入验证**: 对用户输入进行严格验证
3. **错误处理**: 完善的错误处理机制
4. **日志安全**: 避免在日志中记录敏感信息

## 🤝 贡献指南

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📝 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情

## 🆘 常见问题

### Q: 如何解决Ollama连接问题？

A: 
1. 确保Ollama服务正在运行：`ollama serve`
2. 检查端口是否正确（默认11434）
3. 确认防火墙设置
4. 查看日志文件获取详细错误信息

### Q: 如何添加新的AI模型？

A: 
1. 如果是Ollama模型：`ollama pull 模型名称`
2. 在`config/settings.py`中添加模型配置
3. 重启应用

### Q: 如何提高优化质量？

A: 
1. 选择合适的优化策略
2. 提供清晰具体的原始提示词
3. 根据任务场景选择合适的模型
4. 多次测试和迭代

## 📞 支持与反馈

- 问题反馈：请在GitHub Issues中提交
- 功能建议：欢迎通过Issues或Discussions讨论
- 文档问题：请提交PR或Issue

---

**享受AI提示词优化的乐趣！** 🚀
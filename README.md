# 提示词优化器

一个基于 Streamlit 的 AI 提示词优化和测试工具，帮助用户优化提示词并测试其效果。

## 功能特性

-  **智能优化**: 支持多种优化策略（通用、结构化、角色导向、任务导向等）
-  **对比测试**: 实时对比原始提示词和优化后提示词的效果
-  **性能指标**: 提供准确性、相关性、完整性等多维度评估
-  **友好界面**: 简洁直观的用户界面，操作简单
-  **模块化设计**: 便于扩展和二次开发

## 项目结构

```
prompt-optimizer/
├── main.py                 # 主应用入口
├── components/             # UI组件
│   ├── __init__.py
│   ├── prompt_optimizer.py # 提示词优化组件
│   └── test_panel.py      # 测试面板组件
├── services/              # 业务逻辑服务
│   ├── __init__.py
│   ├── optimization_service.py # 优化服务
│   └── test_service.py    # 测试服务
├── utils/                 # 工具函数
│   ├── __init__.py
│   ├── config.py         # 配置文件
│   └── helpers.py        # 辅助函数
├── requirements.txt       # 项目依赖
└── README.md             # 项目说明
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目（如果从git获取）
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

### 2. 创建必要的目录结构

```bash
mkdir components services utils logs
touch components/__init__.py services/__init__.py utils/__init__.py
```

### 3. 运行应用

```bash
streamlit run main.py
```

应用将在浏览器中打开，默认地址为 `http://localhost:8501`

## 使用指南

### 基础使用

1. **输入原始提示词**: 在左侧面板输入需要优化的提示词
2. **选择优化类型**: 选择合适的优化策略
3. **执行优化**: 点击"开始优化"按钮
4. **查看结果**: 在下方查看优化后的提示词
5. **测试对比**: 在右侧输入测试内容，对比两个提示词的效果

### 优化类型说明

- **通用优化**: 适用于大多数场景的通用优化策略
- **结构化优化**: 增加明确的结构和格式要求
- **角色导向优化**: 基于特定角色或身份进行优化
- **任务导向优化**: 针对特定任务目标进行优化

## 扩展开发

### 添加新的优化策略

1. 在 `services/optimization_service.py` 中添加新的优化方法
2. 在配置文件中注册新的优化类型
3. 更新UI组件以支持新选项

```python
def _custom_optimization(self, prompt: str, model: str) -> str:
    """自定义优化策略"""
    # 实现你的优化逻辑
    return optimized_prompt
```

### 集成外部API

1. 在 `services/` 目录下创建对应的API服务文件
2. 实现API调用逻辑
3. 在配置文件中添加API相关配置

### 添加新的评估指标

1. 在 `services/test_service.py` 中添加新的评估方法
2. 更新UI组件以显示新指标
3. 在配置文件中注册新指标

## 配置说明

主要配置项在 `utils/config.py` 中：

- `APP_CONFIG`: 应用基础配置
- `OPTIMIZATION_CONFIG`: 优化相关配置
- `TEST_CONFIG`: 测试相关配置
- `API_CONFIG`: API配置（预留）

## 注意事项

1. **API密钥**: 如需集成真实的AI模型API，请在环境变量中设置相应的API密钥
2. **性能**: 当前版本使用模拟数据，实际部署时需要集成真实的API服务
3. **安全**: 处理敏感数据时请注意数据安全和隐私保护

## 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 支持

如有问题或建议，请提交 Issue 或联系开发者。

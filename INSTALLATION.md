# 📦 安装指南

本文档将指导您完成提示词优化器的完整安装和配置过程。

## 📋 系统要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows 10+, macOS 10.14+, Linux
- **内存**: 建议 4GB 以上
- **磁盘空间**: 至少 2GB 可用空间

## 🚀 快速安装

### 1. 获取项目代码

```bash
# 方式一：从Git仓库克隆（如果有）
git clone <repository-url>
cd prompt-optimizer

# 方式二：下载并解压项目文件
# 下载项目压缩包并解压到本地目录
```

### 2. 创建项目目录结构

如果您是手动创建项目，请按照以下结构创建目录：

```bash
mkdir prompt-optimizer
cd prompt-optimizer

# 创建主要目录
mkdir config core services components utils templates logs
mkdir services/adapters

# 创建 __init__.py 文件
touch config/__init__.py
touch core/__init__.py  
touch services/__init__.py
touch services/adapters/__init__.py
touch components/__init__.py
touch utils/__init__.py
touch templates/__init__.py
```

### 3. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 4. 安装依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装核心依赖
pip install streamlit>=1.28.0 python-dotenv>=1.0.0 requests>=2.31.0

# 安装其他依赖（根据需要）
pip install pandas numpy openai anthropic aiohttp
```

### 5. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量文件
# Windows: notepad .env
# macOS/Linux: nano .env
```

## 🔧 详细配置

### Ollama 本地模型配置（推荐）

1. **安装 Ollama**

```bash
# Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# 从 https://ollama.ai 下载安装程序
```

2. **启动 Ollama 服务**

```bash
# 启动服务（在新终端窗口中运行）
ollama serve
```

3. **下载模型**

```bash
# 下载推荐的模型
ollama pull llama3.2          # 通用对话模型
ollama pull qwen2.5           # 中文优化模型
ollama pull codellama         # 代码专用模型

# 验证模型安装
ollama list
```

4. **配置环境变量**

在 `.env` 文件中设置：

```bash
# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=60
```

### OpenAI 配置（可选）

1. **获取 API 密钥**
   - 访问 [OpenAI Platform](https://platform.openai.com/)
   - 注册账户并获取 API 密钥

2. **配置环境变量**

```bash
# OpenAI 配置
OPENAI_API_KEY=sk-your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_TIMEOUT=60
```

### Anthropic Claude 配置（可选）

1. **获取 API 密钥**
   - 访问 [Anthropic Console](https://console.anthropic.com/)
   - 申请 API 访问权限

2. **配置环境变量**

```bash
# Anthropic 配置
ANTHROPIC_API_KEY=sk-ant-your_anthropic_api_key_here
ANTHROPIC_BASE_URL=https://api.anthropic.com
ANTHROPIC_TIMEOUT=60
```

## 🏃 运行应用

### 1. 验证安装

```bash
# 检查Python版本
python --version

# 检查已安装的包
pip list | grep streamlit

# 验证环境变量
python -c "from dotenv import load_dotenv; load_dotenv(); print('环境变量加载成功')"
```

### 2. 启动应用

```bash
# 确保在项目根目录中
pwd  # 应显示项目路径

# 启动 Streamlit 应用
streamlit run main.py
```

### 3. 访问应用

- 默认地址：`http://localhost:8501`
- 应用将自动在浏览器中打开

## 🔍 验证配置

### 检查模型连接

1. **Ollama 连接测试**

```bash
# 测试 Ollama 服务
curl http://localhost:11434/api/tags

# 应该返回已安装模型的列表
```

2. **OpenAI 连接测试**

```python
# 在Python中测试
import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 测试连接
try:
    response = client.models.list()
    print("OpenAI 连接成功")
except Exception as e:
    print(f"OpenAI 连接失败: {e}")
```

### 应用功能测试

1. 打开应用后，检查侧边栏是否显示可用模型
2. 尝试输入简单的提示词进行优化
3. 检查是否能正常显示优化结果

## 🐛 常见问题解决

### 问题 1: Ollama 连接失败

**症状**: 显示"无法连接到 Ollama 服务"

**解决方案**:
```bash
# 检查 Ollama 是否运行
ps aux | grep ollama

# 重启 Ollama 服务
ollama serve

# 检查端口是否被占用
lsof -i :11434  # macOS/Linux
netstat -ano | findstr :11434  # Windows
```

### 问题 2: Python 包导入错误

**症状**: `ModuleNotFoundError`

**解决方案**:
```bash
# 确保虚拟环境已激活
which python  # 应显示虚拟环境路径

# 重新安装依赖
pip install -r requirements.txt

# 检查 Python 路径
python -c "import sys; print(sys.path)"
```

### 问题 3: Streamlit 启动失败

**症状**: `streamlit: command not found`

**解决方案**:
```bash
# 确保 Streamlit 已安装
pip install streamlit

# 使用完整路径运行
python -m streamlit run main.py

# 检查 PATH 环境变量
echo $PATH
```

### 问题 4: 环境变量加载失败

**症状**: 配置无法正确加载

**解决方案**:
```bash
# 检查 .env 文件是否存在
ls -la .env

# 验证文件格式（不应有空格）
cat .env | head -5

# 手动加载测试
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('OLLAMA_BASE_URL:', os.getenv('OLLAMA_BASE_URL'))
"
```

## 🔄 更新升级

### 更新依赖包

```bash
# 更新所有包到最新版本
pip install --upgrade -r requirements.txt

# 更新特定包
pip install --upgrade streamlit
```

### 更新项目代码

```bash
# 如果使用Git
git pull origin main

# 手动更新
# 下载新版本文件并替换
```

## 🗑️ 卸载

```bash
# 停用虚拟环境
deactivate

# 删除虚拟环境
rm -rf venv

# 删除项目目录
cd ..
rm -rf prompt-optimizer
```

## 📞 获取帮助

如果遇到问题，可以：

1. **检查日志文件**: `logs/app.log`
2. **查看错误详情**: 在应用中启用调试模式
3. **提交问题**: 在项目仓库中创建 Issue
4. **查阅文档**: 参考 README.md 和其他文档

## 🔧 开发环境设置

如果您想参与开发，还需要安装开发工具：

```bash
# 安装开发依赖
pip install pytest black flake8 mypy

# 设置预提交钩子
pip install pre-commit
pre-commit install

# 运行测试
python -m pytest tests/

# 代码格式化
black .

# 代码检查
flake8 .
mypy .
```

恭喜！您已经成功完成了提示词优化器的安装和配置。现在可以开始使用这个强大的工具来优化您的AI提示词了！ 🎉
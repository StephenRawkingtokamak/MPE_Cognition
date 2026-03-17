# 🚀 快速开始指南

欢迎使用 MPE Cognition！本指南将帮助你在 5 分钟内开始使用。

## 📋 前置要求

- Python ≥ 3.8
- Git
- (可选) uv 包管理器

## 1️⃣ 克隆仓库

```bash
git clone https://github.com/StephenRawkingtokamak/MPE_Cognition
cd MPE_Cognition
```

## 2️⃣ 安装依赖

### 方法 A: 使用 uv (推荐)

```bash
# 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

uv pip install -e .
```

### 方法 B: 使用 pip

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

## 3️⃣ 配置 API 密钥 🔑

### 方式 A: 交互式配置（推荐）

```bash
python setup_api_keys.py
```

该脚本会引导你输入 API 密钥并自动生成 `.env` 文件。

### 方式 B: 手动配置

```bash
# 1. 复制模板
cp .env.example .env

# 2. 编辑 .env 文件，填入你的实际密钥
nano .env
```

### 方式 C: 环境变量

```bash
# 选择你使用的 LLM 服务

# OpenAI / DeepSeek / Qwen
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.deepseek.com"  # 可选

# Google Gemini
export GEMINI_API_KEY="your-api-key"
```

或者直接在代码中设置：
```python
MY_KEY = "your-api-key"
MY_URL = "https://api.provider.com/v1"
MY_MODEL = "model-name"
```

## 4️⃣ 运行你的第一个示例

### 示例 1: 观测解析验证

```bash
# 验证 Simple Adversary 环境的观测解析
python obs/parse_adv_obs.py
```

**你会看到**:
- 📚 观测空间的语义说明
- ✅ 维度验证结果
- 📋 解析后的 JSON 格式
- 💡 关键信息摘要

### 示例 2: 观测解析使用示例

```bash
# 查看如何在代码中使用解析器
python obs/example_usage.py
```

**你会看到**:
- 基础用法示例
- 游戏循环中的使用
- 如何构建 LLM Prompt
- 不同角色的观测对比

### 示例 3: 运行完整的游戏 Episode

```bash
# 运行 Simple Spread 环境（需要配置 API 密钥）
python spread_API.py

# 运行 Simple Adversary 环境
python adv_API.py
```

**将生成**:
- 📹 游戏视频 (MP4 格式)
- 📄 详细日志 (JSON 格式)
- 📊 性能统计

## 5️⃣ 探索项目

### 查看文档

```bash
# 项目整体概览
cat PROJECT_OVERVIEW.md

# 观测解析开发指南
cat OBS_PARSING_GUIDE.md

# obs 目录使用说明
cat obs/README.md

# 已完成工作总结
cat WORK_SUMMARY.md
```

### 查看代码结构

```bash
tree -L 2 --filesfirst -I '__pycache__|*.pyc|.git'
```

## 📁 重要文件说明

| 文件 | 说明 |
|------|------|
| `spread_API.py` | Simple Spread 环境主程序 |
| `adv_API.py` | Simple Adversary 环境主程序 |
| `tag_API.py` | Simple Tag 环境主程序 |
| `utils_api.py` | LLM API 调用工具 |
| `obs/parse_adv_obs.py` | 观测解析器示例 |
| `obs/utils.py` | 通用辅助函数 |
| `requirements.txt` | Python 依赖列表 |
| `pyproject.toml` | 项目配置文件 |

## 🎯 下一步

### 对于研究者
1. 阅读 [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) 了解项目架构
2. 修改 Prompt 工程尝试不同策略
3. 对比不同 LLM 的性能

### 对于开发者
1. 阅读 [OBS_PARSING_GUIDE.md](OBS_PARSING_GUIDE.md)
2. 为其他环境实现解析器
3. 贡献新功能或改进

### 对于学习者
1. 运行所有示例代码
2. 阅读 `obs/example_usage.py` 了解用法
3. 参考 `parse_adv_obs.py` 学习解析器实现

## ❓ 常见问题

### Q1: ModuleNotFoundError: No module named 'pettingzoo'
**A**: 你需要先安装依赖。运行：
```bash
pip install -r requirements.txt
```

### Q2: 如何切换不同的 LLM 模型？
**A**: 修改主程序中的配置：
```python
MY_MODEL = "qwen3-max"  # 或 "gpt-4", "gemini-pro" 等
```

### Q3: 视频文件在哪里？
**A**: 视频和日志保存在项目根目录，文件名类似：
- `spread_demo_run_1.mp4`
- `spread_demo_run_1.json`

### Q4: 如何调试观测解析？
**A**: 使用 `obs/utils.py` 中的调试函数：
```python
from obs.utils import print_raw_observation

segments = [("速度", 2), ("位置", 2), ("地标", 4)]
print_raw_observation(obs, agent_id, segments)
```

### Q5: 如何添加新环境？
**A**: 参考 [OBS_PARSING_GUIDE.md](OBS_PARSING_GUIDE.md) 的实现步骤。

## 🆘 获取帮助

- 📖 查看文档: `PROJECT_OVERVIEW.md`, `OBS_PARSING_GUIDE.md`
- 💬 提交 Issue: [GitHub Issues](https://github.com/StephenRawkingtokamak/MPE_Cognition)
- 📧 联系作者: StephenRawkingtokamak

## 🎉 开始你的旅程！

```bash
# 激活环境
source .venv/bin/activate

# 运行第一个示例
python obs/parse_adv_obs.py

# 查看更多示例
python obs/example_usage.py

# 运行完整游戏 (需要 API 密钥)
python spread_API.py
```

祝你使用愉快！🚀

---

**最后更新**: 2026-01-24  
**项目地址**: https://github.com/StephenRawkingtokamak/MPE_Cognition

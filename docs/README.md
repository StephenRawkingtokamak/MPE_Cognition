# 📚 文档导航

欢迎来到 MPE Multi-Agent Benchmark 项目文档中心！

---

## 📖 入门指南

刚接触本项目？从这里开始：

| 文档 | 说明 | 适合人群 |
|-----|------|---------|
| [快速开始](getting_started/quickstart.md) | 5分钟上手运行第一个实验 | 新用户 |
| [环境配置](getting_started/environment_setup.md) | 详细的环境搭建和依赖安装指南 | 所有人 |
| [依赖管理](getting_started/dependency_management.md) | requirements.txt vs requirements.lock | 开发者 |
| [项目概览](getting_started/overview.md) | 了解项目的设计理念和核心架构 | 所有人 |

---

## ⚙️ 配置说明

如何配置和使用本项目：

| 文档 | 说明 |
|-----|------|
| [API 密钥配置](configuration/api_keys.md) | OpenAI/Qwen/DeepSeek 等 LLM 的 API 密钥安全管理 |

---

## 🏗️ 架构与设计

深入理解系统内部原理：

| 文档 | 说明 | 关键概念 |
|-----|------|---------|
| [观察空间解析](architecture/observation_space.md) | 如何将 PettingZoo 的向量观察转换为 JSON | 观察解析器、坐标系统 |
| [日志系统](architecture/logging_system.md) | 完整的日志格式规范和案例 | step-by-step 日志、final_summary |
| [模型使用指南](architecture/models.md) | 支持的 7 种 LLM 提供商和调用方式 | API 引擎、多模型支持 |

---

## 🧪 实验与测试

运行实验、复现结果、分析数据：

| 文档 | 说明 | 核心功能 |
|-----|------|---------|
| [可重现实验](experiments/reproducibility.md) | 使用 seed 参数确保结果可复现 | 固定种子 (1~20) |
| [基准测试指南](experiments/running_benchmarks.md) | 如何批量运行 10+ 轮实验并分析结果 | benchmark_runner.py |
| [基准测试评估](experiments/benchmark_review.md) | 多角色游戏的日志分析和陷阱 | 多智能体环境的特殊性 |

---

## 🛠️ 开发者笔记

历史记录与开发过程资产：

| 文档 | 说明 |
|-----|------|
| [工作总结](dev_notes/work_summary.md) | v1.0 完整开发历程和功能清单 |
| [工作流标准化](dev_notes/workflow_standardization.md) | prompt/obs 模块化设计原则 |
| [API 密钥重构](dev_notes/api_keys_refactor.md) | API 密钥从硬编码到环境变量的迁移日志 |

---

## 🎯 按任务分类

### 我想开始运行实验
1. [快速开始](getting_started/quickstart.md) - 安装依赖
2. [API 密钥配置](configuration/api_keys.md) - 设置 API 密钥
3. [基准测试指南](experiments/running_benchmarks.md) - 批量运行实验

### 我想理解系统设计
1. [项目概览](getting_started/overview.md) - 整体架构
2. [观察空间解析](architecture/observation_space.md) - 观察空间处理
3. [工作流标准化](dev_notes/workflow_standardization.md) - 模块化设计

### 我想复现论文结果
1. [可重现实验](experiments/reproducibility.md) - 种子固定
2. [基准测试指南](experiments/running_benchmarks.md) - 批量实验
3. [日志系统](architecture/logging_system.md) - 结果分析

### 我想贡献代码
1. [工作流标准化](dev_notes/workflow_standardization.md) - 代码规范
2. [观察空间解析](architecture/observation_space.md) - 新环境接入
3. [模型使用指南](architecture/models.md) - 新模型接入

---

## 📂 文档结构

```
docs/
├── README.md                        # 本文档（导航索引）
├── getting_started/                 # 入门指南
│   ├── quickstart.md                # 快速开始
│   └── overview.md                  # 项目概览
├── configuration/                   # 配置文档
│   └── api_keys.md                  # API 密钥管理
├── architecture/                    # 架构设计
│   ├── observation_space.md         # 观察空间解析
│   ├── logging_system.md            # 日志系统
│   └── models.md                    # 模型使用
├── experiments/                     # 实验指南
│   ├── reproducibility.md           # 可重现实验
│   ├── running_benchmarks.md        # 基准测试
│   └── benchmark_review.md          # 评估分析
└── dev_notes/                       # 开发笔记
    ├── work_summary.md              # 工作总结
    ├── workflow_standardization.md  # 工作流标准化
    └── api_keys_refactor.md         # 重构日志
```

---


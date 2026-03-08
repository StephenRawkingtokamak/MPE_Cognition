# Embodied-MPE: 基于 DeepSeek 的具身大模型演进规律与智能增强研究

![LaTeX](https://img.shields.io/badge/Layout-LaTeX-blue) ![DeepSeek](https://img.shields.io/badge/Intelligence-DeepSeek--V3%2FR1-orange) ![Field](https://img.shields.io/badge/Field-Embodied--AI-green)

> **研究定论**：在具身智能领域，经典控制先验并未淘汰，而是成为了锚定大模型“具身幻觉”的关键压舱石。本项目界定了现有架构下语义逻辑与物理积分碰撞的 **0.3s 物理红线**。

## 📖 项目概述
本项目以多智能体粒子环境（MPE）为实证平台，系统性地揭示了大语言模型（LLM）在处理连续动力学任务时的性能演进路径。通过 DeepSeek-V3/R1 驱动的智力中枢，探索模型在复杂动态物理环境中的行为演变与控制精度边界。

## 🧠 核心架构：智力中枢与工程落地
本项目放弃了传统的端到端强化学习，采用层次化的架构实现从语义到动作的映射：

### 1. 状态语义化引擎 (State Interpretation Module)
将 MPE 的连续浮点观测向量转译为富含语义的空间关系文本：
* **方位转译**：将坐标转换为以智能体为原点的八向方位词。
* **动能状态**：计算相对运动趋势而非原始速度。
* **角色设定**：将冰冷的数字 ID 映射为具有社会属性的实体名词（如“捕食者”、“同盟听众”）。

### 2. 层次化提示词工程 (Prompt Engineering)
构建了从 **系统本体论** 到 **动作格式化** 的四层架构，确保模型在长轮次交互中维持目标专注度：
* **System Prompt**: 宣告二维空间属性与物理法则。
* **Role Prompt**: 注入 MPE 场景逻辑与社会身份。
* **Observation Context**: 注入语义化状态文本。
* **Action Formatting**: 强制 JSON 格式输出思考过程（CoT）与决策。

## 🔬 具身演进的瓶颈剖析
研究发现 LLM 在底层物理交互中存在两大核心瓶颈：
1. **时间盲点 (Temporal Blindspot)**：离散 Token 预测步频（~1.5s）与物理积分步频（0.1s）的非对称性导致决策滞后。
2. **动能幻觉 (Kinetic Illusion)**：缺乏对冲量和摩擦力的直观建模，导致严重的惯性过冲（Inertial Overshoot）与震荡。

[Image of autonomous agent experiencing kinetic illusion and inertial overshoot in physical environment]

## 🛠️ 增强算法实现

### A. 势能奖励重构 (PBRS) 与策略不变性
为了引导模型感知动量风险，引入包含动量感知项的势函数 $\Phi(s)$：
$$\Phi(s)=-\lambda_{1}||p_{agent}-p_{target}||-\lambda_{2}\cdot max(0,\vec{V}_{agent}\cdot\vec{d}_{target})$$
本研究基于 **Ng et al. (1999)** [^1] 的理论从数学上证明了 PBRS 在增强物理感知的过程中，逻辑上始终对齐原始任务的最优解。

### B. 基于控制变量 (Control Variates) 的方差削减
在 `Push Ball` 协作任务中，针对物理碰撞产生的强非平稳噪声，引入“确定性基准轨迹”优化 Advantage 函数估计：
* **数学降噪**：新估计量的方差满足 $Var(\hat{A})=(1-\rho^{2})Var(A_{raw})$。
* **自适应权重**：基于推球策略余

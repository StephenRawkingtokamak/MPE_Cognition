# MPE 环境观测解析标准化指南

## 📋 概述

本指南定义了一套**标准化的观测解析流程**，用于将 PettingZoo MPE 环境的原始观测向量转换为结构化的 JSON 格式。这套流程适用于所有 9 个 MPE 游戏环境。

## 🎯 目标

1. **语义化**: 将低维数值向量映射为人类可读的语义信息
2. **结构化**: 输出标准的 JSON 格式，便于 LLM 理解和使用
3. **可验证**: 提供维度检查和正确性验证
4. **可复用**: 统一的代码模式，易于扩展到所有环境

## 🏗️ 标准化流程

### 阶段 1: 观测空间探测 (Observation Probing)

**目的**: 确定观测向量的维度和结构

```python
# 示例: obs_<env_name>.py
from pettingzoo.mpe import <environment>
import numpy as np

env = <environment>.parallel_env(...)
obs, _ = env.reset()

for agent_id, data in obs.items():
    print(f"Agent: {agent_id}")
    print(f"  Shape: {data.shape}")
    print(f"  Data: {np.round(data, 2)}")
```

**输出**: 每个智能体的观测维度和原始数据

### 阶段 2: 观测语义映射 (Semantic Mapping)

**目的**: 确定每个维度的语义含义

**方法**:
1. 查阅环境源代码或文档
2. 通过多次 reset 观察数据变化规律
3. 移动智能体验证坐标系统
4. 记录每个维度的物理意义

**示例**: Simple Adversary 环境

| 维度范围 | 语义含义 | 数据类型 | 说明 |
|---------|---------|---------|------|
| 0-1 (Adv) | Landmark 0 相对坐标 | (x, y) | 相对于自己的位置 |
| 2-3 (Adv) | Landmark 1 相对坐标 | (x, y) | 第二个地标 |
| 4-5 (Adv) | Good Agent 0 相对坐标 | (x, y) | 第一个友方 |
| ... | ... | ... | ... |

### 阶段 3: 解析器实现 (Parser Implementation)

**标准结构**:

```python
def parse_<env_name>_obs(obs: np.ndarray, agent_id: str, **kwargs) -> Dict[str, Any]:
    """
    解析 <环境名> 的观测向量
    
    参数:
        obs: 原始观测向量 (numpy array)
        agent_id: 智能体ID
        **kwargs: 环境特定参数 (如 num_good, num_landmarks 等)
    
    返回:
        结构化的观测字典 (JSON 可序列化)
    """
    data = obs.tolist() if isinstance(obs, np.ndarray) else obs
    struct = {}
    
    # 1. 基础信息
    struct['agent_id'] = agent_id
    struct['role'] = determine_role(agent_id)  # 根据ID判断角色
    struct['description'] = "角色描述"
    
    # 2. 解析各个部分 (使用指针逐步读取)
    ptr = 0
    
    # 示例: 解析速度
    struct['velocity'] = {
        'x': round(data[ptr], 2),
        'y': round(data[ptr+1], 2),
        'speed': round(math.sqrt(data[ptr]**2 + data[ptr+1]**2), 2)
    }
    ptr += 2
    
    # 示例: 解析地标列表
    struct['landmarks'] = []
    for i in range(num_landmarks):
        dx, dy = data[ptr], data[ptr+1]
        dist = math.sqrt(dx**2 + dy**2)
        struct['landmarks'].append({
            'id': i,
            'relative_position': [round(dx, 2), round(dy, 2)],
            'distance': round(dist, 2),
            'direction': get_direction(dx, dy),  # UP/DOWN/LEFT/RIGHT
            'description': f"地标 {i} 在{get_direction(dx, dy)}，距离 {round(dist, 2)}"
        })
        ptr += 2
    
    # 3. 添加战术提示 (可选，但推荐)
    struct['tactical_hint'] = generate_tactical_hint(struct)
    
    return struct
```

### 阶段 4: 验证器实现 (Validator Implementation)

**目的**: 确保解析器正确性

```python
def verify_obs_structure(env_params: Dict) -> None:
    """
    验证观测空间的结构和维度
    """
    # 1. 初始化环境
    env = create_env(**env_params)
    obs, _ = env.reset()
    
    # 2. 验证维度
    for agent_id, data in obs.items():
        expected_dim = calculate_expected_dim(agent_id, env_params)
        actual_dim = len(data)
        assert actual_dim == expected_dim, f"维度不匹配: {actual_dim} != {expected_dim}"
    
    # 3. 验证解析器
    for agent_id, data in obs.items():
        parsed = parse_obs(data, agent_id, **env_params)
        
        # 打印 JSON
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
        
        # 验证关键字段存在
        assert 'agent_id' in parsed
        assert 'role' in parsed
        # ... 更多验证
    
    env.close()
```

## 📦 JSON 输出格式标准

### 必需字段

所有环境的解析器必须包含以下字段：

```json
{
  "agent_id": "agent_0",
  "role": "ROLE_NAME",
  "description": "角色的简短描述",
  "raw_observation": [0.1, 0.2, ...],  // 可选: 保留原始数据
  "tactical_hint": "基于当前观测的战术建议"
}
```

### 环境特定字段

根据环境添加特定的结构化信息：

```json
{
  // 位置类信息
  "landmarks": [
    {
      "id": 0,
      "relative_position": [0.5, 0.3],
      "distance": 0.58,
      "direction": "UP-RIGHT",
      "description": "地标 0 在东北方向，距离 0.58"
    }
  ],
  
  // 其他智能体信息
  "other_agents": [
    {
      "id": "agent_1",
      "relative_position": [-0.2, 0.1],
      "distance": 0.22,
      "direction": "LEFT",
      "description": "队友在左侧，距离 0.22"
    }
  ],
  
  // 物理状态
  "velocity": {
    "x": 0.1,
    "y": -0.05,
    "speed": 0.11
  },
  
  // 通信信息 (如果有)
  "communication": {
    "received_message": [0.2, 0.5, 0.3],
    "decoded_meaning": "目标是地标 1"
  }
}
```

## 🎮 9 个 MPE 环境的解析任务

### 1. Simple Spread ✅
- **文件**: `obs/parse_spread_obs.py`
- **关键观测**: 速度、自身位置、地标位置、其他智能体位置
- **角色**: 无角色区分，所有智能体相同
- **难点**: 需要计算哪个地标未被占据

### 2. Simple Adversary ✅ (已完成示例)
- **文件**: `obs/parse_adv_obs.py`
- **关键观测**: 
  - 敌方: 地标位置、友方位置
  - 友方: 目标地标、所有地标、敌方位置、队友位置
- **角色**: Adversary vs Good Agents
- **难点**: 友方需要识别哪个地标是目标

### 3. Simple Tag
- **文件**: `obs/parse_tag_obs.py`
- **关键观测**: 障碍物位置、猎物/捕食者位置
- **角色**: Predator (多个) vs Prey (1个)
- **难点**: 障碍物的处理、边界约束

### 4. Simple Push
- **文件**: `obs/parse_push_obs.py`
- **关键观测**: 地标位置、目标位置、对手位置
- **角色**: Adversary vs Good Agent
- **难点**: 需要理解"推动"物理操作

### 5. Simple Crypto
- **文件**: `obs/parse_crypto_obs.py`
- **关键观测**: 
  - Alice: 目标消息、私钥
  - Bob: 私钥、接收到的密文
  - Eve: 截获的密文
- **角色**: Alice, Bob, Eve (三方博弈)
- **难点**: 观测空间完全不同，需要分别处理

### 6. Simple Reference
- **文件**: `obs/parse_reference_obs.py`
- **关键观测**: 速度、地标位置+颜色、目标颜色编码
- **角色**: 无明确角色，但需要协作
- **难点**: 颜色编码的解析 (RGB → 颜色名称)

### 7. Simple Speaker Listener
- **文件**: `obs/parse_speaker_obs.py`
- **关键观测**:
  - Speaker: 目标地标的 One-Hot 向量
  - Listener: 速度、地标位置、通信信号
- **角色**: Speaker vs Listener
- **难点**: One-Hot 解码、通信信号的解析

### 8. Simple World Comm
- **文件**: `obs/parse_world_comm_obs.py`
- **关键观测**: 速度、位置、地标(食物/森林/障碍物)、其他智能体、通信信号
- **角色**: Leader vs Follower
- **难点**: 观测空间最复杂，多种地标类型

### 9. Simple (Basic)
- **文件**: `obs/parse_simple_obs.py`
- **关键观测**: 速度、地标位置、其他智能体位置
- **角色**: 无角色区分
- **难点**: 与 Spread 类似但更简单

## 🛠️ 实现步骤 (针对每个环境)

### Step 1: 创建探测脚本
```bash
# 文件名: obs/obs_<env_name>.py
```

**内容**:
```python
from pettingzoo.mpe import <environment_v3>
import numpy as np

env = <environment_v3>.parallel_env(...)
obs, _ = env.reset()

print(f"=== {env_name} Observation Probe ===")
for agent_id, data in obs.items():
    print(f"\nAgent: {agent_id}")
    print(f"  Shape: {data.shape}")
    print(f"  Data: {np.round(data, 2)}")
```

### Step 2: 分析观测结构

运行探测脚本，记录：
1. 每个智能体的观测维度
2. 不同 reset 下的数据变化
3. 推断每个维度的语义

### Step 3: 实现解析器

```bash
# 文件名: obs/parse_<env_name>_obs.py
```

**内容**: 包含以下函数
- `parse_<env_name>_obs()`: 核心解析器
- `verify_obs_structure()`: 验证器
- `print_observation_semantics()`: 语义说明

### Step 4: 验证正确性

```python
# 运行验证器
python obs/parse_<env_name>_obs.py
```

**检查项**:
- [ ] 维度匹配
- [ ] JSON 格式正确
- [ ] 所有字段有意义
- [ ] 方向计算正确 (通过移动智能体验证)

### Step 5: 集成到主代码

将解析器导入到主 API 文件 (`<env_name>_API.py`):

```python
from obs.parse_<env_name>_obs import parse_<env_name>_obs

# 在主循环中使用
for agent_id in env.agents:
    obs_raw = observations[agent_id]
    obs_struct = parse_<env_name>_obs(obs_raw, agent_id, **env_params)
    # 用于构建 prompt
```

## 📐 辅助函数库

建议在 `obs/utils.py` 中创建通用辅助函数：

```python
# obs/utils.py
import math
from typing import Tuple, List

def get_distance(dx: float, dy: float) -> float:
    """计算欧几里得距离"""
    return math.sqrt(dx**2 + dy**2)

def get_direction(dx: float, dy: float, threshold: float = 0.1) -> str:
    """
    根据相对坐标返回主要方向
    
    返回: UP, DOWN, LEFT, RIGHT, UP-LEFT, UP-RIGHT, DOWN-LEFT, DOWN-RIGHT, CENTER
    """
    if abs(dx) < threshold and abs(dy) < threshold:
        return "CENTER"
    
    # 主方向
    h_dir = "RIGHT" if dx > threshold else "LEFT" if dx < -threshold else ""
    v_dir = "UP" if dy > threshold else "DOWN" if dy < -threshold else ""
    
    if h_dir and v_dir:
        return f"{v_dir}-{h_dir}"
    return v_dir or h_dir or "CENTER"

def round_vector(vec: List[float], decimals: int = 2) -> List[float]:
    """向量取整"""
    return [round(x, decimals) for x in vec]

def normalize_vector(vec: List[float]) -> List[float]:
    """向量归一化"""
    mag = math.sqrt(sum(x**2 for x in vec))
    if mag < 1e-6:
        return vec
    return [x / mag for x in vec]

def parse_one_hot(vec: List[float]) -> int:
    """解析 One-Hot 向量"""
    return int(max(range(len(vec)), key=lambda i: vec[i]))

def rgb_to_color_name(rgb: List[float]) -> str:
    """
    将 RGB 向量转换为颜色名称
    
    常见颜色:
    [1, 0, 0] -> RED
    [0, 1, 0] -> GREEN
    [0, 0, 1] -> BLUE
    """
    r, g, b = rgb
    if r > g and r > b:
        return "RED"
    elif g > r and g > b:
        return "GREEN"
    elif b > r and b > g:
        return "BLUE"
    elif r > 0.5 and g > 0.5:
        return "YELLOW"
    elif g > 0.5 and b > 0.5:
        return "CYAN"
    elif r > 0.5 and b > 0.5:
        return "MAGENTA"
    else:
        return "UNKNOWN"
```

## 📊 质量检查清单

对每个解析器进行以下检查：

### 功能性
- [ ] 解析器能正确处理所有智能体类型
- [ ] 输出的 JSON 可被 `json.dumps()` 序列化
- [ ] 所有必需字段都存在
- [ ] 数值精度合理 (通常保留 2 位小数)

### 正确性
- [ ] 维度验证通过 (expected == actual)
- [ ] 方向计算正确 (通过手动测试验证)
- [ ] 距离计算正确
- [ ] 特殊情况处理 (如除零、边界值)

### 可用性
- [ ] 有详细的文档字符串
- [ ] 打印清晰的验证输出
- [ ] 包含语义说明函数
- [ ] 提供战术建议 (tactical_hint)

### 代码质量
- [ ] 符合 PEP 8 风格
- [ ] 变量命名清晰
- [ ] 适当的注释
- [ ] 无硬编码常量 (使用参数)

## 🚀 批量处理脚本

创建一个主验证脚本 `obs/verify_all_envs.py`:

```python
"""
批量验证所有环境的观测解析器
"""

from parse_spread_obs import verify_obs_structure as verify_spread
from parse_adv_obs import verify_obs_structure as verify_adv
from parse_tag_obs import verify_obs_structure as verify_tag
# ... 导入所有其他验证器

def verify_all_environments():
    """运行所有环境的验证"""
    
    envs = [
        ("Simple Spread", verify_spread, {'N': 3}),
        ("Simple Adversary", verify_adv, {'num_good': 2}),
        ("Simple Tag", verify_tag, {'num_good': 1, 'num_adversaries': 3}),
        # ... 添加所有环境
    ]
    
    results = {}
    
    for env_name, verify_func, params in envs:
        print(f"\n{'='*80}")
        print(f"Testing: {env_name}")
        print(f"{'='*80}")
        
        try:
            verify_func(**params)
            results[env_name] = "✅ PASS"
            print(f"\n✅ {env_name} 验证通过\n")
        except Exception as e:
            results[env_name] = f"❌ FAIL: {str(e)}"
            print(f"\n❌ {env_name} 验证失败: {e}\n")
    
    # 打印汇总
    print(f"\n{'='*80}")
    print("验证汇总:")
    print(f"{'='*80}")
    for env, result in results.items():
        print(f"{env:30s} {result}")

if __name__ == "__main__":
    verify_all_environments()
```

## 📝 使用示例

### 在 LLM API 中使用

```python
# 在 xxx_API.py 中
from obs.parse_xxx_obs import parse_xxx_obs

def run_episode(...):
    for step in range(max_steps):
        for agent_id in env.agents:
            # 1. 获取原始观测
            obs_raw = observations[agent_id]
            
            # 2. 解析为 JSON
            obs_struct = parse_xxx_obs(obs_raw, agent_id, **env_params)
            
            # 3. 构建 prompt (使用结构化信息)
            prompt = build_prompt(agent_id, step, obs_struct)
            
            # 4. LLM 推理
            action, thought = llm_engine.generate_action(system_prompt, prompt)
```

### 在 Prompt 中使用

```python
def build_prompt(agent_id: str, step: int, obs: Dict) -> str:
    return f"""
AGENT: {obs['agent_id']}
ROLE: {obs['role']}
STEP: {step}

CURRENT SITUATION:
{obs['description']}

OBSERVATIONS:
{json.dumps(obs, indent=2, ensure_ascii=False)}

TACTICAL ADVICE:
{obs['tactical_hint']}

YOUR ACTION:
[输出动作向量]
"""
```

## 🎓 最佳实践

1. **先探测，再解析**: 总是先用探测脚本确认维度，再实现解析器
2. **保留原始数据**: 在 JSON 中保留 `raw_observation` 字段便于调试
3. **添加语义描述**: 每个字段都加 `description` 帮助 LLM 理解
4. **计算辅助信息**: 不仅解析坐标，还要计算距离、方向等
5. **提供战术建议**: `tactical_hint` 字段给出当前局势的建议
6. **统一坐标系**: 在文档中明确说明坐标系定义
7. **版本控制**: 在代码中注明环境版本 (如 v3)
8. **单元测试**: 为解析器编写测试用例

## 📚 参考资源

- [PettingZoo MPE 文档](https://pettingzoo.farama.org/environments/mpe/)
- [MPE 源代码](https://github.com/Farama-Foundation/PettingZoo/tree/master/pettingzoo/mpe)
- 本项目示例: `obs/parse_adv_obs.py`

## 🔄 更新日志

- **2026-01-24**: 初始版本，完成 Simple Adversary 示例
- **待完成**: 其余 8 个环境的解析器

---

**最后更新**: 2026-01-24

from typing import Dict, Any

def user_prompt(agent: str, step_idx: int, obs_struct: Dict[str, Any], num_agents: int, local_ratio: float) -> str:
    # 读取 spread_API.py 注入的精确距离
    dist = obs_struct.get('precise_dist', 9.9)
    rel = obs_struct.get('landmark_rel', [[0.0, 0.0]])[0]
    dx, dy = rel[0], rel[1]

    # 0.5 锁定逻辑：一旦进入 0.52 范围（预留 0.02 惯性），立即停止
    if dist <= 0.52:
        action_str = "[0.0, 0.0, 0.0, 0.0, 0.0]"
        notes = "ZONE_LOCKED"
    else:
        # 极简方向控制
        a1 = 1.0 if dx < -0.01 else 0.0 # Left
        a2 = 1.0 if dx > 0.01 else 0.0  # Right
        a3 = 1.0 if dy < -0.01 else 0.0 # Down
        a4 = 1.0 if dy > 0.01 else 0.0  # Up
        action_str = f"[0.0, {a1}, {a2}, {a3}, {a4}]"
        notes = "HIGH_SPEED_APPROACH"

    header = f"AGENT: {agent} | STEP: {step_idx} | DIST: {dist}"
    
    # 强制模型输出
    response_format = (
        "\n### OUTPUT JSON ###\n"
        '{"action": ' + action_str + ', "notes": "' + notes + '"}'
    )

    return f"{header}\n{response_format}"

# 兼容性存根
def get_task_and_reward(n=None, r=None): return ""
def get_action_and_response_format(): return ""
def get_physics_rules(): return ""
def get_navigation_hints(): return ""
__all__ = ["user_prompt", "get_task_and_reward", "get_action_and_response_format", "get_physics_rules", "get_navigation_hints"]
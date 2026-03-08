import numpy as np
import imageio
import json
from typing import Dict, Any

# 1. 导入我们剥离出去的通用工具
# 确保 utils_api.py 在同一目录下
from utils_api import get_api_engine, get_unique_filename
from prompt.prompt_for_tag import (
    get_action_and_response_format,
    get_navigation_hints,
    get_physics_rules,
    get_task_and_reward,
)
from obs.parse_tag_obs import parse_tag_obs

# 2. 导入 Tag 环境
try:
    from pettingzoo.mpe import simple_tag_v3
except ImportError:
    raise ImportError("请安装 pettingzoo: pip install pettingzoo[mpe]")

def get_header(env_name: str, agent_name: str, step: int, role: str) -> str:
    return (
        f"ENV: {env_name}\n"
        f"AGENT: {agent_name}\n"
        f"ROLE: {role.upper()}\n"
        f"STEP: {step}"
    )

# 设定运行次数
N_EPISODES = 5
# Tag 环境标准配置
NUM_GOOD = 1        # 猎物数量
NUM_ADV = 3         # 捕食者数量
NUM_OBS = 2         # 障碍物数量
MAX_STEPS = 30      # 追逐通常需要长一点时间

def _format_current_obs(obs_struct: Dict[str, Any], is_predator: bool, num_obstacles: int) -> str:
    obs_semantics = (
        "OBSERVATION SEMANTICS:\n"
        f"- obs = [self_vel, self_pos, obstacles_rel({num_obstacles}), other_agents...]\n"
        "- obstacles_rel: Relative position of grey rocks (impassable).\n"
    )
    if is_predator:
        obs_semantics += "- other_agents: LAST item is the PREY (target); others are PREDATOR teammates.\n\n"
    else:
        obs_semantics += "- other_agents: All items are PREDATORS (threats).\n\n"
    
    return (
        obs_semantics +
        "CURRENT OBS (Structured):\n"
        f"{json.dumps(obs_struct)}\n"
        "- self_vel: [vx, vy]\n"
        "- self_pos: [x, y]\n"
        "- obstacles_rel: [dx, dy, dist]\n"
        "- enemies / teammates: [dx, dy, dist]\n"
    )


def user_prompt_tag(agent: str, step: int, obs: Dict[str, Any], is_predator: bool, num_obstacles: int) -> str:
    role_name = "PREDATOR" if is_predator else "PREY"
    parts = [
        get_header("MPE_Simple_Tag_v3", agent, step, role_name),
        get_task_and_reward(is_predator),
        get_physics_rules(),
        get_action_and_response_format(),
        get_navigation_hints(is_predator),
        _format_current_obs(obs, is_predator, num_obstacles),
    ]
    return "\n\n".join(parts)

# ============================================================================== 
# 2. 主流程
# ============================================================================== 
def run_tag_game(provider: str, output_name: str, **kwargs):
    """
    运行 Tag 游戏
    
    Args:
        provider: 模型提供商 ('qwen', 'deepseek', 'gpt', 'ollama', 'transformers', etc.)
        output_name: 输出文件名前缀
        **kwargs: 传递给 get_api_engine 的额外参数
    """

    

    # 初始化 API
    seed = kwargs.pop('seed', None)
    llm_engine = get_api_engine(provider, **kwargs)
    print(f"Initializing Tag Env (Prey={NUM_GOOD}, Pred={NUM_ADV})...")
    env = simple_tag_v3.parallel_env(
        num_good=NUM_GOOD, 
        num_adversaries=NUM_ADV, 
        num_obstacles=NUM_OBS, 
        max_cycles=MAX_STEPS, 
        continuous_actions=True, 
        render_mode="rgb_array"
    )
    
    observations, infos = env.reset(seed=seed) if seed is not None else env.reset()
    frames = []
    game_log = []
    
    # 记录总分 (Tag环境是零和博弈，分别记录)
    total_reward_prey = 0.0
    total_reward_pred = 0.0

    for step in range(MAX_STEPS):
        print(f"\n=== STEP {step} ===")
        frame = env.render()
        if frame is not None: frames.append(frame)
        
        actions = {}
        step_records = {}

        # --- 1. 决策循环 ---
        for agent_id in env.agents:
            obs_raw = observations[agent_id]
            print(obs_raw)
            is_predator = "adversary" in agent_id

            # A. 解析观测
            obs_struct = parse_tag_obs(obs_raw, agent_id, NUM_OBS, NUM_GOOD, NUM_ADV)
            print(f"  Agent: {agent_id} | Role: {'PREDATOR' if is_predator else 'PREY'} | Obs: {obs_struct}")
            # B. 生成 Prompt (核心差异点)
            full_prompt = user_prompt_tag(agent_id, step, obs_struct, is_predator, NUM_OBS)
            
            # C. 调用 API
            system_role = "You are a Hunter." if is_predator else "You are the Prey."
            action_vec, raw_thought = llm_engine.generate_action(system_role, full_prompt)
            
            # D. 限幅 & 存储
            action_vec = np.clip(action_vec, 0.0, 1.0)
            actions[agent_id] = action_vec
            
            role_label = "[WOLF]" if is_predator else "[SHEEP]"
            print(f"  {role_label} {agent_id} Action: {np.round(action_vec, 2)}")
            
            # E. 日志
            step_records[agent_id] = {
                "step": step,
                "agent": agent_id,
                "role": "predator" if is_predator else "prey",
                "obs": obs_struct,
                "thought": raw_thought,
                "action": action_vec.tolist(),
                "reward": 0.0
            }

        if not actions: break

        # --- 2. 物理步进 ---
        observations, rewards, terminations, truncations, infos = env.step(actions)
        
        # --- 3. 统计 ---
        # 猎物和捕食者分开统计
        step_r_prey = 0.0
        step_r_pred = 0.0
        
        for aid, r in rewards.items():
            if "agent" in aid: step_r_prey += r
            if "adversary" in aid: step_r_pred += r # 这里简单累加所有捕食者得分
            
            # 回填日志
            if aid in step_records:
                step_records[aid]["reward"] = r
                game_log.append(step_records[aid])

        total_reward_prey += step_r_prey
        # 捕食者通常共享奖励，取平均或者单个代表即可，这里累加看总势能
        total_reward_pred += step_r_pred / NUM_ADV 
        print(rewards)
        print(f"  >> Reward: Prey={step_r_prey:.2f} (Tot:{total_reward_prey:.2f}) | Pred_Avg={step_r_pred/NUM_ADV:.2f}")

        if all(terminations.values()) or all(truncations.values()):
            print("Game Over.")
            break

    env.close()
    
    # Add final summary
    all_rewards = {"prey": total_reward_prey, "predators": total_reward_pred}
    mean_reward = (total_reward_prey + total_reward_pred) / 2.0
    game_log.append({
        "final_summary": True,
        "total_rewards": all_rewards,
        "mean_reward": float(mean_reward)
    })
    print(f"\nFINAL: Prey={total_reward_prey:.2f}, Pred={total_reward_pred:.2f}, Mean={mean_reward:.2f}")
    
    # 保存结果
    if frames:
        final_video = get_unique_filename(output_name + ".mp4")
        print(f"Saving video to {final_video} ...")
        imageio.mimsave(final_video, frames, fps=1)
    
    final_log = get_unique_filename(output_name + ".json")
    print(f"Saving logs to {final_log} ...")
    with open(final_log, "w", encoding="utf-8") as f:
        json.dump(game_log, f, indent=4, ensure_ascii=False)

# ============================================================================== 
# 3. 运行入口
# ============================================================================== 
if __name__ == "__main__":
    PROVIDER = "deepseek"
    # 1. 统一管理密钥，确保整个脚本都能访问
    MY_KEY = "sk-54dc1730e7234648b77b60d3a4c4419e"
    
    # 2. 先跑一次初始 Demo 确保通电
    run_tag_game(PROVIDER, "tag_demo", api_key=MY_KEY)
    
    # 3. 批量运行验证模式
    N_EPISODES = 1  # 扫榜阶段建议先跑 1 次，确保流程正确
    print(f"Plan to run {N_EPISODES} episodes...")

    for i in range(N_EPISODES):
        print(f"\n\n" + "="*40)
        print(f"🎬 STARTING BATCH {i+1} / {N_EPISODES}")
        print("="*40)
        
        # 构造带有编号的文件名
        batch_output_name = f"tag_demo_run_{i+1}"
        
        try:
            # 【关键修复】：这里必须把 api_key=MY_KEY 传进去
            # 否则第二次调用会报 401 错误
            run_tag_game(PROVIDER, batch_output_name, api_key=MY_KEY)
            print(f"✅ Batch {i+1} finished.")
        except Exception as e:
            print(f"❌ Batch {i+1} failed with error: {e}")
            continue 

    print("\nAll episodes completed. 扫榜任务即将达成！")
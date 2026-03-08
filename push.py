import numpy as np
import json
from typing import Dict, Any

from utils_api import get_api_engine, get_unique_filename
from prompt.prompt_for_push import (
    get_action_and_response_format,
    get_navigation_hints,
    get_physics_rules,
    get_task_and_reward,
)
from obs.parse_push_obs import parse_push_obs

try:
    from pettingzoo.mpe import simple_push_v3
except ImportError:
    raise ImportError("请安装 pettingzoo: pip install pettingzoo[mpe]")

def _format_current_obs(obs_struct: Dict[str, Any]) -> str:
    role = obs_struct['role']
    obs_lines = [
        "OBSERVATION SEMANTICS:",
        "- obs = [self_vel, landmarks..., opponent_rel] (role-dependent)",
        "CURRENT OBS STRUCT:",
        f"- role: {role}",
        f"- vel: {obs_struct.get('vel')}",
        f"- speed: {obs_struct.get('speed')}",
    ]
    if role == 'ADVERSARY':
        lms = obs_struct.get('landmarks', [])
        obs_lines.append(f"- landmarks: {lms}")
        obs_lines.append(f"- opponent_rel: {obs_struct.get('opponent_rel')}")
        obs_lines.append(f"- opponent_dist: {obs_struct.get('opponent_dist')}")
    else:
        obs_lines.append(f"- goal_rel: {obs_struct.get('goal_rel')}")
        obs_lines.append(f"- goal_dist: {obs_struct.get('goal_dist')}")
        obs_lines.append(f"- fake_rel: {obs_struct.get('fake_rel')}")
        obs_lines.append(f"- fake_dist: {obs_struct.get('fake_dist')}")
        obs_lines.append(f"- opponent_rel: {obs_struct.get('opponent_rel')}")
        obs_lines.append(f"- opponent_dist: {obs_struct.get('opponent_dist')}")
    return "\n".join(obs_lines)


def user_prompt_push(agent_id: str, step: int, obs_struct: Dict[str, Any]) -> str:
    role = obs_struct['role']
    parts = [
        get_task_and_reward(role),
        get_physics_rules(),
        get_action_and_response_format(),
        get_navigation_hints(role),
        _format_current_obs(obs_struct),
    ]
    return "\n\n".join(parts)

# ==============================================================================
# 3. 主循环 (全景记录版)
# ==============================================================================
def run_push_game(provider: str, output_name: str, **kwargs):
    MAX_STEPS = 30
    
    seed = kwargs.pop('seed', None)
    llm_engine = get_api_engine(provider, **kwargs)

    print("Initializing Push Env (Full Info Mode)...")
    env = simple_push_v3.parallel_env(max_cycles=MAX_STEPS, continuous_actions=True, render_mode="rgb_array")
    
    observations, infos = env.reset(seed=seed) if seed is not None else env.reset()
    frames = []
    game_log = []
    
    total_r_good = 0
    total_r_adv = 0

    for step in range(MAX_STEPS):
        print(f"\n{'='*30} STEP {step} {'='*30}")
        frame = env.render()
        if frame is not None: frames.append(frame)
        
        actions = {}
        step_buffer = {}

        # --- Decision Phase ---
        for agent_id in env.agents:
            obs_raw = observations[agent_id]
            obs_struct = parse_push_obs(obs_raw, agent_id)
            full_prompt = user_prompt_push(agent_id, step, obs_struct)
            
            sys_r = "You are a strategic AI agent in a physics simulation."
            action_vec, raw_thought = llm_engine.generate_action(sys_r, full_prompt)
            action_vec = np.clip(action_vec, 0.0, 1.0)
            actions[agent_id] = action_vec
            
            step_buffer[agent_id] = {
                "struct": obs_struct,
                "action": action_vec,
                "thought": raw_thought
            }

        # --- Environment Step ---
        observations, rewards, terminations, truncations, infos = env.step(actions)
        
        # --- Logging Phase ---
        for aid, info in step_buffer.items():
            r = rewards.get(aid, 0.0)
            role = info['struct']['role']
            icon = "🔴" if role == 'ADVERSARY' else "🟢"
            
            if role == 'ADVERSARY': total_r_adv += r
            else: total_r_good += r
            
            # 1. 打印基础信息
            print(f"\n{icon} {aid} | Reward: {r:.4f}")
            
            # 2. 打印物理感知 (Sight)
            if role == 'GOOD_AGENT':
                goal_vec = info['struct']['goal_rel']
                fake_vec = info['struct']['fake_rel']
                adv_vec = info['struct']['opponent_rel']
                print(f"   [Eye] Goal: {goal_vec}")
                print(f"   [Eye] Fake: {fake_vec}")
                print(f"   [Eye] Adv:  {adv_vec}")
            else:
                opp_vec = info['struct']['opponent_rel']
                print(f"   [Eye] GoodAgent: {opp_vec}")
                # 打印坏人看到的两个地标
                lms = info['struct']['landmarks']
                print(f"   [Eye] LM_A: {lms[0]['rel']} | LM_B: {lms[1]['rel']}")

            # 3. 打印完整思维 (Full Thought)
            print(f"   🧠 THOUGHT:\n   {info['thought'].strip()}") 

            # 4. 打印动作解释
            act = info['action']
            act_str = []
            if act[1]>0.1: act_str.append(f"LEFT({act[1]:.2f})")
            if act[2]>0.1: act_str.append(f"RIGHT({act[2]:.2f})")
            if act[3]>0.1: act_str.append(f"DOWN({act[3]:.2f})")
            if act[4]>0.1: act_str.append(f"UP({act[4]:.2f})")
            if sum(act) < 0.1: act_str.append("NO-OP")
            print(f"   🎬 EXECUTION: {np.round(act, 2)} -> {' + '.join(act_str)}")
            
            # 5. 保存详细数据到 Log
            game_log.append({
                "step": step,
                "agent": aid,
                "role": role,
                "obs": info['struct'],
                "action": info['action'].tolist(),
                "thought": info['thought'],
                "reward": r
            })

        if all(terminations.values()) or all(truncations.values()):
            print("Game Over.")
            break

    env.close()
    
    # Add final summary
    mean_reward = (total_r_good + total_r_adv) / 2.0
    game_log.append({
        "final_summary": True,
        "total_rewards": {"good": total_r_good, "adversary": total_r_adv},
        "mean_reward": float(mean_reward)
    })
    
    print(f"\n📊 SUMMARY: Good Reward={total_r_good:.2f}, Adv Reward={total_r_adv:.2f}, Mean={mean_reward:.2f}")
    
    if frames:
        vid_name = get_unique_filename(output_name + ".mp4")
        import imageio
        imageio.mimsave(vid_name, frames, fps=1, macro_block_size=1)
        print(f"Saved video to {vid_name}")
    
    final_log = get_unique_filename(output_name + ".json")
    with open(final_log, "w", encoding="utf-8") as f:
        json.dump(game_log, f, indent=4)
    print(f"Saved detailed logs to {final_log}")

if __name__ == "__main__":
    PROVIDER = "deepseek"
    MY_KEY = "sk-54dc1730e7234648b77b60d3a4c4419e" # 先定义好
    
    # 第一次跑 demo
    run_push_game(PROVIDER, "push_demo", api_key=MY_KEY)
    
    print("Starting Push Full-Info Run...")
    # 第二次跑 full_info，记得也要把 KEY 传进去！
    run_push_game(PROVIDER, "push_full_info", api_key=MY_KEY)
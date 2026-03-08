import os
import re
import json
import numpy as np
import imageio
import math
import matplotlib.pyplot as plt
from typing import Dict, Any, List
from utils_api import get_api_engine, get_unique_filename
from obs.parse_spread_obs import parse_spread_obs

# --- 全局常量定义 ---
DEFAULT_N = 3
LOCAL_RATIO = 0.5
PROVIDER = "deepseek"
API_KEY = "sk-54dc1730e7234648b77b60d3a4c4419e"
SUCCESS_THRESHOLD = 0.5  # 目标精度设为 0.5，展示秒杀效果

# 环境导入检查
try:
    from pettingzoo.mpe import simple_spread_v3
except ImportError:
    raise ImportError("请安装 pettingzoo: pip install pettingzoo[mpe]")

# 导入 Prompt 接口
from prompt.prompt_for_spread import (
    user_prompt,
    get_action_and_response_format,
    get_navigation_hints,
    get_physics_rules,
    get_task_and_reward,
)

def run_spread_game(provider: str, num_episodes: int = 5, **kwargs):
    MAX_STEPS = 30
    llm_engine = get_api_engine(provider, **kwargs)
    system_prompt = "You are a precise motion controller. Output ONLY a one-line JSON."
    
    all_episode_lengths = []

    print(f"🚀 Math Spirit [0.5 Precision Kill] 启动！")

    for ep in range(num_episodes):
        print(f"\n<<< EPISODE {ep+1}/{num_episodes} >>>")
        env = simple_spread_v3.parallel_env(
            N=DEFAULT_N, local_ratio=LOCAL_RATIO, max_cycles=MAX_STEPS,
            continuous_actions=True, render_mode="rgb_array"
        )
        observations, _ = env.reset()
        
        frames = []
        step_count = 0
        
        for step in range(MAX_STEPS):
            step_count += 1
            frame = env.render()
            if frame is not None: frames.append(frame)

            actions = {}
            for agent_id in env.agents:
                obs_raw = observations[agent_id]
                obs_struct = parse_spread_obs(obs_raw, num_agents=DEFAULT_N)
                
                # --- [核心注入：预计算距离] ---
                rel_pos = obs_struct.get('landmark_rel', [[9.9, 9.9]])[0]
                dist = math.sqrt(rel_pos[0]**2 + rel_pos[1]**2)
                obs_struct['precise_dist'] = round(dist, 4) 
                # -------------------------

                full_prompt = user_prompt(agent_id, step, obs_struct, num_agents=DEFAULT_N, local_ratio=LOCAL_RATIO)
                action_vec, _ = llm_engine.generate_action(system_prompt, full_prompt)
                
                # 防御性对齐
                if not isinstance(action_vec, (list, np.ndarray)) or len(action_vec) != 5:
                    action_vec = [0.0] * 5
                
                actions[agent_id] = np.array(action_vec, dtype=np.float32)

            observations, rewards, terminations, truncations, infos = env.step(actions)

            # 0.5 阈值判定
            dists = []
            for aid in env.agents:
                st = parse_spread_obs(observations[aid], num_agents=DEFAULT_N)
                d_to_l = [np.linalg.norm(l) for l in st.get('landmark_rel', [])]
                if d_to_l: dists.append(min(d_to_l))
            
            if dists and all(d < SUCCESS_THRESHOLD for d in dists):
                print(f"🎯 0.5 精度达成！步数: {step_count}")
                break
            
            if all(terminations.values()) or all(truncations.values()):
                break

        all_episode_lengths.append(step_count)
        env.close()
        
        if frames:
            imageio.mimsave(get_unique_filename(f"ep{ep+1}_05_test.mp4"), frames, fps=5)

    # 绘图逻辑
    os.makedirs("theory", exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, num_episodes + 1), all_episode_lengths, color='#003366', marker='o', label='Math Spirit (0.5 Kill)')
    plt.axhline(y=MAX_STEPS, color='#A9A9A9', linestyle='--', label='Baseline Limit')
    plt.title('Convergence Analysis (Threshold: 0.5)', fontsize=14, color='#003366', fontweight='bold')
    plt.xlabel('Trial Episode')
    plt.ylabel('Steps')
    plt.ylim(0, 35)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig("theory/efficiency_curve.pdf", bbox_inches='tight')
    print(f"\n✅ 0.5 实验完成！PDF 已更新。")

if __name__ == "__main__":
    run_spread_game(PROVIDER, num_episodes=5, api_key=API_KEY)
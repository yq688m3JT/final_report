from pathlib import Path

import pandas as pd

from baselines import LocalGreedyHeuristic, StaticFixedTiming, ThresholdHeuristic
from complex_traffic_env import ComplexTrafficEnv
from rl_agent import DQNAgent


HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "dqn_complex.pt"
RESULTS_PATH = HERE / "results_complex.csv"


def run_policy(name, policy, episodes: int = 80, seed: int = 800):
    rows = []
    for i in range(episodes):
        env = ComplexTrafficEnv(seed=seed + i)
        if hasattr(policy, "reset"):
            policy.reset()
        total_reward = total_queue = total_delay = throughput = switches = spillback = 0.0
        done = False
        while not done:
            if name == "DQN RL":
                action = policy.act(env.state_vector(), epsilon=0.0)
            else:
                action = policy.act(env)
            _, reward, done, info = env.step(action)
            total_reward += reward
            total_queue += info["total_queue"]
            total_delay += info["delay"]
            throughput += info["throughput"]
            switches += info["switches"]
            spillback += info["spillback"]
        rows.append(
            {
                "Approach": name,
                "Avg Reward": total_reward,
                "Avg Queue": total_queue / env.horizon,
                "Avg Delay": total_delay / env.horizon,
                "Throughput": throughput,
                "Switches": switches,
                "Spillback": spillback / env.horizon,
            }
        )
    return rows


def evaluate():
    dqn = DQNAgent(seed=19)
    dqn.load(MODEL_PATH)
    policies = {
        "DQN RL": dqn,
        "Static": StaticFixedTiming(cycle=12),
        "Greedy": LocalGreedyHeuristic(),
        "Threshold": ThresholdHeuristic(threshold=4),
    }
    rows = []
    for name, policy in policies.items():
        rows.extend(run_policy(name, policy))
    df = pd.DataFrame(rows).groupby("Approach", as_index=False).mean(numeric_only=True)
    df = df.sort_values("Avg Reward", ascending=False)
    df.to_csv(RESULTS_PATH, index=False)
    print(df.to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    print(f"\nSaved complex experiment results to {RESULTS_PATH}")


if __name__ == "__main__":
    evaluate()

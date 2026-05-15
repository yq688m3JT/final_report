from pathlib import Path

import pandas as pd

from complex_traffic_env import ComplexTrafficEnv
from rl_agent import DQNAgent


HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "dqn_complex.pt"
CURVE_PATH = HERE / "training_curve.csv"


def train(episodes: int = 180, seed: int = 19):
    agent = DQNAgent(seed=seed)
    rows = []
    epsilon_start, epsilon_end = 1.0, 0.05

    for episode in range(episodes):
        env = ComplexTrafficEnv(seed=seed + episode)
        state = env.state_vector()
        total_reward = 0.0
        total_loss = 0.0
        updates = 0
        epsilon = max(epsilon_end, epsilon_start - episode / (episodes * 0.78))

        done = False
        while not done:
            action = agent.act(state, epsilon=epsilon)
            _, reward, done, _ = env.step(action)
            next_state = env.state_vector()
            agent.remember(state, action, reward / 50.0, next_state, done)
            loss = agent.learn()
            if loss is not None:
                total_loss += loss
                updates += 1
            state = next_state
            total_reward += reward

        if episode % 8 == 0:
            agent.update_target()
        rows.append(
            {
                "episode": episode + 1,
                "reward": total_reward,
                "epsilon": epsilon,
                "loss": total_loss / updates if updates else 0.0,
            }
        )
        if (episode + 1) % 30 == 0:
            print(f"episode {episode + 1:03d} reward={total_reward:8.1f} epsilon={epsilon:.2f}")

    agent.save(MODEL_PATH)
    pd.DataFrame(rows).to_csv(CURVE_PATH, index=False)
    print(f"Saved model to {MODEL_PATH}")
    print(f"Saved training curve to {CURVE_PATH}")


if __name__ == "__main__":
    train()

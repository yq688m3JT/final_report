import numpy as np
import time
import random

# --- Environment Setup ---
class TrafficEnv:
    def __init__(self):
        self.queue_ns = 0
        self.queue_ew = 0
        self.phase = 0  # 0: NS Green, 1: EW Green
        self.max_queue = 15
        self.arrival_rate = 0.3
        self.departure_rate = 0.5
        self.penalty_switch = 1.0

    def get_state(self):
        # Discretize: Low [0-3], Medium [4-8], High [9+]
        def discretize(q):
            if q <= 3: return 0
            if q <= 8: return 1
            return 2
        return (discretize(self.queue_ns), discretize(self.queue_ew), self.phase)

    def step(self, action):
        # Action: 0: Stay, 1: Switch
        reward = -(self.queue_ns + self.queue_ew)
        
        if action == 1:
            self.phase = 1 - self.phase
            reward -= self.penalty_switch

        # Departures
        if self.phase == 0:
            if self.queue_ns > 0 and random.random() < self.departure_rate:
                self.queue_ns -= 1
        else:
            if self.queue_ew > 0 and random.random() < self.departure_rate:
                self.queue_ew -= 1

        # Arrivals
        if random.random() < self.arrival_rate:
            self.queue_ns = min(self.queue_ns + 1, self.max_queue)
        if random.random() < self.arrival_rate:
            self.queue_ew = min(self.queue_ew + 1, self.max_queue)

        return self.get_state(), reward

    def reset(self):
        self.queue_ns = random.randint(0, 5)
        self.queue_ew = random.randint(0, 5)
        self.phase = 0
        return self.get_state()

# --- Agents ---

class QLearningAgent:
    def __init__(self, states_shape, actions_n, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.q_table = np.zeros(states_shape + (actions_n,))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 1)
        return np.argmax(self.q_table[state])

    def learn(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.gamma * self.q_table[next_state][best_next_action]
        self.q_table[state][action] += self.alpha * (td_target - self.q_table[state][action])

class SARSAAgent(QLearningAgent):
    def learn(self, state, action, reward, next_state, next_action):
        td_target = reward + self.gamma * self.q_table[next_state][next_action]
        self.q_table[state][action] += self.alpha * (td_target - self.q_table[state][action])

class MCAgent:
    def __init__(self, states_shape, actions_n, gamma=0.9, epsilon=0.1):
        self.q_table = np.zeros(states_shape + (actions_n,))
        self.returns = {} # (state, action) -> list of returns
        self.gamma = gamma
        self.epsilon = epsilon

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 1)
        return np.argmax(self.q_table[state])

    def learn(self, episode_data):
        G = 0
        visited = set()
        for i in reversed(range(len(episode_data))):
            state, action, reward = episode_data[i]
            G = reward + self.gamma * G
            if (state, action) not in visited:
                if (state, action) not in self.returns:
                    self.returns[(state, action)] = []
                self.returns[(state, action)].append(G)
                self.q_table[state][action] = np.mean(self.returns[(state, action)])
                visited.add((state, action))

# --- Value Iteration for Optimal Policy ---

class ValueIterationAgent:
    def __init__(self, max_q=15, arrival_rate=0.3, departure_rate=0.5, penalty_switch=1.0, gamma=0.9):
        self.max_q = max_q
        self.arrival_rate = arrival_rate
        self.departure_rate = departure_rate
        self.penalty_switch = penalty_switch
        self.gamma = gamma
        # State: (q_ns, q_ew, phase) -> 16 * 16 * 2 = 512 states
        self.V = np.zeros((max_q + 1, max_q + 1, 2))
        self.policy = np.zeros((max_q + 1, max_q + 1, 2), dtype=int)
        self.compute_optimal_policy()

    def compute_optimal_policy(self, iterations=100):
        for _ in range(iterations):
            new_V = np.copy(self.V)
            for q_ns in range(self.max_q + 1):
                for q_ew in range(self.max_q + 1):
                    for phase in range(2):
                        q_values = []
                        for action in range(2): # 0: Stay, 1: Switch
                            # Reward
                            reward = -(q_ns + q_ew)
                            if action == 1:
                                reward -= self.penalty_switch
                            
                            # Next phase
                            next_phase = phase if action == 0 else 1 - phase
                            
                            # Simple transition model for VI (Approximation of the env)
                            # In reality, multiple arrivals/departures can happen.
                            # We'll use a simplified expected next state for VI baseline.
                            expected_v_next = 0
                            
                            # Probabilities of arrival/departure
                            # P(arr) = 0.3, P(no_arr) = 0.7
                            # P(dep) = 0.5, P(no_dep) = 0.5 (only for green lane)
                            
                            for arr_ns in [0, 1]:
                                p_arr_ns = self.arrival_rate if arr_ns == 1 else (1 - self.arrival_rate)
                                for arr_ew in [0, 1]:
                                    p_arr_ew = self.arrival_rate if arr_ew == 1 else (1 - self.arrival_rate)
                                    for dep in [0, 1]:
                                        p_dep = self.departure_rate if dep == 1 else (1 - self.departure_rate)
                                        
                                        n_q_ns = min(self.max_q, q_ns + arr_ns)
                                        n_q_ew = min(self.max_q, q_ew + arr_ew)
                                        
                                        if next_phase == 0: # NS Green
                                            if dep == 1 and n_q_ns > 0: n_q_ns -= 1
                                        else: # EW Green
                                            if dep == 1 and n_q_ew > 0: n_q_ew -= 1
                                            
                                        prob = p_arr_ns * p_arr_ew * p_dep
                                        expected_v_next += prob * self.V[n_q_ns, n_q_ew, next_phase]
                            
                            q_values.append(reward + self.gamma * expected_v_next)
                        
                        new_V[q_ns, q_ew, phase] = max(q_values)
                        self.policy[q_ns, q_ew, phase] = np.argmax(q_values)
            if np.max(np.abs(new_V - self.V)) < 1e-4:
                break
            self.V = new_V

    def choose_action(self, state_full):
        return self.policy[state_full]

# --- Experiment Execution ---

def run_experiment(episodes=10000, steps_per_episode=50):
    env = TrafficEnv()
    states_shape = (3, 3, 2)
    actions_n = 2

    vi_agent = ValueIterationAgent()

    agents = {
        "Q-Learning": QLearningAgent(states_shape, actions_n),
        "SARSA": SARSAAgent(states_shape, actions_n),
        "Monte Carlo": MCAgent(states_shape, actions_n),
        "Optimal (VI)": vi_agent,
        "Static (Baseline)": None,
        "Greedy (Heuristic)": None
    }


    results = {name: [] for name in agents}
    times = {name: 0 for name in agents}

    for name, agent in agents.items():
        start_time = time.time()
        for ep in range(episodes):
            state = env.reset()
            total_reward = 0
            episode_data = []
            
            # For SARSA
            if name == "SARSA":
                action = agent.choose_action(state)

            for _ in range(steps_per_episode):
                if name == "Static (Baseline)":
                    action = 1 if _ % 10 == 0 else 0
                elif name == "Greedy (Heuristic)":
                    # Discretized comparison
                    action = 1 if (env.phase == 0 and env.queue_ew > env.queue_ns) or \
                                  (env.phase == 1 and env.queue_ns > env.queue_ew) else 0
                elif name == "Optimal (VI)":
                    action = agent.choose_action((env.queue_ns, env.queue_ew, env.phase))
                elif name == "SARSA":
                    pass # action already chosen
                else:
                    action = agent.choose_action(state)

                next_state, reward = env.step(action)
                total_reward += reward

                if name == "Q-Learning":
                    agent.learn(state, action, reward, next_state)
                elif name == "SARSA":
                    next_action = agent.choose_action(next_state)
                    agent.learn(state, action, reward, next_state, next_action)
                    action = next_action
                elif name == "Monte Carlo":
                    episode_data.append((state, action, reward))
                
                state = next_state

            if name == "Monte Carlo":
                agent.learn(episode_data)

            results[name].append(total_reward)
        times[name] = time.time() - start_time

    return results, times

if __name__ == "__main__":
    print("Running 10,000 tests (episodes) per approach...")
    results, times = run_experiment(10000)
    
    print("\nResults (Average Reward of Last 1000 Episodes):")
    for name, rewards in results.items():
        avg_last_1000 = np.mean(rewards[-1000:])
        print(f"{name:20}: Reward: {avg_last_1000:.2f}, Time: {times[name]:.2f}s")

    # Save summary for updates
    with open("results_summary.txt", "w") as f:
        f.write("Approach | Avg Reward (Last 1k) | Execution Time (s)\n")
        f.write("-" * 55 + "\n")
        for name, rewards in results.items():
            avg_last_1000 = np.mean(rewards[-1000:])
            f.write(f"{name:20} | {avg_last_1000:18.2f} | {times[name]:18.2f}\n")

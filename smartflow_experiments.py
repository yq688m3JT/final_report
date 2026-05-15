"""SmartFlow traffic-signal experiments.

This file contains two reproducible experiments:

1. A single-intersection experiment that matches the original slide/report
   formulation: tabular Q-learning, SARSA, Monte Carlo, static timing,
   greedy longest-queue-first, and a value-iteration ceiling.
2. A network experiment on a 3x3 city grid with spillback. The extension is
   intentionally harder for traditional algorithms because a local queue can
   be a bad signal when the downstream road is already full.

Run:
    python smartflow_experiments.py
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import csv
import json
import math
import random
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"


# ---------------------------------------------------------------------------
# Experiment 1: original single-intersection slide validation
# ---------------------------------------------------------------------------


class TrafficEnv:
    def __init__(
        self,
        arrival_rate: float = 0.30,
        departure_rate: float = 0.50,
        max_queue: int = 15,
        penalty_switch: float = 1.0,
    ) -> None:
        self.arrival_rate = arrival_rate
        self.departure_rate = departure_rate
        self.max_queue = max_queue
        self.penalty_switch = penalty_switch
        self.queue_ns = 0
        self.queue_ew = 0
        self.phase = 0

    def reset(self) -> tuple[int, int, int]:
        self.queue_ns = random.randint(0, 5)
        self.queue_ew = random.randint(0, 5)
        self.phase = 0
        return self.state()

    def state(self) -> tuple[int, int, int]:
        def bucket(q: int) -> int:
            if q <= 3:
                return 0
            if q <= 8:
                return 1
            return 2

        return bucket(self.queue_ns), bucket(self.queue_ew), self.phase

    def step(self, action: int) -> tuple[tuple[int, int, int], float]:
        reward = -(self.queue_ns + self.queue_ew)
        if action == 1:
            self.phase = 1 - self.phase
            reward -= self.penalty_switch

        if self.phase == 0:
            if self.queue_ns > 0 and random.random() < self.departure_rate:
                self.queue_ns -= 1
        else:
            if self.queue_ew > 0 and random.random() < self.departure_rate:
                self.queue_ew -= 1

        if random.random() < self.arrival_rate:
            self.queue_ns = min(self.max_queue, self.queue_ns + 1)
        if random.random() < self.arrival_rate:
            self.queue_ew = min(self.max_queue, self.queue_ew + 1)
        return self.state(), reward


class QLearningAgent:
    def __init__(
        self,
        state_shape: tuple[int, ...],
        actions: int,
        alpha: float = 0.10,
        gamma: float = 0.90,
        epsilon: float = 0.10,
    ) -> None:
        self.q = np.zeros(state_shape + (actions,))
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def choose_action(self, state: tuple[int, ...]) -> int:
        if random.random() < self.epsilon:
            return random.randint(0, self.q.shape[-1] - 1)
        return int(np.argmax(self.q[state]))

    def learn(self, state: tuple[int, ...], action: int, reward: float, next_state: tuple[int, ...]) -> None:
        target = reward + self.gamma * np.max(self.q[next_state])
        self.q[state][action] += self.alpha * (target - self.q[state][action])


class SARSAAgent(QLearningAgent):
    def learn(  # type: ignore[override]
        self,
        state: tuple[int, ...],
        action: int,
        reward: float,
        next_state: tuple[int, ...],
        next_action: int,
    ) -> None:
        target = reward + self.gamma * self.q[next_state][next_action]
        self.q[state][action] += self.alpha * (target - self.q[state][action])


class MCAgent(QLearningAgent):
    def __init__(self, state_shape: tuple[int, ...], actions: int, gamma: float = 0.90, epsilon: float = 0.10) -> None:
        super().__init__(state_shape, actions, alpha=0.0, gamma=gamma, epsilon=epsilon)
        self.returns: dict[tuple[tuple[int, ...], int], list[float]] = {}

    def learn_episode(self, episode: list[tuple[tuple[int, ...], int, float]]) -> None:
        total = 0.0
        visited: set[tuple[tuple[int, ...], int]] = set()
        for state, action, reward in reversed(episode):
            total = reward + self.gamma * total
            key = (state, action)
            if key in visited:
                continue
            self.returns.setdefault(key, []).append(total)
            self.q[state][action] = float(np.mean(self.returns[key]))
            visited.add(key)


class ValueIterationAgent:
    def __init__(
        self,
        max_queue: int = 15,
        arrival_rate: float = 0.30,
        departure_rate: float = 0.50,
        switch_penalty: float = 1.0,
        gamma: float = 0.90,
    ) -> None:
        self.max_queue = max_queue
        self.arrival_rate = arrival_rate
        self.departure_rate = departure_rate
        self.switch_penalty = switch_penalty
        self.gamma = gamma
        self.v = np.zeros((max_queue + 1, max_queue + 1, 2))
        self.policy = np.zeros((max_queue + 1, max_queue + 1, 2), dtype=int)
        self._solve()

    def _solve(self, iterations: int = 100) -> None:
        for _ in range(iterations):
            next_v = self.v.copy()
            for q_ns in range(self.max_queue + 1):
                for q_ew in range(self.max_queue + 1):
                    for phase in range(2):
                        action_values = []
                        for action in (0, 1):
                            reward = -(q_ns + q_ew) - (self.switch_penalty if action else 0.0)
                            next_phase = phase if action == 0 else 1 - phase
                            expected = 0.0
                            for arr_ns in (0, 1):
                                p_ns = self.arrival_rate if arr_ns else 1 - self.arrival_rate
                                for arr_ew in (0, 1):
                                    p_ew = self.arrival_rate if arr_ew else 1 - self.arrival_rate
                                    for dep in (0, 1):
                                        p_dep = self.departure_rate if dep else 1 - self.departure_rate
                                        n_ns = min(self.max_queue, q_ns + arr_ns)
                                        n_ew = min(self.max_queue, q_ew + arr_ew)
                                        if next_phase == 0 and dep and n_ns > 0:
                                            n_ns -= 1
                                        if next_phase == 1 and dep and n_ew > 0:
                                            n_ew -= 1
                                        expected += p_ns * p_ew * p_dep * self.v[n_ns, n_ew, next_phase]
                            action_values.append(reward + self.gamma * expected)
                        next_v[q_ns, q_ew, phase] = max(action_values)
                        self.policy[q_ns, q_ew, phase] = int(np.argmax(action_values))
            if np.max(np.abs(next_v - self.v)) < 1e-4:
                self.v = next_v
                break
            self.v = next_v

    def choose_action(self, env: TrafficEnv) -> int:
        return int(self.policy[env.queue_ns, env.queue_ew, env.phase])


def run_slide_validation(episodes: int = 10_000, steps: int = 50, seed: int = 19) -> dict[str, dict[str, float]]:
    np.random.seed(seed)
    random.seed(seed)
    agents = {
        "Q-Learning": QLearningAgent((3, 3, 2), 2),
        "SARSA": SARSAAgent((3, 3, 2), 2),
        "Monte Carlo": MCAgent((3, 3, 2), 2),
        "Optimal (VI)": ValueIterationAgent(),
        "Static (Baseline)": None,
        "Greedy (Heuristic)": None,
    }
    summary: dict[str, dict[str, float]] = {}

    for name, agent in agents.items():
        env = TrafficEnv()
        rewards: list[float] = []
        start = time.time()
        for _ in range(episodes):
            state = env.reset()
            total = 0.0
            episode: list[tuple[tuple[int, ...], int, float]] = []
            action = agent.choose_action(state) if name == "SARSA" and agent is not None else 0
            for step in range(steps):
                if name == "Static (Baseline)":
                    action = 1 if step % 10 == 0 else 0
                elif name == "Greedy (Heuristic)":
                    action = int((env.phase == 0 and env.queue_ew > env.queue_ns) or (env.phase == 1 and env.queue_ns > env.queue_ew))
                elif name == "Optimal (VI)":
                    action = agent.choose_action(env)  # type: ignore[union-attr]
                elif name != "SARSA":
                    action = agent.choose_action(state)  # type: ignore[union-attr]

                next_state, reward = env.step(action)
                total += reward

                if name == "Q-Learning":
                    agent.learn(state, action, reward, next_state)  # type: ignore[union-attr]
                elif name == "SARSA":
                    next_action = agent.choose_action(next_state)  # type: ignore[union-attr]
                    agent.learn(state, action, reward, next_state, next_action)  # type: ignore[union-attr]
                    action = next_action
                elif name == "Monte Carlo":
                    episode.append((state, action, reward))
                state = next_state
            if name == "Monte Carlo":
                agent.learn_episode(episode)  # type: ignore[union-attr]
            rewards.append(total)
        summary[name] = {
            "avg_reward_last_1000": float(np.mean(rewards[-1000:])),
            "runtime_seconds": float(time.time() - start),
        }
    return summary


# ---------------------------------------------------------------------------
# Experiment 2: network extension with spillback
# ---------------------------------------------------------------------------


DIRS = ("N", "S", "E", "W")
DELTA = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
PHASE_GROUP = {0: ("N", "S"), 1: ("E", "W")}


@dataclass
class Vehicle:
    path: deque[str]
    born: int


class GridTrafficEnv:
    def __init__(
        self,
        size: int = 3,
        horizon: int = 240,
        capacity: int = 42,
        saturation: int = 3,
        switch_penalty: float = 0.40,
        seed: int = 0,
        demand_scale: float = 1.0,
    ) -> None:
        self.size = size
        self.horizon = horizon
        self.capacity = capacity
        self.saturation = saturation
        self.switch_penalty = switch_penalty
        self.rng = random.Random(seed)
        self.demand_scale = demand_scale
        self.t = 0
        self.phase = np.zeros((size, size), dtype=int)
        self.min_green = np.zeros((size, size), dtype=int)
        self.queues: list[list[dict[str, deque[Vehicle]]]] = []
        self.last_switches = 0
        self.last_blocked = 0
        self.exited_delays: list[int] = []
        self.reset(seed)

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self.rng.seed(seed)
        self.t = 0
        self.phase.fill(0)
        self.min_green.fill(0)
        self.last_switches = 0
        self.last_blocked = 0
        self.exited_delays = []
        self.queues = [[{direction: deque() for direction in DIRS} for _ in range(self.size)] for _ in range(self.size)]

    def clone_phase(self) -> np.ndarray:
        return self.phase.copy()

    def total_queue(self) -> int:
        return sum(len(self.queues[r][c][d]) for r in range(self.size) for c in range(self.size) for d in DIRS)

    def intersection_queue(self, r: int, c: int) -> int:
        return sum(len(self.queues[r][c][d]) for d in DIRS)

    def movement_count(self, r: int, c: int, directions: tuple[str, str]) -> int:
        return sum(len(self.queues[r][c][d]) for d in directions)

    def downstream_pressure(self, r: int, c: int, directions: tuple[str, str]) -> int:
        pressure = 0
        for direction in directions:
            nr, nc = r + DELTA[direction][0], c + DELTA[direction][1]
            if 0 <= nr < self.size and 0 <= nc < self.size:
                pressure += self.intersection_queue(nr, nc)
        return pressure

    def local_state(self, r: int, c: int) -> tuple[int, int, int, int]:
        ns = self.movement_count(r, c, ("N", "S"))
        ew = self.movement_count(r, c, ("E", "W"))
        downstream = self.downstream_pressure(r, c, PHASE_GROUP[self.phase[r, c]])

        def bucket(value: int) -> int:
            if value <= 4:
                return 0
            if value <= 12:
                return 1
            return 2

        return bucket(ns), bucket(ew), int(self.phase[r, c]), bucket(downstream)

    def _demand_rate(self) -> float:
        base = 0.15 + 0.10 * math.sin(2 * math.pi * self.t / self.horizon)
        rush_pulse = 0.20 if 70 <= self.t <= 155 else 0.0
        return self.demand_scale * (base + rush_pulse)

    def _make_route(self, start_side: str, lane: int) -> tuple[int, int, deque[str]]:
        n = self.size
        if start_side == "N":
            r, c = 0, lane
            main = ["S"] * n
        elif start_side == "S":
            r, c = n - 1, lane
            main = ["N"] * n
        elif start_side == "W":
            r, c = lane, 0
            main = ["E"] * n
        else:
            r, c = lane, n - 1
            main = ["W"] * n

        route = deque(main)
        if self.rng.random() < 0.35:
            if start_side in ("N", "S"):
                turn = "E" if lane < n - 1 else "W"
            else:
                turn = "S" if lane < n - 1 else "N"
            route.insert(max(1, len(route) // 2), turn)
        return r, c, route

    def _arrive(self) -> None:
        rate = self._demand_rate()
        sides = ["N", "S", "E", "W"]
        for side in sides:
            for lane in range(self.size):
                lane_bias = 1.25 if lane == 1 else 0.85
                if self.rng.random() < rate * lane_bias:
                    r, c, route = self._make_route(side, lane)
                    first_direction = route[0]
                    if self.intersection_queue(r, c) < self.capacity:
                        self.queues[r][c][first_direction].append(Vehicle(route, self.t))
                    else:
                        self.last_blocked += 1

    def step(self, actions: np.ndarray) -> tuple[float, dict[str, float]]:
        self.last_switches = 0
        self.last_blocked = 0
        for r in range(self.size):
            for c in range(self.size):
                if actions[r, c] == 1 and self.min_green[r, c] <= 0:
                    self.phase[r, c] = 1 - self.phase[r, c]
                    self.min_green[r, c] = 3
                    self.last_switches += 1
                else:
                    self.min_green[r, c] = max(0, self.min_green[r, c] - 1)

        moved: list[tuple[int, int, Vehicle]] = []
        for r in range(self.size):
            for c in range(self.size):
                for direction in PHASE_GROUP[int(self.phase[r, c])]:
                    q = self.queues[r][c][direction]
                    for _ in range(min(self.saturation, len(q))):
                        vehicle = q[0]
                        current_direction = vehicle.path[0]
                        nr, nc = r + DELTA[current_direction][0], c + DELTA[current_direction][1]
                        if 0 <= nr < self.size and 0 <= nc < self.size and self.intersection_queue(nr, nc) >= self.capacity:
                            self.last_blocked += 1
                            break
                        q.popleft()
                        vehicle.path.popleft()
                        if not vehicle.path:
                            self.exited_delays.append(self.t - vehicle.born + 1)
                        else:
                            moved.append((nr, nc, vehicle))

        for nr, nc, vehicle in moved:
            self.queues[nr][nc][vehicle.path[0]].append(vehicle)

        self._arrive()
        queue = self.total_queue()
        delay = queue
        reward = -delay - 6.0 * self.last_blocked - self.switch_penalty * self.last_switches
        self.t += 1
        metrics = {
            "queue": float(queue),
            "blocked": float(self.last_blocked),
            "switches": float(self.last_switches),
            "throughput": float(len(self.exited_delays)),
        }
        return reward, metrics


class NetworkQLearning:
    def __init__(self, epsilon: float = 0.20, alpha: float = 0.20, gamma: float = 0.95) -> None:
        self.q = np.zeros((3, 3, 2, 3, 2))
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma

    def act(self, env: GridTrafficEnv, train: bool = True) -> tuple[np.ndarray, list[tuple[int, int, tuple[int, int, int, int], int]]]:
        actions = np.zeros((env.size, env.size), dtype=int)
        records: list[tuple[int, int, tuple[int, int, int, int], int]] = []
        for r in range(env.size):
            for c in range(env.size):
                state = env.local_state(r, c)
                if train and random.random() < self.epsilon:
                    action = random.randint(0, 1)
                else:
                    action = int(np.argmax(self.q[state]))
                actions[r, c] = action
                records.append((r, c, state, action))
        return actions, records

    def learn(self, records: list[tuple[int, int, tuple[int, int, int, int], int]], reward: float, env: GridTrafficEnv) -> None:
        for r, c, state, action in records:
            local_reward = reward / (env.size * env.size)
            next_state = env.local_state(r, c)
            target = local_reward + self.gamma * np.max(self.q[next_state])
            self.q[state][action] += self.alpha * (target - self.q[state][action])


def fixed_time_policy(env: GridTrafficEnv, cycle: int = 12) -> np.ndarray:
    action = np.zeros((env.size, env.size), dtype=int)
    if env.t % cycle == 0:
        action.fill(1)
    return action


def greedy_policy(env: GridTrafficEnv) -> np.ndarray:
    action = np.zeros((env.size, env.size), dtype=int)
    for r in range(env.size):
        for c in range(env.size):
            ns = env.movement_count(r, c, ("N", "S"))
            ew = env.movement_count(r, c, ("E", "W"))
            desired = 0 if ns >= ew else 1
            action[r, c] = int(desired != env.phase[r, c])
    return action


def max_pressure_policy(env: GridTrafficEnv) -> np.ndarray:
    action = np.zeros((env.size, env.size), dtype=int)
    for r in range(env.size):
        for c in range(env.size):
            ns_score = env.movement_count(r, c, ("N", "S")) - 0.25 * env.downstream_pressure(r, c, ("N", "S"))
            ew_score = env.movement_count(r, c, ("E", "W")) - 0.25 * env.downstream_pressure(r, c, ("E", "W"))
            desired = 0 if ns_score >= ew_score else 1
            action[r, c] = int(desired != env.phase[r, c])
    return action


def train_network_agent(episodes: int = 700, horizon: int = 240, seed: int = 19) -> NetworkQLearning:
    np.random.seed(seed)
    random.seed(seed)
    agent = NetworkQLearning()
    for ep in range(episodes):
        env = GridTrafficEnv(horizon=horizon, seed=seed + ep, demand_scale=1.15)
        agent.epsilon = max(0.02, 0.25 * (1.0 - ep / episodes))
        for _ in range(horizon):
            actions, records = agent.act(env, train=True)
            reward, _ = env.step(actions)
            agent.learn(records, reward, env)
    return agent


def evaluate_network_policy(
    name: str,
    policy,
    episodes: int = 80,
    horizon: int = 240,
    seed: int = 900,
) -> dict[str, float]:
    totals = {"queue": [], "blocked": [], "switches": [], "throughput": [], "delay": []}
    for ep in range(episodes):
        env = GridTrafficEnv(horizon=horizon, seed=seed + ep, demand_scale=1.15)
        queue_area = 0.0
        blocked = 0.0
        switches = 0.0
        for _ in range(horizon):
            actions = policy(env)
            _, metrics = env.step(actions)
            queue_area += metrics["queue"]
            blocked += metrics["blocked"]
            switches += metrics["switches"]
        throughput = len(env.exited_delays)
        mean_delay = float(np.mean(env.exited_delays)) if env.exited_delays else float("nan")
        totals["queue"].append(queue_area / horizon)
        totals["blocked"].append(blocked)
        totals["switches"].append(switches)
        totals["throughput"].append(throughput)
        totals["delay"].append(mean_delay)

    return {
        "policy": name,
        "avg_queue": float(np.mean(totals["queue"])),
        "avg_blocked": float(np.mean(totals["blocked"])),
        "avg_switches": float(np.mean(totals["switches"])),
        "avg_throughput": float(np.mean(totals["throughput"])),
        "avg_delay": float(np.mean(totals["delay"])),
    }


def run_network_extension(seed: int = 19) -> list[dict[str, float]]:
    start = time.time()
    agent = train_network_agent(seed=seed)

    def rl_policy(env: GridTrafficEnv) -> np.ndarray:
        actions, _ = agent.act(env, train=False)
        return actions

    rows = [
        evaluate_network_policy("Static fixed-time", fixed_time_policy),
        evaluate_network_policy("Greedy longest-queue", greedy_policy),
        evaluate_network_policy("Max-pressure heuristic", max_pressure_policy),
        evaluate_network_policy("Tabular RL network controller", rl_policy),
    ]
    for row in rows:
        row["experiment_seconds"] = time.time() - start
    return rows


def write_outputs(slide_rows: dict[str, dict[str, float]], network_rows: list[dict[str, float]]) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    FIGURES_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "slide_validation.json").write_text(json.dumps(slide_rows, indent=2), encoding="utf-8")
    (RESULTS_DIR / "network_extension.json").write_text(json.dumps(network_rows, indent=2), encoding="utf-8")

    with (RESULTS_DIR / "network_extension.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(network_rows[0].keys()))
        writer.writeheader()
        writer.writerows(network_rows)

    labels = [row["policy"] for row in network_rows]
    queues = [row["avg_queue"] for row in network_rows]
    delays = [row["avg_delay"] for row in network_rows]

    plt.figure(figsize=(9, 4.8))
    bars = plt.bar(labels, queues, color=["#7f8c8d", "#95a5a6", "#4f6d7a", "#1f77b4"])
    plt.ylabel("Average network queue")
    plt.title("Network extension: congestion by controller")
    plt.xticks(rotation=18, ha="right")
    for bar, value in zip(bars, queues):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{value:.1f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "network_queue_comparison.png", dpi=180)
    plt.close()

    plt.figure(figsize=(9, 4.8))
    bars = plt.bar(labels, delays, color=["#7f8c8d", "#95a5a6", "#4f6d7a", "#1f77b4"])
    plt.ylabel("Mean completed-trip delay")
    plt.title("Network extension: delay by controller")
    plt.xticks(rotation=18, ha="right")
    for bar, value in zip(bars, delays):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{value:.1f}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "network_delay_comparison.png", dpi=180)
    plt.close()


def main() -> None:
    print("Running slide-validation experiment...")
    slide_rows = run_slide_validation()
    print(json.dumps(slide_rows, indent=2))

    print("\nRunning 3x3 network extension...")
    network_rows = run_network_extension()
    print(json.dumps(network_rows, indent=2))
    write_outputs(slide_rows, network_rows)
    print(f"\nWrote results to {RESULTS_DIR}")


if __name__ == "__main__":
    main()

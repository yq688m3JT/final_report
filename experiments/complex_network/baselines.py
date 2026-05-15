from __future__ import annotations

from complex_traffic_env import ComplexTrafficEnv


class StaticFixedTiming:
    def __init__(self, cycle: int = 12):
        self.cycle = cycle

    def reset(self):
        pass

    def act(self, env: ComplexTrafficEnv) -> int:
        switch = int(env.t > 0 and env.t % self.cycle == 0)
        return 3 if switch else 0


class LocalGreedyHeuristic:
    def reset(self):
        pass

    def act(self, env: ComplexTrafficEnv) -> int:
        q = env.raw_queues()
        switch_a = int((q["phase_a"] == 0 and q["a_ew"] > q["a_ns"]) or (q["phase_a"] == 1 and q["a_ns"] > q["a_ew"]))
        switch_b = int((q["phase_b"] == 0 and q["b_ew"] > q["b_ns"]) or (q["phase_b"] == 1 and q["b_ns"] > q["b_ew"]))
        return switch_a * 2 + switch_b


class ThresholdHeuristic:
    def __init__(self, threshold: int = 4):
        self.threshold = threshold

    def reset(self):
        pass

    def act(self, env: ComplexTrafficEnv) -> int:
        q = env.raw_queues()
        switch_a = int(
            (q["phase_a"] == 0 and q["a_ew"] > q["a_ns"] + self.threshold)
            or (q["phase_a"] == 1 and q["a_ns"] > q["a_ew"] + self.threshold)
        )
        switch_b = int(
            (q["phase_b"] == 0 and q["b_ew"] > q["b_ns"] + self.threshold)
            or (q["phase_b"] == 1 and q["b_ns"] > q["b_ew"] + self.threshold)
        )
        return switch_a * 2 + switch_b

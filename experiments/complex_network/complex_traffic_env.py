from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np


Action = int
State = Tuple[int, int, int, int, int, int, int, int]


@dataclass
class StepInfo:
    total_queue: float
    delay: float
    throughput: float
    switches: int
    spillback: float


class ComplexTrafficEnv:
    """Two-intersection corridor with delayed upstream-to-downstream flow.

    Phase 0 serves north-south traffic. Phase 1 serves east-west traffic.
    Vehicles served east-west at intersection A enter a transit pipeline and
    arrive at intersection B after a fixed delay.
    """

    ACTIONS = {
        0: (0, 0),  # stay, stay
        1: (0, 1),  # stay, switch B
        2: (1, 0),  # switch A, stay
        3: (1, 1),  # switch A, switch B
    }

    def __init__(
        self,
        seed: int | None = None,
        horizon: int = 180,
        max_queue: int = 42,
        service_rate: int = 4,
        transit_delay: int = 4,
        switch_penalty: float = 2.0,
        spillback_threshold: int = 28,
    ):
        self.rng = np.random.default_rng(seed)
        self.horizon = horizon
        self.max_queue = max_queue
        self.service_rate = service_rate
        self.transit_delay = transit_delay
        self.switch_penalty = switch_penalty
        self.spillback_threshold = spillback_threshold
        self.reset()

    def reset(self, seed: int | None = None) -> State:
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self.t = 0
        self.phase_a = 1
        self.phase_b = 0
        self.a_ns = int(self.rng.integers(3, 8))
        self.a_ew = int(self.rng.integers(6, 12))
        self.b_ns = int(self.rng.integers(4, 9))
        self.b_ew = int(self.rng.integers(1, 5))
        self.transit = [0 for _ in range(self.transit_delay)]
        self.last_info = StepInfo(0.0, 0.0, 0.0, 0, 0.0)
        return self.get_state()

    def demand_regime(self) -> int:
        block = (self.t // 45) % 4
        return block

    @staticmethod
    def bucket(q: int) -> int:
        if q <= 4:
            return 0
        if q <= 10:
            return 1
        if q <= 20:
            return 2
        return 3

    def get_state(self) -> State:
        return (
            self.bucket(self.a_ns),
            self.bucket(self.a_ew),
            self.bucket(self.b_ns),
            self.bucket(self.b_ew),
            self.phase_a,
            self.phase_b,
            self.bucket(sum(self.transit)),
            self.demand_regime(),
        )

    def state_vector(self) -> np.ndarray:
        state = self.get_state()
        scales = np.array([3, 3, 3, 3, 1, 1, 3, 3], dtype=np.float32)
        return np.array(state, dtype=np.float32) / scales

    def _arrivals(self) -> Tuple[int, int, int, int]:
        regime = self.demand_regime()
        # A_ew burst creates platoons that must be anticipated downstream at B.
        rates = {
            0: (1.0, 2.0, 1.0, 0.4),
            1: (1.2, 5.0, 1.0, 0.5),
            2: (4.0, 1.2, 3.0, 0.5),
            3: (1.4, 3.2, 1.0, 0.7),
        }[regime]
        return tuple(int(self.rng.poisson(rate)) for rate in rates)

    def _cap(self, q: int) -> int:
        return int(min(self.max_queue, q))

    def step(self, action: Action) -> Tuple[State, float, bool, Dict[str, float]]:
        switch_a, switch_b = self.ACTIONS[action]
        switches = int(switch_a) + int(switch_b)
        if switch_a:
            self.phase_a = 1 - self.phase_a
        if switch_b:
            self.phase_b = 1 - self.phase_b

        arriving_from_a = self.transit.pop(0)
        self.b_ew = self._cap(self.b_ew + arriving_from_a)
        self.transit.append(0)

        a_ns_arr, a_ew_arr, b_ns_arr, b_ew_arr = self._arrivals()
        self.a_ns = self._cap(self.a_ns + a_ns_arr)
        self.a_ew = self._cap(self.a_ew + a_ew_arr)
        self.b_ns = self._cap(self.b_ns + b_ns_arr)
        self.b_ew = self._cap(self.b_ew + b_ew_arr)

        throughput = 0
        released_to_corridor = 0
        if self.phase_a == 0:
            served = min(self.service_rate, self.a_ns)
            self.a_ns -= served
            throughput += served
        else:
            downstream_room = max(0, self.max_queue - self.b_ew - sum(self.transit))
            served = min(self.service_rate, self.a_ew, downstream_room)
            self.a_ew -= served
            released_to_corridor = served
            self.transit[-1] += served

        if self.phase_b == 0:
            served = min(self.service_rate, self.b_ns)
            self.b_ns -= served
            throughput += served
        else:
            served = min(self.service_rate, self.b_ew)
            self.b_ew -= served
            throughput += served

        total_queue = self.a_ns + self.a_ew + self.b_ns + self.b_ew + sum(self.transit)
        spillback = max(0, self.b_ew - self.spillback_threshold) + max(
            0, sum(self.transit) + self.b_ew - self.max_queue
        )
        delay = total_queue + 1.5 * spillback
        reward = -delay - self.switch_penalty * switches + 1.6 * throughput
        reward -= 0.7 * max(0, released_to_corridor - self.service_rate // 2) * int(self.phase_b == 0)

        self.t += 1
        done = self.t >= self.horizon
        self.last_info = StepInfo(total_queue, delay, throughput, switches, spillback)
        return self.get_state(), float(reward), done, self.last_info.__dict__.copy()

    def raw_queues(self) -> Dict[str, int]:
        return {
            "a_ns": self.a_ns,
            "a_ew": self.a_ew,
            "b_ns": self.b_ns,
            "b_ew": self.b_ew,
            "transit": sum(self.transit),
            "phase_a": self.phase_a,
            "phase_b": self.phase_b,
        }

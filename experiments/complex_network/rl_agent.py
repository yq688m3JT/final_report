from __future__ import annotations

from collections import deque, namedtuple
import random

import numpy as np
import torch
from torch import nn
from torch.optim import Adam


Transition = namedtuple("Transition", "state action reward next_state done")


class QNetwork(nn.Module):
    def __init__(self, state_dim: int = 8, action_dim: int = 4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
        )

    def forward(self, x):
        return self.net(x)


class DQNAgent:
    def __init__(
        self,
        state_dim: int = 8,
        action_dim: int = 4,
        gamma: float = 0.96,
        lr: float = 1e-3,
        batch_size: int = 64,
        replay_size: int = 20_000,
        seed: int = 19,
    ):
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        self.action_dim = action_dim
        self.gamma = gamma
        self.batch_size = batch_size
        self.policy = QNetwork(state_dim, action_dim)
        self.target = QNetwork(state_dim, action_dim)
        self.target.load_state_dict(self.policy.state_dict())
        self.optimizer = Adam(self.policy.parameters(), lr=lr)
        self.replay = deque(maxlen=replay_size)
        self.loss_fn = nn.SmoothL1Loss()

    def act(self, state: np.ndarray, epsilon: float = 0.0) -> int:
        if random.random() < epsilon:
            return random.randrange(self.action_dim)
        with torch.no_grad():
            tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            return int(torch.argmax(self.policy(tensor), dim=1).item())

    def remember(self, *args):
        self.replay.append(Transition(*args))

    def learn(self) -> float | None:
        if len(self.replay) < self.batch_size:
            return None
        batch = random.sample(self.replay, self.batch_size)
        states = torch.tensor(np.array([b.state for b in batch]), dtype=torch.float32)
        actions = torch.tensor([b.action for b in batch], dtype=torch.int64).unsqueeze(1)
        rewards = torch.tensor([b.reward for b in batch], dtype=torch.float32).unsqueeze(1)
        next_states = torch.tensor(np.array([b.next_state for b in batch]), dtype=torch.float32)
        dones = torch.tensor([b.done for b in batch], dtype=torch.float32).unsqueeze(1)

        q_values = self.policy(states).gather(1, actions)
        with torch.no_grad():
            next_actions = torch.argmax(self.policy(next_states), dim=1, keepdim=True)
            next_q = self.target(next_states).gather(1, next_actions)
            target = rewards + self.gamma * next_q * (1.0 - dones)
        loss = self.loss_fn(q_values, target)
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.policy.parameters(), 5.0)
        self.optimizer.step()
        return float(loss.item())

    def update_target(self):
        self.target.load_state_dict(self.policy.state_dict())

    def save(self, path):
        torch.save(self.policy.state_dict(), path)

    def load(self, path):
        self.policy.load_state_dict(torch.load(path, map_location="cpu", weights_only=True))
        self.target.load_state_dict(self.policy.state_dict())

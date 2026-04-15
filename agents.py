"""Tabular RL agents for the Cliff Walking environment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import numpy as np


class CliffEnvLike(Protocol):
    def reset(self) -> int: ...

    def step(self, action: int) -> tuple[int, int, bool]: ...


@dataclass
class BaseAgent:
    n_states: int
    n_actions: int
    alpha: float = 0.1
    gamma: float = 0.9
    epsilon: float = 0.1
    seed: int = 42
    rng: np.random.Generator = field(init=False)
    Q: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        self.rng = np.random.default_rng(self.seed)
        self.Q = np.zeros((self.n_states, self.n_actions), dtype=np.float64)

    def choose_action(self, state: int) -> int:
        if self.rng.random() < self.epsilon:
            return int(self.rng.integers(self.n_actions))
        return self.greedy_action(state)

    def greedy_action(self, state: int) -> int:
        q_row = self.Q[state]
        best_value = np.max(q_row)
        best_actions = np.flatnonzero(q_row == best_value)
        return int(self.rng.choice(best_actions))


class QLearningAgent(BaseAgent):
    name = "Q-learning"

    def update(self, state: int, action: int, reward: int, next_state: int, done: bool) -> None:
        target = reward if done else reward + self.gamma * np.max(self.Q[next_state])
        self.Q[state, action] += self.alpha * (target - self.Q[state, action])

    def run_episode(self, env: CliffEnvLike, max_steps: int = 1000) -> float:
        state = env.reset()
        total_reward = 0.0
        steps = 0

        while steps < max_steps:
            action = self.choose_action(state)
            next_state, reward, done = env.step(action)
            self.update(state, action, reward, next_state, done)
            total_reward += reward
            state = next_state
            steps += 1
            if done:
                break
        return total_reward


class SARSAAgent(BaseAgent):
    name = "SARSA"

    def update(
        self,
        state: int,
        action: int,
        reward: int,
        next_state: int,
        next_action: int,
        done: bool,
    ) -> None:
        target = reward if done else reward + self.gamma * self.Q[next_state, next_action]
        self.Q[state, action] += self.alpha * (target - self.Q[state, action])

    def run_episode(self, env: CliffEnvLike, max_steps: int = 1000) -> float:
        state = env.reset()
        action = self.choose_action(state)
        total_reward = 0.0
        steps = 0

        while steps < max_steps:
            next_state, reward, done = env.step(action)
            next_action = self.choose_action(next_state)
            self.update(state, action, reward, next_state, next_action, done)
            total_reward += reward
            state = next_state
            action = next_action
            steps += 1
            if done:
                break
        return total_reward

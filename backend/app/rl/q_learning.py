from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.rl.environment import PortfolioEnvironment


@dataclass(frozen=True)
class QLearningResult:
    q_table: dict[tuple[tuple[int, ...], int], float]
    episodes: int


class QLearningPortfolioAgent:
    def __init__(
        self,
        actions: list[np.ndarray],
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
        risk_penalty: float = 0.0,
        state_window: int = 5,
        seed: int = 42,
    ) -> None:
        if not actions:
            raise ValueError("Actions cannot be empty.")
        if not 0 < learning_rate <= 1:
            raise ValueError("Learning rate must be between 0 and 1.")
        if not 0 <= discount_factor <= 1:
            raise ValueError("Discount factor must be between 0 and 1.")
        if not 0 <= epsilon <= 1:
            raise ValueError("Epsilon must be between 0 and 1.")
        if risk_penalty < 0:
            raise ValueError("Risk penalty cannot be negative.")
        if state_window < 1:
            raise ValueError("State window must be positive.")

        self.actions = [np.asarray(action, dtype=float).copy() for action in actions]
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.risk_penalty = risk_penalty
        self.state_window = state_window
        self.rng = np.random.default_rng(seed)
        self.q_table: dict[tuple[tuple[int, ...], int], float] = {}

    def state(
        self,
        returns: pd.DataFrame,
        step: int,
        previous_action: int,
    ) -> tuple[tuple[int, ...], int]:
        start = max(0, step - self.state_window)
        history = returns.iloc[start:step]

        if history.empty:
            regime = np.zeros(returns.shape[1], dtype=int)
        else:
            means = history.mean(axis=0).to_numpy(dtype=float)
            regime = np.sign(means).astype(int)

        return tuple(regime.tolist()), previous_action

    def select_action(
        self,
        state: tuple[tuple[int, ...], int],
        explore: bool = False,
    ) -> int:
        if explore and self.rng.random() < self.epsilon:
            return int(self.rng.integers(len(self.actions)))

        values = [
            self.q_table.get((state[0], action), 0.0)
            for action in range(len(self.actions))
        ]
        return int(np.argmax(values))

    def train(
        self,
        returns: pd.DataFrame,
        initial_capital: float = 100_000.0,
        transaction_cost_bps: float = 5.0,
        episodes: int = 20,
    ) -> QLearningResult:
        if returns.empty:
            raise ValueError("Training returns cannot be empty.")
        if episodes < 1:
            raise ValueError("Episodes must be positive.")

        self.q_table = {}

        for _ in range(episodes):
            env = PortfolioEnvironment(
                returns,
                initial_capital=initial_capital,
                transaction_cost_bps=transaction_cost_bps,
            )
            previous_action = 0
            history_rewards: list[float] = []

            for step in range(len(returns)):
                current_state = self.state(
                    returns,
                    step,
                    previous_action,
                )

                action_index = self.select_action(
                    current_state,
                    explore=True,
                )

                _, reward, done = env.step(self.actions[action_index])

                if self.risk_penalty and history_rewards:
                    risk = float(np.std(history_rewards))
                    reward -= self.risk_penalty * risk

                history_rewards.append(reward)

                next_action = action_index
                next_state = self.state(
                    returns,
                    step + 1,
                    next_action,
                )

                current_q = self.q_table.get(
                    (current_state[0], action_index),
                    0.0,
                )
                next_q = max(
                    (
                        self.q_table.get(
                            (next_state[0], candidate),
                            0.0,
                        )
                        for candidate in range(len(self.actions))
                    ),
                    default=0.0,
                )

                target = reward
                if not done:
                    target += self.discount_factor * next_q

                self.q_table[(current_state[0], action_index)] = (
                    current_q
                    + self.learning_rate * (target - current_q)
                )

                previous_action = next_action

                if done:
                    break

        return QLearningResult(
            q_table=self.q_table.copy(),
            episodes=episodes,
        )

    def evaluate(
        self,
        returns: pd.DataFrame,
        initial_capital: float = 100_000.0,
        transaction_cost_bps: float = 5.0,
    ) -> tuple[float, float, float, float]:
        if returns.empty:
            raise ValueError("Evaluation returns cannot be empty.")

        env = PortfolioEnvironment(
            returns,
            initial_capital=initial_capital,
            transaction_cost_bps=transaction_cost_bps,
        )

        previous_action = 0
        rewards: list[float] = []
        total_turnover = 0.0

        for step in range(len(returns)):
            state = self.state(
                returns,
                step,
                previous_action,
            )
            action_index = self.select_action(state)
            previous_weights = env.weights.copy()
            _, reward, done = env.step(self.actions[action_index])
            rewards.append(reward)
            total_turnover += float(
                np.abs(self.actions[action_index] - previous_weights).sum()
            )
            previous_action = action_index

            if done:
                break

        final_value = env.portfolio_value
        cumulative_return = (final_value / initial_capital) - 1.0
        average_reward = float(np.mean(rewards))

        return final_value, cumulative_return, average_reward, total_turnover

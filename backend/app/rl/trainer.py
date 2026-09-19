from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.rl.agent import DiscretePortfolioAgent
from app.rl.environment import PortfolioEnvironment


@dataclass(frozen=True)
class RLEvaluation:
    final_value: float
    cumulative_return: float
    average_reward: float
    total_turnover: float
    rewards: np.ndarray


@dataclass(frozen=True)
class RLTrainingResult:
    selected_action: int
    training_rewards: dict[int, float]


def evaluate_agent(
    returns: pd.DataFrame,
    agent: DiscretePortfolioAgent,
    action_index: int,
    initial_capital: float = 100_000.0,
    transaction_cost_bps: float = 5.0,
) -> RLEvaluation:
    if returns.empty:
        raise ValueError("Returns cannot be empty.")

    env = PortfolioEnvironment(
        returns,
        initial_capital=initial_capital,
        transaction_cost_bps=transaction_cost_bps,
    )

    action = agent.select_action(action_index).weights
    rewards: list[float] = []
    turnovers: list[float] = []

    for _ in range(len(returns)):
        previous_weights = env.weights.copy()
        _, reward, done = env.step(action)

        rewards.append(reward)
        turnovers.append(
            float(np.abs(action - previous_weights).sum())
        )

        if done:
            break

    final_value = env.portfolio_value

    return RLEvaluation(
        final_value=final_value,
        cumulative_return=(final_value / initial_capital) - 1.0,
        average_reward=float(np.mean(rewards)),
        total_turnover=float(np.sum(turnovers)),
        rewards=np.asarray(rewards, dtype=float),
    )


def train_discrete_agent(
    train_returns: pd.DataFrame,
    actions: list[np.ndarray],
    initial_capital: float = 100_000.0,
    transaction_cost_bps: float = 5.0,
) -> tuple[DiscretePortfolioAgent, RLTrainingResult]:
    if train_returns.empty:
        raise ValueError("Training returns cannot be empty.")

    agent = DiscretePortfolioAgent(actions)
    training_rewards: dict[int, float] = {}

    for index in range(len(actions)):
        evaluation = evaluate_agent(
            train_returns,
            agent,
            action_index=index,
            initial_capital=initial_capital,
            transaction_cost_bps=transaction_cost_bps,
        )
        training_rewards[index] = evaluation.cumulative_return

    selected_action = max(
        training_rewards,
        key=training_rewards.get,
    )

    return agent, RLTrainingResult(
        selected_action=selected_action,
        training_rewards=training_rewards,
    )

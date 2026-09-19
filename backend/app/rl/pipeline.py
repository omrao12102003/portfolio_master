from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.rl.agent import DiscretePortfolioAgent
from app.rl.q_learning import QLearningPortfolioAgent
from app.rl.split import chronological_split
from app.rl.trainer import RLEvaluation, evaluate_agent


@dataclass(frozen=True)
class RLPipelineResult:
    selected_action: int
    training_rewards: dict[int, float]
    validation: RLEvaluation
    test: RLEvaluation
    q_learning_validation: RLEvaluation
    q_learning_test: RLEvaluation


def run_rl_pipeline(
    returns: pd.DataFrame,
    actions: list[np.ndarray],
    initial_capital: float = 100_000.0,
    transaction_cost_bps: float = 5.0,
) -> RLPipelineResult:
    split = chronological_split(returns)

    agent = DiscretePortfolioAgent(actions)

    training_rewards: dict[int, float] = {}

    for index in range(len(actions)):
        evaluation = evaluate_agent(
            split.train,
            agent,
            index,
            initial_capital=initial_capital,
            transaction_cost_bps=transaction_cost_bps,
        )
        training_rewards[index] = evaluation.cumulative_return

    selected_action = max(
        training_rewards,
        key=training_rewards.get,
    )

    validation = evaluate_agent(
        split.validation,
        agent,
        selected_action,
        initial_capital=initial_capital,
        transaction_cost_bps=transaction_cost_bps,
    )

    test = evaluate_agent(
        split.test,
        agent,
        selected_action,
        initial_capital=initial_capital,
        transaction_cost_bps=transaction_cost_bps,
    )

    q_agent = QLearningPortfolioAgent(actions)
    q_agent.train(
        split.train,
        initial_capital=initial_capital,
        transaction_cost_bps=transaction_cost_bps,
        episodes=30,
    )

    (
        q_validation_value,
        q_validation_return,
        q_validation_reward,
        q_validation_turnover,
    ) = q_agent.evaluate(
        split.validation,
        initial_capital=initial_capital,
        transaction_cost_bps=transaction_cost_bps,
    )

    (
        q_test_value,
        q_test_return,
        q_test_reward,
        q_test_turnover,
    ) = q_agent.evaluate(
        split.test,
        initial_capital=initial_capital,
        transaction_cost_bps=transaction_cost_bps,
    )

    q_learning_validation = RLEvaluation(
        final_value=q_validation_value,
        cumulative_return=q_validation_return,
        average_reward=q_validation_reward,
        total_turnover=q_validation_turnover,
        rewards=np.array([], dtype=float),
    )

    q_learning_test = RLEvaluation(
        final_value=q_test_value,
        cumulative_return=q_test_return,
        average_reward=q_test_reward,
        total_turnover=q_test_turnover,
        rewards=np.array([], dtype=float),
    )

    return RLPipelineResult(
        selected_action=selected_action,
        training_rewards=training_rewards,
        validation=validation,
        test=test,
        q_learning_validation=q_learning_validation,
        q_learning_test=q_learning_test,
    )

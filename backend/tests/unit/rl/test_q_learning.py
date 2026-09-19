import numpy as np
import pandas as pd

from app.rl.q_learning import QLearningPortfolioAgent


def test_q_learning_produces_state_dependent_policy():
    returns = pd.DataFrame(
        [
            [0.03, -0.01],
            [0.02, -0.02],
            [0.025, -0.01],
            [-0.02, 0.03],
            [-0.01, 0.025],
            [-0.02, 0.03],
            [0.02, -0.01],
            [0.025, -0.02],
        ],
        columns=["A", "B"],
    )

    agent = QLearningPortfolioAgent(
        [
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0]),
        ],
        epsilon=0.2,
        seed=7,
    )

    result = agent.train(
        returns,
        episodes=30,
    )

    assert result.episodes == 30
    assert result.q_table

    positive_state = agent.state(returns, 2, 0)
    negative_state = agent.state(returns, 5, 0)

    assert positive_state != negative_state


def test_q_learning_evaluation_returns_valid_metrics():
    returns = pd.DataFrame(
        [
            [0.01, 0.02],
            [0.02, 0.01],
            [0.01, 0.03],
            [0.02, 0.01],
            [0.01, 0.02],
            [0.02, 0.01],
        ],
        columns=["A", "B"],
    )

    agent = QLearningPortfolioAgent(
        [
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0]),
        ]
    )

    agent.train(returns, episodes=5)

    final_value, cumulative_return, average_reward, turnover = agent.evaluate(
        returns
    )

    assert final_value > 0
    assert np.isfinite(cumulative_return)
    assert np.isfinite(average_reward)
    assert turnover >= 0

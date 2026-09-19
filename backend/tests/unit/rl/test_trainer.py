import numpy as np
import pandas as pd
import pytest

from app.rl.agent import DiscretePortfolioAgent
from app.rl.trainer import evaluate_agent


def test_evaluate_agent():
    returns = pd.DataFrame(
        [
            [0.01, 0.02],
            [0.02, 0.01],
            [-0.01, 0.03],
        ],
        columns=["A", "B"],
    )

    agent = DiscretePortfolioAgent(
        [
            np.array([0.5, 0.5]),
            np.array([1.0, 0.0]),
        ]
    )

    result = evaluate_agent(
        returns,
        agent,
        action_index=0,
        transaction_cost_bps=0,
    )

    assert result.final_value > 100_000
    assert result.cumulative_return > 0
    assert result.average_reward > 0
    assert len(result.rewards) == 3


def test_evaluate_agent_rejects_empty_returns():
    returns = pd.DataFrame(columns=["A", "B"])

    agent = DiscretePortfolioAgent(
        [np.array([0.5, 0.5])]
    )

    with pytest.raises(ValueError, match="Returns cannot be empty"):
        evaluate_agent(returns, agent, 0)

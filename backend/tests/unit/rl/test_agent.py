import numpy as np
import pytest

from app.rl.agent import DiscretePortfolioAgent


def test_discrete_agent_selects_action():
    actions = [
        np.array([1.0, 0.0]),
        np.array([0.5, 0.5]),
    ]

    agent = DiscretePortfolioAgent(actions)

    result = agent.select_action(1)

    assert np.allclose(result.weights, [0.5, 0.5])


def test_agent_rejects_invalid_action():
    with pytest.raises(ValueError, match="sum to 1"):
        DiscretePortfolioAgent(
            [np.array([0.2, 0.2])]
        )

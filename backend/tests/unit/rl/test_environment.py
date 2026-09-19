import numpy as np
import pandas as pd
import pytest

from app.rl.environment import PortfolioEnvironment


def test_environment_reset():
    returns = pd.DataFrame(
        [[0.01, 0.02], [0.02, -0.01]],
        columns=["A", "B"],
    )

    env = PortfolioEnvironment(returns)
    state = env.reset()

    assert state.step == 0
    assert state.portfolio_value == 100_000
    assert np.allclose(state.weights, [0.5, 0.5])


def test_environment_step():
    returns = pd.DataFrame(
        [[0.01, 0.02], [0.02, -0.01]],
        columns=["A", "B"],
    )

    env = PortfolioEnvironment(
        returns,
        transaction_cost_bps=0,
    )

    _, reward, done = env.step(np.array([0.25, 0.75]))

    assert reward == pytest.approx(0.0175)
    assert not done


def test_environment_rejects_invalid_weights():
    returns = pd.DataFrame(
        [[0.01, 0.02], [0.02, -0.01]],
        columns=["A", "B"],
    )

    env = PortfolioEnvironment(returns)

    with pytest.raises(ValueError, match="sum to 1"):
        env.step(np.array([0.2, 0.2]))


def test_environment_transaction_cost():
    returns = pd.DataFrame(
        [[0.01, 0.02], [0.02, -0.01]],
        columns=["A", "B"],
    )

    env = PortfolioEnvironment(
        returns,
        transaction_cost_bps=100,
    )

    _, reward, _ = env.step(np.array([0.8, 0.2]))

    assert reward < 0.015

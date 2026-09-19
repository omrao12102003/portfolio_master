import pytest

from app.rl.rewards import portfolio_reward


def test_portfolio_reward():
    result = portfolio_reward(
        portfolio_return=0.02,
        transaction_cost=0.001,
        risk_penalty=0.002,
        turnover_penalty=0.001,
    )

    assert result == pytest.approx(0.016)

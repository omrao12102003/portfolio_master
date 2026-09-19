import numpy as np
import pandas as pd
import pytest

from app.backtest.engine import (
    backtest_summary,
    run_backtest,
    validate_prices,
    validate_target_weights,
)


@pytest.fixture
def prices():
    return pd.DataFrame(
        {
            "A": [100.0, 102.0, 101.0, 104.0, 106.0],
            "B": [100.0, 101.0, 103.0, 102.0, 105.0],
        },
        index=pd.date_range("2026-01-05", periods=5, freq="B"),
    )


@pytest.fixture
def weights():
    return pd.Series({"A": 0.6, "B": 0.4})


def test_backtest_runs(prices, weights):
    result = run_backtest(
        prices,
        weights,
        initial_capital=100_000,
        transaction_cost_bps=0,
    )

    assert len(result.equity_curve) == len(prices)
    assert len(result.portfolio_returns) == len(prices)
    assert result.equity_curve.iloc[0] == pytest.approx(100_000)
    assert result.equity_curve.iloc[-1] > 0


def test_weights_sum_to_target(prices, weights):
    result = run_backtest(
        prices,
        weights,
        transaction_cost_bps=0,
    )

    assert result.weights.sum(axis=1).to_numpy() == pytest.approx(1.0)


def test_transaction_costs_reduce_equity(prices, weights):
    free = run_backtest(
        prices,
        weights,
        transaction_cost_bps=0,
    )

    costly = run_backtest(
        prices,
        weights,
        transaction_cost_bps=100,
    )

    assert costly.equity_curve.iloc[-1] < free.equity_curve.iloc[-1]
    assert costly.transaction_costs.sum() > 0


def test_daily_rebalancing(prices, weights):
    result = run_backtest(
        prices,
        weights,
        transaction_cost_bps=0,
        rebalance_frequency="daily",
    )

    assert result.turnover.iloc[0] == pytest.approx(1.0)
    assert (result.turnover.iloc[1:] > 0).all()


def test_weekly_rebalancing(prices, weights):
    result = run_backtest(
        prices,
        weights,
        transaction_cost_bps=0,
        rebalance_frequency="weekly",
    )

    assert result.turnover.iloc[0] == pytest.approx(1.0)
    assert result.turnover.iloc[1:].sum() == pytest.approx(0.0)


def test_monthly_rebalancing(prices, weights):
    result = run_backtest(
        prices,
        weights,
        transaction_cost_bps=0,
        rebalance_frequency="monthly",
    )

    assert result.turnover.iloc[0] == pytest.approx(1.0)
    assert result.turnover.iloc[1:].sum() == pytest.approx(0.0)


def test_summary(prices, weights):
    result = run_backtest(prices, weights, transaction_cost_bps=0)
    summary = backtest_summary(result)

    assert summary["initial_capital"] == pytest.approx(100_000)
    assert summary["final_capital"] > 0
    assert "maximum_drawdown" in summary
    assert "annualized_volatility" in summary


def test_validation(prices, weights):
    with pytest.raises(ValueError):
        validate_prices(pd.DataFrame())

    bad_prices = prices.copy()
    bad_prices.iloc[0, 0] = np.nan

    with pytest.raises(ValueError):
        validate_prices(bad_prices)

    with pytest.raises(ValueError):
        validate_target_weights(pd.Series({"A": 0.5, "B": 0.4}))

    with pytest.raises(ValueError):
        validate_target_weights(pd.Series({"A": -0.1, "B": 1.1}))


def test_invalid_parameters(prices, weights):
    with pytest.raises(ValueError):
        run_backtest(prices, weights, initial_capital=0)

    with pytest.raises(ValueError):
        run_backtest(prices, weights, transaction_cost_bps=-1)

    with pytest.raises(ValueError):
        run_backtest(
            prices,
            pd.Series({"A": 0.5, "C": 0.5}),
        )

    with pytest.raises(ValueError):
        run_backtest(
            prices,
            weights,
            rebalance_frequency="hourly",
        )

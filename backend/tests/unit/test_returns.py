import numpy as np
import pandas as pd
import pytest

from app.analytics.returns import (
    annualized_return,
    annualized_volatility,
    cumulative_returns,
    downside_volatility,
    drawdown,
    log_returns,
    maximum_drawdown,
    rolling_volatility,
    sharpe_ratio,
    simple_returns,
    sortino_ratio,
)


@pytest.fixture
def prices():
    return pd.Series([100.0, 110.0, 99.0, 108.9])


@pytest.fixture
def returns():
    return pd.Series([0.01, -0.02, 0.03, -0.01, 0.02])


def test_simple_returns(prices):
    result = simple_returns(prices)

    assert pd.isna(result.iloc[0])
    assert result.iloc[1] == pytest.approx(0.10)
    assert result.iloc[2] == pytest.approx(-0.10)


def test_log_returns(prices):
    result = log_returns(prices)

    assert pd.isna(result.iloc[0])
    assert result.iloc[1] == pytest.approx(np.log(1.10))


def test_log_returns_rejects_non_positive_prices():
    with pytest.raises(ValueError, match="positive"):
        log_returns(pd.Series([100.0, 0.0, 101.0]))


def test_cumulative_returns(returns):
    result = cumulative_returns(returns)

    expected = (1 + returns).cumprod() - 1
    pd.testing.assert_series_equal(result, expected)


def test_annualized_return():
    returns = pd.Series([0.01, 0.01, 0.01, 0.01])

    result = annualized_return(returns, periods_per_year=4)

    assert result == pytest.approx((1.01**4) ** (4 / 4) - 1)


def test_annualized_volatility(returns):
    result = annualized_volatility(returns, periods_per_year=252)

    assert result > 0


def test_downside_volatility(returns):
    result = downside_volatility(returns, periods_per_year=252)

    assert result > 0


def test_sharpe_ratio(returns):
    result = sharpe_ratio(
        returns,
        risk_free_rate=0.0,
        periods_per_year=252,
    )

    assert np.isfinite(result)


def test_sortino_ratio(returns):
    result = sortino_ratio(
        returns,
        risk_free_rate=0.0,
        periods_per_year=252,
    )

    assert np.isfinite(result)


def test_drawdown():
    returns = pd.Series([0.10, -0.05, -0.10, 0.20])

    result = drawdown(returns)

    assert result.iloc[0] == pytest.approx(0.0)
    assert result.min() < 0


def test_maximum_drawdown():
    returns = pd.Series([0.10, -0.05, -0.10, 0.20])

    result = maximum_drawdown(returns)

    assert result < 0


def test_rolling_volatility(returns):
    result = rolling_volatility(
        returns,
        window=3,
        periods_per_year=252,
    )

    assert pd.isna(result.iloc[0])
    assert pd.isna(result.iloc[1])
    assert np.isfinite(result.iloc[2])


def test_rolling_volatility_rejects_invalid_window(returns):
    with pytest.raises(ValueError, match="greater than 1"):
        rolling_volatility(returns, window=1)


def test_annualized_return_empty():
    result = annualized_return(pd.Series(dtype=float))
    assert np.isnan(result)


def test_annualized_return_invalid_growth():
    result = annualized_return(pd.Series([-1.0]))
    assert np.isnan(result)


def test_annualized_volatility_insufficient_data():
    result = annualized_volatility(pd.Series([0.01]))
    assert np.isnan(result)


def test_downside_volatility_empty():
    result = downside_volatility(pd.Series(dtype=float))
    assert np.isnan(result)


def test_sharpe_ratio_insufficient_data():
    result = sharpe_ratio(pd.Series([0.01]))
    assert np.isnan(result)


def test_sharpe_ratio_zero_volatility():
    result = sharpe_ratio(pd.Series([0.01, 0.01, 0.01]))
    assert np.isnan(result)


def test_sortino_ratio_zero_downside():
    result = sortino_ratio(pd.Series([0.01, 0.02, 0.03]))
    assert np.isnan(result)


def test_maximum_drawdown_empty():
    result = maximum_drawdown(pd.Series(dtype=float))
    assert np.isnan(result)


def test_rolling_volatility_short_series():
    result = rolling_volatility(
        pd.Series([0.01]),
        window=3,
    )
    assert pd.isna(result.iloc[0])


def test_sortino_ratio_empty():
    result = sortino_ratio(pd.Series(dtype=float))
    assert np.isnan(result)

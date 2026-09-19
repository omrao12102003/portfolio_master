import numpy as np
import pandas as pd
import pytest

from app.analytics.portfolio import (
    correlation_matrix,
    covariance_matrix,
    mean_returns,
    portfolio_return,
    portfolio_sharpe,
    portfolio_volatility,
    validate_weights,
)


@pytest.fixture
def returns():
    return pd.DataFrame(
        {
            "AAPL": [0.01, -0.02, 0.03, 0.01],
            "MSFT": [0.02, 0.01, -0.01, 0.02],
            "SPY": [0.015, -0.005, 0.02, 0.01],
        }
    )


@pytest.fixture
def weights():
    return pd.Series(
        {"AAPL": 0.4, "MSFT": 0.4, "SPY": 0.2}
    )


def test_mean_returns(returns):
    result = mean_returns(returns, periods_per_year=252)

    assert list(result.index) == ["AAPL", "MSFT", "SPY"]
    assert result["AAPL"] == pytest.approx(0.03 * 252 / 4)


def test_covariance_matrix(returns):
    result = covariance_matrix(returns, periods_per_year=252)

    assert result.shape == (3, 3)
    assert list(result.index) == list(returns.columns)
    assert np.allclose(result.values, result.values.T)


def test_correlation_matrix(returns):
    result = correlation_matrix(returns)

    assert result.shape == (3, 3)
    assert np.allclose(np.diag(result), 1.0)


def test_validate_weights_accepts_valid_weights(weights):
    validate_weights(weights)


def test_validate_weights_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        validate_weights(pd.Series(dtype=float))


def test_validate_weights_rejects_missing():
    weights = pd.Series({"AAPL": 0.5, "MSFT": np.nan})

    with pytest.raises(ValueError, match="missing"):
        validate_weights(weights)


def test_validate_weights_rejects_sum_not_one():
    weights = pd.Series({"AAPL": 0.4, "MSFT": 0.4})

    with pytest.raises(ValueError, match="sum to 1"):
        validate_weights(weights)


def test_validate_weights_rejects_negative():
    weights = pd.Series({"AAPL": 1.2, "MSFT": -0.2})

    with pytest.raises(ValueError, match="Negative"):
        validate_weights(weights)


def test_portfolio_return(weights):
    expected = pd.Series(
        {"AAPL": 0.08, "MSFT": 0.06, "SPY": 0.04}
    )

    result = portfolio_return(weights, expected)

    assert result == pytest.approx(0.064)


def test_portfolio_return_rejects_mismatched_assets(weights):
    expected = pd.Series({"AAPL": 0.08, "MSFT": 0.06})

    with pytest.raises(ValueError, match="same assets"):
        portfolio_return(weights, expected)


def test_portfolio_volatility(weights, returns):
    covariance = covariance_matrix(returns)

    result = portfolio_volatility(weights, covariance)

    assert result >= 0


def test_portfolio_volatility_rejects_mismatched_assets(weights, returns):
    covariance = covariance_matrix(returns).drop(columns=["SPY"])

    with pytest.raises(ValueError, match="assets"):
        portfolio_volatility(weights, covariance)


def test_portfolio_sharpe(weights, returns):
    expected = mean_returns(returns)
    covariance = covariance_matrix(returns)

    result = portfolio_sharpe(
        weights,
        expected,
        covariance,
        risk_free_rate=0.02,
    )

    assert np.isfinite(result)


def test_portfolio_sharpe_zero_volatility():
    weights = pd.Series({"AAPL": 1.0})
    expected = pd.Series({"AAPL": 0.05})
    covariance = pd.DataFrame([[0.0]], index=["AAPL"], columns=["AAPL"])

    result = portfolio_sharpe(weights, expected, covariance)

    assert np.isnan(result)

import numpy as np
import pandas as pd
import pytest

from app.risk.metrics import (
    beta,
    component_risk_contribution,
    concentration,
    expected_shortfall,
    historical_var,
    marginal_risk_contribution,
    parametric_var,
    percentage_risk_contribution,
    tracking_error,
)


def test_historical_var():
    returns = pd.Series([-0.10, -0.05, 0.01, 0.02, 0.04])
    assert historical_var(returns, 0.8) == pytest.approx(0.06)


def test_parametric_var():
    returns = pd.Series([-0.02, -0.01, 0.0, 0.01, 0.02])
    result = parametric_var(returns, 0.95)
    assert result >= 0


def test_expected_shortfall():
    returns = pd.Series([-0.10, -0.05, 0.01, 0.02, 0.04])
    assert expected_shortfall(returns, 0.8) == pytest.approx(0.10)


def test_beta():
    benchmark = pd.Series([0.01, -0.02, 0.03, 0.02])
    asset = benchmark * 1.5
    assert beta(asset, benchmark) == pytest.approx(1.5)


def test_tracking_error():
    portfolio = pd.Series([0.02, 0.01, 0.03, 0.00])
    benchmark = pd.Series([0.01, 0.01, 0.02, 0.00])
    result = tracking_error(portfolio, benchmark)
    assert result >= 0


def test_concentration():
    weights = pd.Series({"A": 0.5, "B": 0.3, "C": 0.2})
    assert concentration(weights) == pytest.approx(0.38)


def test_risk_contributions_sum_to_portfolio_volatility():
    weights = pd.Series({"A": 0.6, "B": 0.4})
    covariance = pd.DataFrame(
        [[0.04, 0.01], [0.01, 0.09]],
        index=weights.index,
        columns=weights.index,
    )

    component = component_risk_contribution(weights, covariance)
    portfolio_vol = np.sqrt(weights.values @ covariance.values @ weights.values)

    assert component.sum() == pytest.approx(portfolio_vol)


def test_percentage_risk_contribution_sums_to_one():
    weights = pd.Series({"A": 0.6, "B": 0.4})
    covariance = pd.DataFrame(
        [[0.04, 0.01], [0.01, 0.09]],
        index=weights.index,
        columns=weights.index,
    )

    result = percentage_risk_contribution(weights, covariance)
    assert result.sum() == pytest.approx(1.0)


def test_invalid_confidence_level():
    returns = pd.Series([0.01, -0.02, 0.03])

    with pytest.raises(ValueError):
        historical_var(returns, 1.0)

    with pytest.raises(ValueError):
        parametric_var(returns, 0.0)

    with pytest.raises(ValueError):
        expected_shortfall(returns, -0.1)


def test_empty_returns():
    returns = pd.Series(dtype=float)

    with pytest.raises(ValueError):
        historical_var(returns)

    with pytest.raises(ValueError):
        parametric_var(returns)

    with pytest.raises(ValueError):
        expected_shortfall(returns)


def test_invalid_beta():
    asset = pd.Series([0.01, 0.02, 0.03])
    benchmark = pd.Series([0.01, 0.01, 0.01])

    with pytest.raises(ValueError):
        beta(asset, benchmark)


def test_invalid_tracking_error():
    with pytest.raises(ValueError):
        tracking_error(
            pd.Series(dtype=float),
            pd.Series(dtype=float),
        )


def test_invalid_concentration():
    with pytest.raises(ValueError):
        concentration(pd.Series(dtype=float))

    with pytest.raises(ValueError):
        concentration(pd.Series({"A": 0.6, "B": -0.1}))

    with pytest.raises(ValueError):
        concentration(pd.Series({"A": 0.6, "B": 0.3}))


def test_invalid_risk_contribution():
    weights = pd.Series({"A": 0.5, "B": 0.5})
    bad_covariance = pd.DataFrame([[1.0]], index=["A"], columns=["A"])

    with pytest.raises(ValueError):
        marginal_risk_contribution(weights, bad_covariance)

    zero_covariance = pd.DataFrame(
        [[0.0, 0.0], [0.0, 0.0]],
        index=weights.index,
        columns=weights.index,
    )

    with pytest.raises(ValueError):
        marginal_risk_contribution(weights, zero_covariance)

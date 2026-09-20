import numpy as np
import pytest

from app.risk.advanced import (
    FactorRiskResult,
    MonteCarloRiskResult,
    RiskAttributionResult,
    StressTestResult,
    factor_risk,
    monte_carlo_var,
    risk_attribution,
    stress_test,
)


def test_monte_carlo_var_returns_risk_estimates():
    rng = np.random.default_rng(42)
    returns = rng.normal(0.0005, 0.01, 500)

    result = monte_carlo_var(
        returns,
        confidence=0.95,
        simulations=5000,
        seed=42,
    )

    assert isinstance(result, MonteCarloRiskResult)
    assert result.var > 0
    assert result.expected_shortfall >= result.var
    assert len(result.simulated_returns) == 5000
    assert result.confidence == 0.95
    assert result.simulations == 5000


def test_monte_carlo_var_is_reproducible():
    rng = np.random.default_rng(10)
    returns = rng.normal(0, 0.01, 200)

    first = monte_carlo_var(returns, simulations=2000, seed=7)
    second = monte_carlo_var(returns, simulations=2000, seed=7)

    assert first.var == pytest.approx(second.var)
    assert first.expected_shortfall == pytest.approx(
        second.expected_shortfall
    )


def test_monte_carlo_var_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="thirty observations"):
        monte_carlo_var(np.ones(20) * 0.01)

    with pytest.raises(ValueError, match="between 0 and 1"):
        monte_carlo_var(
            np.random.default_rng(1).normal(0, 0.01, 50),
            confidence=1.0,
        )

    with pytest.raises(ValueError, match="one hundred"):
        monte_carlo_var(
            np.random.default_rng(1).normal(0, 0.01, 50),
            simulations=99,
        )


def test_stress_test_calculates_portfolio_impact():
    result = stress_test(
        np.array([0.5, 0.3, 0.2]),
        np.array([-0.10, -0.20, 0.05]),
        "market_crash",
    )

    assert isinstance(result, StressTestResult)
    assert result.portfolio_return == pytest.approx(-0.10)
    assert result.scenario_name == "market_crash"


def test_stress_test_rejects_invalid_weights():
    with pytest.raises(ValueError, match="sum to one"):
        stress_test(
            np.array([0.5, 0.3]),
            np.array([-0.1, -0.2]),
        )


def test_factor_risk_decomposes_systematic_and_idiosyncratic_risk():
    exposures = np.array([1.2, 0.5])
    covariance = np.array(
        [
            [0.04, 0.01],
            [0.01, 0.025],
        ]
    )

    result = factor_risk(
        exposures,
        covariance,
        residual_variance=0.01,
    )

    assert isinstance(result, FactorRiskResult)
    assert result.systematic_variance > 0
    assert result.idiosyncratic_variance == pytest.approx(0.01)
    assert result.total_variance == pytest.approx(
        result.systematic_variance + 0.01
    )
    assert result.systematic_percentage + result.idiosyncratic_percentage == pytest.approx(
        1.0
    )


def test_factor_risk_rejects_dimension_mismatch():
    with pytest.raises(ValueError, match="dimensions"):
        factor_risk(
            np.array([1.0, 0.5]),
            np.eye(3),
            0.01,
        )


def test_risk_attribution_components_sum_to_total_risk():
    weights = np.array([0.5, 0.3, 0.2])
    covariance = np.array(
        [
            [0.04, 0.01, 0.005],
            [0.01, 0.025, 0.003],
            [0.005, 0.003, 0.016],
        ]
    )

    result = risk_attribution(weights, covariance)

    assert isinstance(result, RiskAttributionResult)
    assert result.total_risk > 0
    assert np.sum(result.component_contributions) == pytest.approx(
        result.total_risk
    )
    assert np.sum(result.percentage_contributions) == pytest.approx(1.0)


def test_risk_attribution_rejects_invalid_covariance():
    with pytest.raises(ValueError, match="dimensions"):
        risk_attribution(
            np.array([0.5, 0.5]),
            np.eye(3),
        )

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MonteCarloRiskResult:
    var: float
    expected_shortfall: float
    simulated_returns: np.ndarray
    confidence: float
    simulations: int


@dataclass(frozen=True)
class StressTestResult:
    portfolio_return: float
    asset_returns: np.ndarray
    scenario_name: str


@dataclass(frozen=True)
class FactorRiskResult:
    factor_contributions: np.ndarray
    systematic_variance: float
    idiosyncratic_variance: float
    total_variance: float
    systematic_percentage: float
    idiosyncratic_percentage: float


@dataclass(frozen=True)
class RiskAttributionResult:
    marginal_contributions: np.ndarray
    component_contributions: np.ndarray
    percentage_contributions: np.ndarray
    total_risk: float


def monte_carlo_var(
    returns: np.ndarray,
    confidence: float = 0.95,
    simulations: int = 10_000,
    seed: int | None = 42,
) -> MonteCarloRiskResult:
    values = np.asarray(returns, dtype=float)

    if values.ndim != 1:
        raise ValueError("Returns must be one-dimensional.")

    if len(values) < 30:
        raise ValueError("At least thirty observations are required.")

    if not np.isfinite(values).all():
        raise ValueError("Returns must contain only finite values.")

    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1.")

    if simulations < 100:
        raise ValueError("At least one hundred simulations are required.")

    mean = float(np.mean(values))
    volatility = float(np.std(values, ddof=1))

    if volatility <= 0:
        raise ValueError("Returns must have positive variance.")

    rng = np.random.default_rng(seed)
    simulated = rng.normal(mean, volatility, simulations)

    var = float(-np.quantile(simulated, 1.0 - confidence))

    tail = simulated[simulated <= np.quantile(simulated, 1.0 - confidence)]

    if len(tail) == 0:
        raise ValueError("Simulation produced no tail observations.")

    expected_shortfall = float(-np.mean(tail))

    return MonteCarloRiskResult(
        var=var,
        expected_shortfall=expected_shortfall,
        simulated_returns=simulated,
        confidence=confidence,
        simulations=simulations,
    )


def stress_test(
    weights: np.ndarray,
    scenario_returns: np.ndarray,
    scenario_name: str = "custom",
) -> StressTestResult:
    portfolio_weights = np.asarray(weights, dtype=float)
    asset_returns = np.asarray(scenario_returns, dtype=float)

    if portfolio_weights.ndim != 1 or asset_returns.ndim != 1:
        raise ValueError("Weights and scenario returns must be one-dimensional.")

    if len(portfolio_weights) != len(asset_returns):
        raise ValueError("Weights and scenario returns must have equal length.")

    if len(portfolio_weights) == 0:
        raise ValueError("At least one asset is required.")

    if not np.isfinite(portfolio_weights).all():
        raise ValueError("Weights must contain only finite values.")

    if not np.isfinite(asset_returns).all():
        raise ValueError("Scenario returns must contain only finite values.")

    if not np.isclose(np.sum(portfolio_weights), 1.0):
        raise ValueError("Weights must sum to one.")

    portfolio_return = float(np.dot(portfolio_weights, asset_returns))

    return StressTestResult(
        portfolio_return=portfolio_return,
        asset_returns=asset_returns,
        scenario_name=scenario_name,
    )


def factor_risk(
    factor_exposures: np.ndarray,
    factor_covariance: np.ndarray,
    residual_variance: float,
) -> FactorRiskResult:
    exposures = np.asarray(factor_exposures, dtype=float)
    covariance = np.asarray(factor_covariance, dtype=float)

    if exposures.ndim != 1:
        raise ValueError("Factor exposures must be one-dimensional.")

    if covariance.ndim != 2:
        raise ValueError("Factor covariance must be two-dimensional.")

    if covariance.shape != (len(exposures), len(exposures)):
        raise ValueError("Factor covariance dimensions must match exposures.")

    if not np.isfinite(exposures).all():
        raise ValueError("Factor exposures must contain only finite values.")

    if not np.isfinite(covariance).all():
        raise ValueError("Factor covariance must contain only finite values.")

    if residual_variance < 0 or not np.isfinite(residual_variance):
        raise ValueError("Residual variance must be finite and non-negative.")

    systematic_variance = float(exposures @ covariance @ exposures)

    if systematic_variance < -1e-12:
        raise ValueError("Factor covariance produced negative variance.")

    systematic_variance = max(systematic_variance, 0.0)
    total_variance = systematic_variance + residual_variance

    if total_variance <= 0:
        raise ValueError("Total variance must be positive.")

    factor_contributions = exposures * (covariance @ exposures)

    return FactorRiskResult(
        factor_contributions=factor_contributions,
        systematic_variance=systematic_variance,
        idiosyncratic_variance=float(residual_variance),
        total_variance=total_variance,
        systematic_percentage=systematic_variance / total_variance,
        idiosyncratic_percentage=residual_variance / total_variance,
    )


def risk_attribution(
    weights: np.ndarray,
    covariance: np.ndarray,
) -> RiskAttributionResult:
    portfolio_weights = np.asarray(weights, dtype=float)
    cov = np.asarray(covariance, dtype=float)

    if portfolio_weights.ndim != 1:
        raise ValueError("Weights must be one-dimensional.")

    if cov.ndim != 2:
        raise ValueError("Covariance must be two-dimensional.")

    if cov.shape != (len(portfolio_weights), len(portfolio_weights)):
        raise ValueError("Covariance dimensions must match weights.")

    if not np.isfinite(portfolio_weights).all():
        raise ValueError("Weights must contain only finite values.")

    if not np.isfinite(cov).all():
        raise ValueError("Covariance must contain only finite values.")

    variance = float(portfolio_weights @ cov @ portfolio_weights)

    if variance <= 0:
        raise ValueError("Portfolio variance must be positive.")

    total_risk = float(np.sqrt(variance))
    marginal = (cov @ portfolio_weights) / total_risk
    component = portfolio_weights * marginal
    percentage = component / total_risk

    return RiskAttributionResult(
        marginal_contributions=marginal,
        component_contributions=component,
        percentage_contributions=percentage,
        total_risk=total_risk,
    )

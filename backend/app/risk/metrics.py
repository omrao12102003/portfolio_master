from __future__ import annotations

import numpy as np
import pandas as pd


def historical_var(
    returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    if returns.empty:
        raise ValueError("Returns cannot be empty.")
    if not 0 < confidence_level < 1:
        raise ValueError("Confidence level must be between 0 and 1.")

    return float(-returns.quantile(1 - confidence_level))


def parametric_var(
    returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    if returns.empty:
        raise ValueError("Returns cannot be empty.")
    if not 0 < confidence_level < 1:
        raise ValueError("Confidence level must be between 0 and 1.")

    mean = returns.mean()
    std = returns.std(ddof=1)

    if std == 0:
        return float(max(-mean, 0.0))

    z = float(_normal_ppf(confidence_level))
    return float(max(-(mean - z * std), 0.0))


def expected_shortfall(
    returns: pd.Series,
    confidence_level: float = 0.95,
) -> float:
    if returns.empty:
        raise ValueError("Returns cannot be empty.")
    if not 0 < confidence_level < 1:
        raise ValueError("Confidence level must be between 0 and 1.")

    var = returns.quantile(1 - confidence_level)
    tail = returns[returns <= var]

    if tail.empty:
        return float(-var)

    return float(-tail.mean())


def beta(
    asset_returns: pd.Series,
    benchmark_returns: pd.Series,
) -> float:
    aligned = pd.concat(
        [asset_returns.rename("asset"), benchmark_returns.rename("benchmark")],
        axis=1,
    ).dropna()

    if aligned.empty:
        raise ValueError("Returns must contain overlapping observations.")

    benchmark_variance = aligned["benchmark"].var(ddof=1)

    if np.isclose(benchmark_variance, 0):
        raise ValueError("Benchmark variance must be positive.")

    return float(
        aligned["asset"].cov(aligned["benchmark"]) / benchmark_variance
    )


def tracking_error(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    aligned = pd.concat(
        [portfolio_returns.rename("portfolio"), benchmark_returns.rename("benchmark")],
        axis=1,
    ).dropna()

    if aligned.empty:
        raise ValueError("Returns must contain overlapping observations.")

    active_returns = aligned["portfolio"] - aligned["benchmark"]
    return float(active_returns.std(ddof=1) * np.sqrt(periods_per_year))


def concentration(weights: pd.Series) -> float:
    if weights.empty:
        raise ValueError("Weights cannot be empty.")
    if weights.isna().any():
        raise ValueError("Weights cannot contain missing values.")
    if (weights < 0).any():
        raise ValueError("Negative weights are not supported.")

    total = weights.sum()
    if not np.isclose(total, 1.0):
        raise ValueError("Weights must sum to 1.")

    return float((weights**2).sum())


def marginal_risk_contribution(
    weights: pd.Series,
    covariance: pd.DataFrame,
) -> pd.Series:
    if not weights.index.equals(covariance.index) or not weights.index.equals(
        covariance.columns
    ):
        raise ValueError("Weights and covariance assets must match.")

    portfolio_vol = float(
        np.sqrt(weights.values @ covariance.values @ weights.values)
    )

    if np.isclose(portfolio_vol, 0):
        raise ValueError("Portfolio volatility must be positive.")

    marginal = covariance @ weights
    return marginal / portfolio_vol


def component_risk_contribution(
    weights: pd.Series,
    covariance: pd.DataFrame,
) -> pd.Series:
    marginal = marginal_risk_contribution(weights, covariance)
    return weights * marginal


def percentage_risk_contribution(
    weights: pd.Series,
    covariance: pd.DataFrame,
) -> pd.Series:
    component = component_risk_contribution(weights, covariance)
    total = component.sum()

    if np.isclose(total, 0):
        raise ValueError("Total risk contribution must be positive.")

    return component / total


def _normal_ppf(probability: float) -> float:
    from statistics import NormalDist

    return float(NormalDist().inv_cdf(probability))

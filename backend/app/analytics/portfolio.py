from __future__ import annotations

import numpy as np
import pandas as pd


def validate_weights(weights: pd.Series) -> None:
    if weights.empty:
        raise ValueError("Weights cannot be empty.")

    if weights.isna().any():
        raise ValueError("Weights cannot contain missing values.")

    if not np.isclose(weights.sum(), 1.0):
        raise ValueError("Portfolio weights must sum to 1.")

    if (weights < 0).any():
        raise ValueError("Negative weights are not allowed.")


def mean_returns(
    returns: pd.DataFrame,
    periods_per_year: int = 252,
) -> pd.Series:
    return returns.mean() * periods_per_year


def covariance_matrix(
    returns: pd.DataFrame,
    periods_per_year: int = 252,
) -> pd.DataFrame:
    return returns.cov() * periods_per_year


def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.corr()


def portfolio_return(
    weights: pd.Series,
    expected_returns: pd.Series,
) -> float:
    if not weights.index.equals(expected_returns.index):
        raise ValueError("Weights and expected returns must have the same assets.")

    validate_weights(weights)

    return float(np.dot(weights.values, expected_returns.values))


def portfolio_volatility(
    weights: pd.Series,
    covariance: pd.DataFrame,
) -> float:
    if not weights.index.equals(covariance.index) or not weights.index.equals(
        covariance.columns
    ):
        raise ValueError("Weights and covariance assets must match.")

    validate_weights(weights)

    variance = weights.values @ covariance.values @ weights.values

    if variance < 0 and not np.isclose(variance, 0):
        raise ValueError("Portfolio variance cannot be negative.")

    return float(np.sqrt(max(variance, 0.0)))


def portfolio_sharpe(
    weights: pd.Series,
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    risk_free_rate: float = 0.0,
) -> float:
    excess_return = portfolio_return(weights, expected_returns) - risk_free_rate
    volatility = portfolio_volatility(weights, covariance)

    if volatility == 0:
        return float("nan")

    return float(excess_return / volatility)

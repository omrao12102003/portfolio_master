from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from app.analytics.portfolio import (
    portfolio_sharpe,
    portfolio_volatility,
    validate_weights,
)


def _validate_inputs(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
) -> None:
    if expected_returns.empty:
        raise ValueError("Expected returns cannot be empty.")

    if not expected_returns.index.equals(covariance.index) or not expected_returns.index.equals(
        covariance.columns
    ):
        raise ValueError("Expected returns and covariance assets must match.")

    if covariance.isna().any().any() or expected_returns.isna().any():
        raise ValueError("Optimization inputs cannot contain missing values.")


def _bounds(
    assets: pd.Index,
    min_weight: float,
    max_weight: float,
) -> list[tuple[float, float]]:
    if min_weight < 0:
        raise ValueError("Minimum weight cannot be negative.")
    if max_weight < min_weight:
        raise ValueError("Maximum weight must be >= minimum weight.")
    if len(assets) * min_weight > 1:
        raise ValueError("Minimum weight constraints are infeasible.")
    if len(assets) * max_weight < 1:
        raise ValueError("Maximum weight constraints are infeasible.")

    return [(min_weight, max_weight)] * len(assets)


def _initial_weights(
    assets: pd.Index,
    min_weight: float,
    max_weight: float,
) -> np.ndarray:
    n = len(assets)
    weights = np.full(n, 1.0 / n)

    if np.all(weights >= min_weight) and np.all(weights <= max_weight):
        return weights

    result = minimize(
        lambda w: float(np.sum((w - 1.0 / n) ** 2)),
        weights,
        method="SLSQP",
        bounds=_bounds(assets, min_weight, max_weight),
        constraints={"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
    )

    if not result.success:
        raise ValueError("Unable to construct feasible initial weights.")

    return result.x


def _optimize(
    objective,
    assets: pd.Index,
    min_weight: float,
    max_weight: float,
) -> pd.Series:
    initial = _initial_weights(assets, min_weight, max_weight)

    result = minimize(
        objective,
        initial,
        method="SLSQP",
        bounds=_bounds(assets, min_weight, max_weight),
        constraints={"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
        options={"maxiter": 1000, "ftol": 1e-10},
    )

    if not result.success:
        raise ValueError(f"Optimization failed: {result.message}")

    weights = pd.Series(result.x, index=assets, dtype=float)
    weights = weights / weights.sum()

    validate_weights(weights)

    return weights


def equal_weight(expected_returns: pd.Series) -> pd.Series:
    if expected_returns.empty:
        raise ValueError("Expected returns cannot be empty.")

    return pd.Series(
        1.0 / len(expected_returns),
        index=expected_returns.index,
        dtype=float,
    )


def minimum_volatility(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> pd.Series:
    _validate_inputs(expected_returns, covariance)

    return _optimize(
        lambda w: portfolio_volatility(
            pd.Series(w, index=expected_returns.index),
            covariance,
        ),
        expected_returns.index,
        min_weight,
        max_weight,
    )


def maximum_sharpe(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    risk_free_rate: float = 0.0,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> pd.Series:
    _validate_inputs(expected_returns, covariance)

    def objective(w: np.ndarray) -> float:
        weights = pd.Series(w, index=expected_returns.index)
        sharpe = portfolio_sharpe(
            weights,
            expected_returns,
            covariance,
            risk_free_rate,
        )

        if np.isnan(sharpe):
            return 1e6

        return -sharpe

    return _optimize(
        objective,
        expected_returns.index,
        min_weight,
        max_weight,
    )


def risk_parity(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> pd.Series:
    _validate_inputs(expected_returns, covariance)

    def objective(w: np.ndarray) -> float:
        weights = pd.Series(w, index=expected_returns.index)
        portfolio_vol = portfolio_volatility(weights, covariance)

        if np.isclose(portfolio_vol, 0):
            return 1e6

        marginal = covariance @ weights
        contributions = weights * marginal / portfolio_vol
        target = portfolio_vol / len(weights)

        return float(np.sum((contributions - target) ** 2))

    return _optimize(
        objective,
        expected_returns.index,
        min_weight,
        max_weight,
    )

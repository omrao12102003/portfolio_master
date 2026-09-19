from __future__ import annotations

import numpy as np
import pandas as pd

from app.analytics.portfolio import portfolio_return, portfolio_volatility
from app.optimization.classical import _validate_inputs


def target_return_portfolio(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    target_return: float,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> pd.Series:
    _validate_inputs(expected_returns, covariance)

    minimum = float(expected_returns.min())
    maximum = float(expected_returns.max())

    if target_return < minimum or target_return > maximum:
        raise ValueError("Target return is outside the feasible return range.")

    assets = expected_returns.index

    def objective(w: np.ndarray) -> float:
        weights = pd.Series(w, index=assets)
        return portfolio_volatility(weights, covariance)

    initial = np.full(len(assets), 1.0 / len(assets))

    bounds = [(min_weight, max_weight)] * len(assets)

    from scipy.optimize import minimize

    result = minimize(
        objective,
        initial,
        method="SLSQP",
        bounds=bounds,
        constraints=[
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
            {
                "type": "eq",
                "fun": lambda w: portfolio_return(
                    pd.Series(w, index=assets),
                    expected_returns,
                )
                - target_return,
            },
        ],
        options={"maxiter": 1000, "ftol": 1e-10},
    )

    if not result.success:
        raise ValueError(f"Target-return optimization failed: {result.message}")

    weights = pd.Series(result.x, index=assets, dtype=float)
    return weights / weights.sum()


def efficient_frontier(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    points: int = 25,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> pd.DataFrame:
    _validate_inputs(expected_returns, covariance)

    if points < 2:
        raise ValueError("Frontier requires at least 2 points.")

    minimum_return = float(expected_returns.min())
    maximum_return = float(expected_returns.max())

    targets = np.linspace(minimum_return, maximum_return, points)

    rows: list[dict[str, float]] = []

    for target in targets:
        weights = target_return_portfolio(
            expected_returns,
            covariance,
            float(target),
            min_weight,
            max_weight,
        )

        rows.append(
            {
                "target_return": float(target),
                "expected_return": portfolio_return(weights, expected_returns),
                "volatility": portfolio_volatility(weights, covariance),
            }
        )

    return pd.DataFrame(rows)


def portfolio_metrics(
    weights: pd.Series,
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
) -> dict[str, float]:
    return {
        "expected_return": portfolio_return(weights, expected_returns),
        "volatility": portfolio_volatility(weights, covariance),
    }

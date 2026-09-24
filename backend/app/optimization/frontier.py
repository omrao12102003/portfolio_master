from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from app.analytics.portfolio import portfolio_return, portfolio_volatility
from app.optimization.classical import _validate_inputs


def _validate_bounds(
    asset_count: int,
    min_weight: float,
    max_weight: float,
) -> None:
    if not np.isfinite(min_weight) or not np.isfinite(max_weight):
        raise ValueError("Weight bounds must be finite.")

    if min_weight < 0 or max_weight > 1:
        raise ValueError("Weight bounds must be between 0 and 1.")

    if min_weight > max_weight:
        raise ValueError("min_weight must be <= max_weight.")

    if asset_count * min_weight > 1 + 1e-12:
        raise ValueError("Minimum weight constraints are infeasible.")

    if asset_count * max_weight < 1 - 1e-12:
        raise ValueError("Maximum weight constraints are infeasible.")


def _endpoint_weights(
    expected_returns: pd.Series,
    min_weight: float,
    max_weight: float,
    reverse: bool = False,
) -> pd.Series:
    asset_count = len(expected_returns)
    _validate_bounds(asset_count, min_weight, max_weight)

    weights = np.full(asset_count, min_weight, dtype=float)
    remaining = 1.0 - asset_count * min_weight

    order = np.argsort(expected_returns.to_numpy(dtype=float))
    if reverse:
        order = order[::-1]

    capacity = max_weight - min_weight

    for index in order:
        allocation = min(remaining, capacity)
        weights[index] += allocation
        remaining -= allocation

        if remaining <= 1e-12:
            break

    if remaining > 1e-10:
        raise ValueError("Unable to construct a feasible portfolio.")

    return pd.Series(weights, index=expected_returns.index, dtype=float)


def _feasible_return_range(
    expected_returns: pd.Series,
    min_weight: float,
    max_weight: float,
) -> tuple[float, float, pd.Series, pd.Series]:
    minimum_weights = _endpoint_weights(
        expected_returns,
        min_weight,
        max_weight,
    )
    maximum_weights = _endpoint_weights(
        expected_returns,
        min_weight,
        max_weight,
        reverse=True,
    )

    minimum_return = portfolio_return(
        minimum_weights,
        expected_returns,
    )
    maximum_return = portfolio_return(
        maximum_weights,
        expected_returns,
    )

    return (
        float(minimum_return),
        float(maximum_return),
        minimum_weights,
        maximum_weights,
    )


def target_return_portfolio(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    target_return: float,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> pd.Series:
    _validate_inputs(expected_returns, covariance)

    if not np.isfinite(target_return):
        raise ValueError("Target return must be finite.")

    minimum, maximum, minimum_weights, maximum_weights = _feasible_return_range(
        expected_returns,
        min_weight,
        max_weight,
    )

    tolerance = 1e-10
    if target_return < minimum - tolerance or target_return > maximum + tolerance:
        raise ValueError("Target return is outside the feasible return range.")

    if abs(maximum - minimum) <= tolerance:
        initial = minimum_weights.to_numpy(dtype=float)
    else:
        fraction = (target_return - minimum) / (maximum - minimum)
        fraction = float(np.clip(fraction, 0.0, 1.0))
        initial = (
            minimum_weights.to_numpy(dtype=float)
            + fraction
            * (
                maximum_weights.to_numpy(dtype=float)
                - minimum_weights.to_numpy(dtype=float)
            )
        )

    assets = expected_returns.index

    def objective(weights: np.ndarray) -> float:
        portfolio_weights = pd.Series(weights, index=assets)
        return portfolio_volatility(portfolio_weights, covariance)

    bounds = [(min_weight, max_weight)] * len(assets)

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

    if abs(float(weights.sum()) - 1.0) > 1e-7:
        raise ValueError("Frontier optimization produced invalid weights.")

    if (
        (weights < min_weight - 1e-7).any()
        or (weights > max_weight + 1e-7).any()
    ):
        raise ValueError("Frontier optimization violated weight bounds.")

    return weights


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

    minimum_return, maximum_return, _, _ = _feasible_return_range(
        expected_returns,
        min_weight,
        max_weight,
    )

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

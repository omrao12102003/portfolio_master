from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CAPMResult:
    alpha: float
    beta: float
    r_squared: float
    observations: int


def capm_analysis(
    asset_returns: np.ndarray,
    market_returns: np.ndarray,
    risk_free_returns: np.ndarray | None = None,
) -> CAPMResult:
    asset = np.asarray(asset_returns, dtype=float)
    market = np.asarray(market_returns, dtype=float)

    if asset.ndim != 1 or market.ndim != 1:
        raise ValueError("Returns must be one-dimensional.")

    if len(asset) != len(market):
        raise ValueError("Asset and market returns must have equal length.")

    if len(asset) < 2:
        raise ValueError("At least two observations are required.")

    if risk_free_returns is None:
        excess_asset = asset
        excess_market = market
    else:
        risk_free = np.asarray(risk_free_returns, dtype=float)

        if risk_free.ndim != 1 or len(risk_free) != len(asset):
            raise ValueError(
                "Risk-free returns must be one-dimensional and match asset length."
            )

        excess_asset = asset - risk_free
        excess_market = market - risk_free

    if not np.isfinite(excess_asset).all() or not np.isfinite(excess_market).all():
        raise ValueError("Returns must contain only finite values.")

    variance = float(np.var(excess_market, ddof=1))

    if variance <= 0:
        raise ValueError("Market returns must have positive variance.")

    beta = float(
        np.cov(excess_asset, excess_market, ddof=1)[0, 1] / variance
    )
    alpha = float(np.mean(excess_asset) - beta * np.mean(excess_market))

    predicted = alpha + beta * excess_market
    residuals = excess_asset - predicted
    total_sum_squares = float(
        np.sum((excess_asset - np.mean(excess_asset)) ** 2)
    )
    residual_sum_squares = float(np.sum(residuals**2))

    if total_sum_squares == 0:
        r_squared = 0.0
    else:
        r_squared = float(1.0 - residual_sum_squares / total_sum_squares)

    return CAPMResult(
        alpha=alpha,
        beta=beta,
        r_squared=r_squared,
        observations=len(asset),
    )

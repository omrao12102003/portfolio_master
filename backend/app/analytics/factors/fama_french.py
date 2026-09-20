from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FamaFrenchResult:
    alpha: float
    market_beta: float
    smb_beta: float
    hml_beta: float
    r_squared: float
    residual_volatility: float
    observations: int


def fama_french_3_factor(
    asset_returns: np.ndarray,
    market_excess_returns: np.ndarray,
    smb_returns: np.ndarray,
    hml_returns: np.ndarray,
    *,
    annualization_factor: float | None = None,
) -> FamaFrenchResult:
    asset = np.asarray(asset_returns, dtype=float)
    market = np.asarray(market_excess_returns, dtype=float)
    smb = np.asarray(smb_returns, dtype=float)
    hml = np.asarray(hml_returns, dtype=float)

    arrays = (asset, market, smb, hml)

    if any(array.ndim != 1 for array in arrays):
        raise ValueError("All return series must be one-dimensional.")

    lengths = {len(array) for array in arrays}
    if len(lengths) != 1:
        raise ValueError("All return series must have equal length.")

    observations = len(asset)

    if observations < 4:
        raise ValueError("At least four observations are required.")

    if not all(np.isfinite(array).all() for array in arrays):
        raise ValueError("Return series must contain only finite values.")

    if annualization_factor is not None and annualization_factor <= 0:
        raise ValueError("annualization_factor must be positive.")

    design = np.column_stack(
        (
            np.ones(observations),
            market,
            smb,
            hml,
        )
    )

    coefficients, _, rank, _ = np.linalg.lstsq(
        design,
        asset,
        rcond=None,
    )

    if rank < design.shape[1]:
        raise ValueError("Factor matrix must have full column rank.")

    predicted = design @ coefficients
    residuals = asset - predicted

    total_sum_squares = float(
        np.sum((asset - np.mean(asset)) ** 2)
    )
    residual_sum_squares = float(np.sum(residuals**2))

    if total_sum_squares == 0:
        r_squared = 0.0
    else:
        r_squared = float(
            1.0 - residual_sum_squares / total_sum_squares
        )

    residual_volatility = float(np.std(residuals, ddof=1))

    if annualization_factor is not None:
        residual_volatility *= float(np.sqrt(annualization_factor))

    return FamaFrenchResult(
        alpha=float(coefficients[0]),
        market_beta=float(coefficients[1]),
        smb_beta=float(coefficients[2]),
        hml_beta=float(coefficients[3]),
        r_squared=r_squared,
        residual_volatility=residual_volatility,
        observations=observations,
    )

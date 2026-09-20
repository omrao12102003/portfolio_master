from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from arch import arch_model


@dataclass(frozen=True)
class GARCHForecast:
    conditional_volatility: np.ndarray
    forecast_variance: np.ndarray
    forecast_volatility: np.ndarray
    annualized_forecast_volatility: np.ndarray


def garch_forecast(
    returns: np.ndarray,
    steps: int,
    *,
    annualization_factor: float = 252.0,
) -> GARCHForecast:
    values = np.asarray(returns, dtype=float)

    if values.ndim != 1:
        raise ValueError("Returns must be one-dimensional.")

    if len(values) < 30:
        raise ValueError("At least thirty observations are required.")

    if not np.isfinite(values).all():
        raise ValueError("Returns must contain only finite values.")

    if steps < 1:
        raise ValueError("steps must be positive.")

    if annualization_factor <= 0:
        raise ValueError("annualization_factor must be positive.")

    if np.std(values, ddof=1) <= 0:
        raise ValueError("Returns must have positive variance.")

    model = arch_model(
        values * 100.0,
        mean="Constant",
        vol="GARCH",
        p=1,
        q=1,
        dist="normal",
        rescale=False,
    )

    fitted = model.fit(disp="off")

    forecasts = fitted.forecast(horizon=steps, reindex=False)

    variance = np.asarray(
        forecasts.variance.iloc[-1].to_numpy(),
        dtype=float,
    )

    conditional_volatility = np.asarray(
        fitted.conditional_volatility,
        dtype=float,
    ) / 100.0

    forecast_volatility = np.sqrt(variance) / 100.0
    annualized = forecast_volatility * np.sqrt(annualization_factor)

    return GARCHForecast(
        conditional_volatility=conditional_volatility,
        forecast_variance=variance / 10000.0,
        forecast_volatility=forecast_volatility,
        annualized_forecast_volatility=annualized,
    )

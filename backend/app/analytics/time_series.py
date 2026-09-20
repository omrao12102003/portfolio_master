from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from statsmodels.tsa.arima.model import ARIMA


@dataclass(frozen=True)
class ARIMAForecast:
    forecast: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    order: tuple[int, int, int]


def arima_forecast(
    values: np.ndarray,
    order: tuple[int, int, int],
    steps: int,
    *,
    alpha: float = 0.05,
) -> ARIMAForecast:
    series = np.asarray(values, dtype=float)

    if series.ndim != 1:
        raise ValueError("Values must be one-dimensional.")

    if len(series) < 10:
        raise ValueError("At least ten observations are required.")

    if not np.isfinite(series).all():
        raise ValueError("Values must contain only finite values.")

    if len(order) != 3:
        raise ValueError("ARIMA order must contain three integers.")

    p, d, q = order

    if any(not isinstance(value, (int, np.integer)) for value in order):
        raise ValueError("ARIMA order values must be integers.")

    if p < 0 or d < 0 or q < 0:
        raise ValueError("ARIMA order values cannot be negative.")

    if steps < 1:
        raise ValueError("steps must be positive.")

    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1.")

    model = ARIMA(series, order=(p, d, q))
    fitted = model.fit()

    forecast_result = fitted.get_forecast(steps=steps)
    forecast = np.asarray(forecast_result.predicted_mean, dtype=float)
    intervals = np.asarray(
        forecast_result.conf_int(alpha=alpha),
        dtype=float,
    )

    return ARIMAForecast(
        forecast=forecast,
        lower=intervals[:, 0],
        upper=intervals[:, 1],
        order=(p, d, q),
    )

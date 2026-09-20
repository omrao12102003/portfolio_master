import numpy as np
import pytest

from app.analytics.time_series import ARIMAForecast, arima_forecast


def test_arima_returns_forecast_and_confidence_intervals():
    rng = np.random.default_rng(42)
    values = np.cumsum(rng.normal(0.001, 0.01, 80))

    result = arima_forecast(
        values,
        order=(1, 1, 0),
        steps=5,
    )

    assert isinstance(result, ARIMAForecast)
    assert result.order == (1, 1, 0)
    assert result.forecast.shape == (5,)
    assert result.lower.shape == (5,)
    assert result.upper.shape == (5,)
    assert np.all(result.lower <= result.forecast)
    assert np.all(result.forecast <= result.upper)


def test_arima_is_reproducible():
    rng = np.random.default_rng(7)
    values = np.cumsum(rng.normal(0, 0.02, 60))

    first = arima_forecast(values, (1, 1, 0), 4)
    second = arima_forecast(values, (1, 1, 0), 4)

    np.testing.assert_allclose(first.forecast, second.forecast)
    np.testing.assert_allclose(first.lower, second.lower)
    np.testing.assert_allclose(first.upper, second.upper)


def test_arima_rejects_short_series():
    with pytest.raises(ValueError, match="ten observations"):
        arima_forecast(np.ones(9), (1, 0, 0), 2)


def test_arima_rejects_non_finite_values():
    values = np.ones(20)
    values[5] = np.nan

    with pytest.raises(ValueError, match="finite"):
        arima_forecast(values, (1, 0, 0), 2)


def test_arima_rejects_invalid_order():
    with pytest.raises(ValueError, match="negative"):
        arima_forecast(np.ones(20), (-1, 0, 0), 2)


def test_arima_rejects_invalid_steps():
    with pytest.raises(ValueError, match="positive"):
        arima_forecast(np.ones(20), (1, 0, 0), 0)


def test_arima_rejects_invalid_alpha():
    with pytest.raises(ValueError, match="between 0 and 1"):
        arima_forecast(np.ones(20), (1, 0, 0), 2, alpha=1.0)

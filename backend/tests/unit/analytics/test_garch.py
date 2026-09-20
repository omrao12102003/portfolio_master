import numpy as np
import pytest

from app.analytics.garch import GARCHForecast, garch_forecast


def test_garch_returns_conditional_and_forecast_volatility():
    rng = np.random.default_rng(42)
    returns = rng.normal(0, 0.01, 150)

    result = garch_forecast(returns, steps=5)

    assert isinstance(result, GARCHForecast)
    assert result.conditional_volatility.shape == (150,)
    assert result.forecast_variance.shape == (5,)
    assert result.forecast_volatility.shape == (5,)
    assert result.annualized_forecast_volatility.shape == (5,)
    assert np.all(result.conditional_volatility > 0)
    assert np.all(result.forecast_variance > 0)
    assert np.all(result.forecast_volatility > 0)
    assert np.all(result.annualized_forecast_volatility > 0)


def test_garch_forecast_is_reproducible():
    rng = np.random.default_rng(7)
    returns = rng.normal(0, 0.015, 120)

    first = garch_forecast(returns, steps=4)
    second = garch_forecast(returns, steps=4)

    np.testing.assert_allclose(
        first.forecast_variance,
        second.forecast_variance,
    )
    np.testing.assert_allclose(
        first.forecast_volatility,
        second.forecast_volatility,
    )


def test_garch_annualization_is_applied():
    rng = np.random.default_rng(11)
    returns = rng.normal(0, 0.01, 100)

    result = garch_forecast(
        returns,
        steps=3,
        annualization_factor=252,
    )

    np.testing.assert_allclose(
        result.annualized_forecast_volatility,
        result.forecast_volatility * np.sqrt(252),
    )


def test_garch_rejects_short_series():
    with pytest.raises(ValueError, match="thirty observations"):
        garch_forecast(np.ones(29) * 0.01, steps=2)


def test_garch_rejects_non_finite_values():
    values = np.ones(50) * 0.01
    values[10] = np.nan

    with pytest.raises(ValueError, match="finite"):
        garch_forecast(values, steps=2)


def test_garch_rejects_invalid_steps():
    with pytest.raises(ValueError, match="positive"):
        garch_forecast(np.ones(50) * 0.01, steps=0)


def test_garch_rejects_invalid_annualization_factor():
    with pytest.raises(ValueError, match="positive"):
        garch_forecast(
            np.random.default_rng(5).normal(0, 0.01, 80),
            steps=2,
            annualization_factor=0,
        )


def test_garch_rejects_zero_variance():
    with pytest.raises(ValueError, match="positive variance"):
        garch_forecast(np.ones(50) * 0.01, steps=2)

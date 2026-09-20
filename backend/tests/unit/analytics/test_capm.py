import numpy as np
import pytest

from app.analytics.factors.capm import CAPMResult, capm_analysis


def test_capm_recovers_known_alpha_and_beta():
    market = np.array([0.01, 0.02, -0.01, 0.03, 0.015])
    asset = 0.002 + 1.5 * market

    result = capm_analysis(asset, market)

    assert isinstance(result, CAPMResult)
    assert result.alpha == pytest.approx(0.002)
    assert result.beta == pytest.approx(1.5)
    assert result.r_squared == pytest.approx(1.0)
    assert result.observations == 5


def test_capm_supports_risk_free_returns():
    market = np.array([0.01, 0.02, 0.03, 0.015])
    risk_free = np.array([0.002, 0.002, 0.002, 0.002])
    asset = risk_free + 0.001 + 1.2 * (market - risk_free)

    result = capm_analysis(asset, market, risk_free)

    assert result.alpha == pytest.approx(0.001)
    assert result.beta == pytest.approx(1.2)


def test_capm_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="equal length"):
        capm_analysis(
            np.array([0.01, 0.02]),
            np.array([0.01, 0.02, 0.03]),
        )


def test_capm_rejects_constant_market():
    with pytest.raises(ValueError, match="positive variance"):
        capm_analysis(
            np.array([0.01, 0.02, 0.03]),
            np.array([0.01, 0.01, 0.01]),
        )


def test_capm_rejects_non_finite_values():
    with pytest.raises(ValueError, match="finite"):
        capm_analysis(
            np.array([0.01, np.nan, 0.03]),
            np.array([0.01, 0.02, 0.03]),
        )

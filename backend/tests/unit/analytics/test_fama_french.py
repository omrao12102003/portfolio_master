import numpy as np
import pytest

from app.analytics.factors.fama_french import (
    FamaFrenchResult,
    fama_french_3_factor,
)


def test_fama_french_recovers_known_factor_loadings():
    market = np.array([0.01, 0.02, -0.01, 0.03, 0.015, -0.02])
    smb = np.array([0.02, -0.01, 0.015, 0.01, -0.02, 0.005])
    hml = np.array([-0.01, 0.015, 0.02, -0.005, 0.01, -0.015])

    asset = 0.002 + 1.2 * market + 0.7 * smb - 0.4 * hml

    result = fama_french_3_factor(asset, market, smb, hml)

    assert isinstance(result, FamaFrenchResult)
    assert result.alpha == pytest.approx(0.002)
    assert result.market_beta == pytest.approx(1.2)
    assert result.smb_beta == pytest.approx(0.7)
    assert result.hml_beta == pytest.approx(-0.4)
    assert result.r_squared == pytest.approx(1.0)
    assert result.residual_volatility == pytest.approx(0.0)
    assert result.observations == 6


def test_fama_french_supports_annualized_residual_volatility():
    market = np.array([0.01, 0.02, 0.03, -0.01, 0.015, 0.02])
    smb = np.array([0.01, -0.01, 0.005, 0.02, -0.005, 0.01])
    hml = np.array([-0.005, 0.01, 0.015, -0.01, 0.005, -0.002])

    noise = np.array([0.001, -0.001, 0.002, -0.002, 0.001, -0.001])
    asset = 0.001 + 1.1 * market + 0.5 * smb - 0.3 * hml + noise

    result = fama_french_3_factor(
        asset,
        market,
        smb,
        hml,
        annualization_factor=252,
    )

    assert result.residual_volatility > 0


def test_fama_french_rejects_mismatched_lengths():
    with pytest.raises(ValueError, match="equal length"):
        fama_french_3_factor(
            np.array([0.01, 0.02, 0.03, 0.04]),
            np.array([0.01, 0.02, 0.03]),
            np.array([0.01, 0.02, 0.03, 0.04]),
            np.array([0.01, 0.02, 0.03, 0.04]),
        )


def test_fama_french_rejects_non_finite_values():
    with pytest.raises(ValueError, match="finite"):
        fama_french_3_factor(
            np.array([0.01, np.nan, 0.03, 0.04]),
            np.array([0.01, 0.02, 0.03, 0.04]),
            np.array([0.01, 0.02, 0.03, 0.04]),
            np.array([0.01, 0.02, 0.03, 0.04]),
        )


def test_fama_french_rejects_invalid_annualization_factor():
    with pytest.raises(ValueError, match="positive"):
        fama_french_3_factor(
            np.array([0.01, 0.02, 0.03, 0.04]),
            np.array([0.01, 0.02, 0.03, 0.04]),
            np.array([0.01, 0.02, 0.03, 0.04]),
            np.array([0.01, 0.02, 0.03, 0.04]),
            annualization_factor=0,
        )


def test_fama_french_rejects_rank_deficient_factor_matrix():
    factor = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    asset = 0.001 + 1.2 * factor

    with pytest.raises(ValueError, match="full column rank"):
        fama_french_3_factor(
            asset,
            factor,
            factor,
            factor,
        )

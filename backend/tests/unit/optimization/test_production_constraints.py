import numpy as np
import pandas as pd

from app.optimization.classical import (
    maximum_sharpe,
    minimum_volatility,
    risk_parity,
)


def _inputs():
    assets = pd.Index(["A", "B", "C"])
    expected = pd.Series([0.08, 0.14, 0.04], index=assets)
    covariance = pd.DataFrame(
        [
            [0.04, 0.006, 0.002],
            [0.006, 0.09, 0.003],
            [0.002, 0.003, 0.025],
        ],
        index=assets,
        columns=assets,
    )
    return expected, covariance


def test_constrained_optimizers_respect_bounds():
    expected, covariance = _inputs()

    for optimizer in (minimum_volatility, maximum_sharpe, risk_parity):
        weights = optimizer(
            expected,
            covariance,
            min_weight=0.20,
            max_weight=0.60,
        )

        assert np.isclose(weights.sum(), 1.0)
        assert (weights >= 0.20 - 1e-8).all()
        assert (weights <= 0.60 + 1e-8).all()


def test_maximum_sharpe_responds_to_expected_return_assumptions():
    _, covariance = _inputs()
    assets = covariance.index

    low_b = pd.Series([0.08, 0.09, 0.04], index=assets)
    high_b = pd.Series([0.08, 0.30, 0.04], index=assets)

    first = maximum_sharpe(
        low_b,
        covariance,
        risk_free_rate=0.02,
        min_weight=0.0,
        max_weight=0.80,
    )

    second = maximum_sharpe(
        high_b,
        covariance,
        risk_free_rate=0.02,
        min_weight=0.0,
        max_weight=0.80,
    )

    assert not np.allclose(
        first.to_numpy(),
        second.to_numpy(),
        atol=1e-5,
    )


def test_infeasible_bounds_are_rejected():
    expected, covariance = _inputs()

    try:
        minimum_volatility(
            expected,
            covariance,
            min_weight=0.40,
            max_weight=1.0,
        )
    except ValueError as exc:
        assert "infeasible" in str(exc).lower()
    else:
        raise AssertionError(
            "Expected infeasible minimum-weight bounds to fail."
        )

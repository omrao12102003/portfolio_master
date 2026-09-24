import numpy as np
import pandas as pd
import pytest

from app.optimization.frontier import (
    efficient_frontier,
    target_return_portfolio,
)


def _inputs() -> tuple[pd.Series, pd.DataFrame]:
    assets = ["A", "B", "C"]
    expected_returns = pd.Series(
        [0.05, 0.10, 0.15],
        index=assets,
        dtype=float,
    )
    covariance = pd.DataFrame(
        [
            [0.040, 0.006, 0.002],
            [0.006, 0.025, 0.005],
            [0.002, 0.005, 0.050],
        ],
        index=assets,
        columns=assets,
        dtype=float,
    )
    return expected_returns, covariance


def test_target_return_respects_weight_bounds():
    expected_returns, covariance = _inputs()

    weights = target_return_portfolio(
        expected_returns,
        covariance,
        target_return=0.10,
        min_weight=0.20,
        max_weight=0.60,
    )

    assert np.isclose(weights.sum(), 1.0)
    assert (weights >= 0.20 - 1e-7).all()
    assert (weights <= 0.60 + 1e-7).all()
    assert np.isclose(
        float(weights @ expected_returns),
        0.10,
        atol=1e-7,
    )


def test_constrained_frontier_uses_feasible_return_range():
    expected_returns, covariance = _inputs()

    result = efficient_frontier(
        expected_returns,
        covariance,
        points=5,
        min_weight=0.20,
        max_weight=0.60,
    )

    assert len(result) == 5
    assert np.isclose(result.iloc[0]["expected_return"], 0.08, atol=1e-7)
    assert np.isclose(result.iloc[-1]["expected_return"], 0.12, atol=1e-7)
    assert result["expected_return"].is_monotonic_increasing


def test_frontier_rejects_target_outside_constrained_range():
    expected_returns, covariance = _inputs()

    with pytest.raises(ValueError, match="outside the feasible"):
        target_return_portfolio(
            expected_returns,
            covariance,
            target_return=0.05,
            min_weight=0.20,
            max_weight=0.60,
        )

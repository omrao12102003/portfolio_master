import numpy as np
import pandas as pd
import pytest

from app.optimization.classical import (
    equal_weight,
    maximum_sharpe,
    minimum_volatility,
    risk_parity,
)


@pytest.fixture
def inputs():
    assets = pd.Index(["A", "B", "C"])

    expected_returns = pd.Series(
        [0.08, 0.12, 0.06],
        index=assets,
    )

    covariance = pd.DataFrame(
        [
            [0.04, 0.01, 0.00],
            [0.01, 0.09, 0.01],
            [0.00, 0.01, 0.01],
        ],
        index=assets,
        columns=assets,
    )

    return expected_returns, covariance


def test_equal_weight(inputs):
    expected_returns, _ = inputs

    result = equal_weight(expected_returns)

    assert result.sum() == pytest.approx(1.0)
    assert result.tolist() == pytest.approx([1 / 3] * 3)


def test_minimum_volatility(inputs):
    expected_returns, covariance = inputs

    result = minimum_volatility(expected_returns, covariance)

    assert result.sum() == pytest.approx(1.0)
    assert (result >= 0).all()
    assert (result <= 1).all()


def test_maximum_sharpe(inputs):
    expected_returns, covariance = inputs

    result = maximum_sharpe(expected_returns, covariance)

    assert result.sum() == pytest.approx(1.0)
    assert (result >= 0).all()
    assert (result <= 1).all()


def test_risk_parity(inputs):
    expected_returns, covariance = inputs

    result = risk_parity(expected_returns, covariance)

    assert result.sum() == pytest.approx(1.0)
    assert (result >= 0).all()
    assert (result <= 1).all()


def test_weight_bounds(inputs):
    expected_returns, covariance = inputs

    result = minimum_volatility(
        expected_returns,
        covariance,
        min_weight=0.1,
        max_weight=0.6,
    )

    assert result.sum() == pytest.approx(1.0)
    assert (result >= 0.1 - 1e-8).all()
    assert (result <= 0.6 + 1e-8).all()


def test_invalid_inputs(inputs):
    expected_returns, covariance = inputs

    with pytest.raises(ValueError):
        minimum_volatility(pd.Series(dtype=float), covariance)

    with pytest.raises(ValueError):
        minimum_volatility(
            expected_returns,
            covariance.drop(columns="C"),
        )

    with pytest.raises(ValueError):
        minimum_volatility(
            expected_returns,
            covariance,
            min_weight=0.5,
            max_weight=1.0,
        )

    with pytest.raises(ValueError):
        minimum_volatility(
            expected_returns,
            covariance,
            min_weight=0.0,
            max_weight=0.2,
        )


def test_missing_values_are_rejected(inputs):
    expected_returns, covariance = inputs
    bad_returns = expected_returns.copy()
    bad_returns["A"] = np.nan

    with pytest.raises(ValueError):
        minimum_volatility(bad_returns, covariance)


def test_risk_parity_bounds(inputs):
    expected_returns, covariance = inputs

    result = risk_parity(
        expected_returns,
        covariance,
        min_weight=0.1,
        max_weight=0.7,
    )

    assert result.sum() == pytest.approx(1.0)
    assert (result >= 0.1 - 1e-8).all()
    assert (result <= 0.7 + 1e-8).all()

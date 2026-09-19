import pandas as pd
import pytest

from app.optimization.frontier import (
    efficient_frontier,
    portfolio_metrics,
    target_return_portfolio,
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


def test_target_return_portfolio(inputs):
    expected_returns, covariance = inputs

    result = target_return_portfolio(
        expected_returns,
        covariance,
        target_return=0.08,
    )

    assert result.sum() == pytest.approx(1.0)
    assert (result >= -1e-8).all()

    achieved = float(result @ expected_returns)
    assert achieved == pytest.approx(0.08, abs=1e-7)


def test_target_return_with_bounds(inputs):
    expected_returns, covariance = inputs

    result = target_return_portfolio(
        expected_returns,
        covariance,
        target_return=0.08,
        min_weight=0.1,
        max_weight=0.7,
    )

    assert result.sum() == pytest.approx(1.0)
    assert (result >= 0.1 - 1e-7).all()
    assert (result <= 0.7 + 1e-7).all()


def test_efficient_frontier(inputs):
    expected_returns, covariance = inputs

    result = efficient_frontier(
        expected_returns,
        covariance,
        points=10,
    )

    assert len(result) == 10
    assert list(result.columns) == [
        "target_return",
        "expected_return",
        "volatility",
    ]
    assert result["volatility"].notna().all()
    assert result["expected_return"].notna().all()


def test_portfolio_metrics(inputs):
    expected_returns, covariance = inputs

    weights = pd.Series(
        [0.4, 0.4, 0.2],
        index=expected_returns.index,
    )

    result = portfolio_metrics(weights, expected_returns, covariance)

    assert result["expected_return"] == pytest.approx(0.092)
    assert result["volatility"] > 0


def test_invalid_frontier_points(inputs):
    expected_returns, covariance = inputs

    with pytest.raises(ValueError):
        efficient_frontier(
            expected_returns,
            covariance,
            points=1,
        )


def test_invalid_target_return(inputs):
    expected_returns, covariance = inputs

    with pytest.raises(ValueError):
        target_return_portfolio(
            expected_returns,
            covariance,
            target_return=0.50,
        )

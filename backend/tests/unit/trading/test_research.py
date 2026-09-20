import numpy as np
import pytest

from app.trading.research import (
    ExecutionConfig,
    evaluate_strategy,
    mean_reversion_signal,
    momentum_signal,
    position_size,
    simulate_execution,
    walk_forward_splits,
)


def test_momentum_signal():
    prices = [100, 101, 102, 103, 104, 105]
    signal = momentum_signal(prices, lookback=2)

    assert np.array_equal(signal[:2], [0.0, 0.0])
    assert np.all(signal[2:] == 1.0)


def test_momentum_signal_downtrend():
    prices = [105, 104, 103, 102, 101, 100]
    signal = momentum_signal(prices, lookback=2)

    assert np.all(signal[2:] == -1.0)


def test_mean_reversion_signal():
    prices = [100, 100, 100, 100, 100, 110]
    signal = mean_reversion_signal(
        prices,
        lookback=5,
        entry_zscore=1.0,
    )

    assert signal[-1] == 0.0


def test_position_sizing_and_cap():
    signal = np.array([1.0, -1.0, 1.0])
    volatility = np.array([0.05, 0.10, 0.50])

    positions = position_size(
        signal=signal,
        volatility=volatility,
        target_volatility=0.10,
        max_position=1.0,
    )

    assert np.allclose(positions, [1.0, -1.0, 0.2])


def test_execution_costs_reduce_returns():
    positions = [0.0, 1.0, 1.0]
    returns = [0.0, 0.01, 0.01]

    result, turnover, total_cost = simulate_execution(
        positions,
        returns,
        ExecutionConfig(
            transaction_cost_bps=10,
            slippage_bps=5,
        ),
    )

    assert turnover.tolist() == [0.0, 1.0, 0.0]
    assert total_cost == pytest.approx(0.0015)
    assert result[1] == pytest.approx(0.0085)
    assert result[2] == pytest.approx(0.01)


def test_market_impact_is_applied():
    result, _, total_cost = simulate_execution(
        [0.0, 1.0],
        [0.0, 0.01],
        ExecutionConfig(
            transaction_cost_bps=0,
            slippage_bps=0,
            market_impact_bps=10,
            impact_exponent=1.0,
        ),
    )

    assert total_cost == pytest.approx(0.001)
    assert result[-1] == pytest.approx(0.009)


def test_strategy_evaluation():
    result = evaluate_strategy(
        target_positions=[0.0, 1.0, 1.0, 0.0],
        asset_returns=[0.0, 0.01, 0.02, -0.01],
        execution=ExecutionConfig(
            transaction_cost_bps=0,
            slippage_bps=0,
        ),
    )

    assert result.observations == 4
    assert result.cumulative_return == pytest.approx(0.0302)
    assert result.total_turnover == pytest.approx(2.0)
    assert result.total_cost == pytest.approx(0.0)
    assert result.maximum_drawdown == pytest.approx(0.0)


def test_walk_forward_splits():
    splits = walk_forward_splits(
        observations=100,
        train_size=60,
        test_size=10,
        step_size=10,
    )

    assert len(splits) == 4
    assert splits[0].train_start == 0
    assert splits[0].train_end == 60
    assert splits[0].test_start == 60
    assert splits[0].test_end == 70
    assert splits[-1].test_end == 100


def test_walk_forward_has_no_train_test_overlap():
    splits = walk_forward_splits(
        observations=120,
        train_size=60,
        test_size=20,
        step_size=20,
    )

    for split in splits:
        assert split.train_end <= split.test_start


@pytest.mark.parametrize(
    "kwargs",
    [
        {"lookback": 0},
        {"lookback": 10},
    ],
)
def test_momentum_rejects_invalid_lookback(kwargs):
    with pytest.raises(ValueError):
        momentum_signal([100, 101, 102, 103, 104], **kwargs)


def test_position_sizing_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        position_size(
            signal=[1, 1],
            volatility=[0.1],
        )


def test_execution_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        simulate_execution(
            target_positions=[1, 1],
            asset_returns=[0.01],
        )


def test_strategy_evaluation_rejects_invalid_periods():
    with pytest.raises(ValueError):
        evaluate_strategy(
            target_positions=[1, 1],
            asset_returns=[0.01, 0.02],
            periods_per_year=0,
        )

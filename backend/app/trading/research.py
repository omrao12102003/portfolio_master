from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ExecutionConfig:
    transaction_cost_bps: float = 5.0
    slippage_bps: float = 2.0
    market_impact_bps: float = 0.0
    impact_exponent: float = 0.5


@dataclass(frozen=True)
class WalkForwardSplit:
    train_start: int
    train_end: int
    test_start: int
    test_end: int


@dataclass(frozen=True)
class ResearchResult:
    strategy_returns: np.ndarray
    cumulative_return: float
    annualized_return: float
    annualized_volatility: float
    sharpe_ratio: float
    maximum_drawdown: float
    total_turnover: float
    total_cost: float
    observations: int


def _as_1d_array(values: Sequence[float], name: str) -> np.ndarray:
    array = np.asarray(values, dtype=float)

    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional.")
    if len(array) == 0:
        raise ValueError(f"{name} cannot be empty.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain finite values.")

    return array


def _validate_returns(returns: Sequence[float]) -> np.ndarray:
    array = _as_1d_array(returns, "returns")

    if len(array) < 2:
        raise ValueError("returns must contain at least two observations.")

    return array


def momentum_signal(
    prices: Sequence[float],
    lookback: int = 20,
) -> np.ndarray:
    prices_array = _as_1d_array(prices, "prices")

    if np.any(prices_array <= 0):
        raise ValueError("prices must be positive.")
    if not isinstance(lookback, int) or lookback < 1:
        raise ValueError("lookback must be a positive integer.")
    if lookback >= len(prices_array):
        raise ValueError("lookback must be smaller than the number of prices.")

    signal = np.zeros(len(prices_array), dtype=float)
    signal[lookback:] = np.sign(
        prices_array[lookback:] / prices_array[:-lookback] - 1.0
    )

    return signal


def mean_reversion_signal(
    prices: Sequence[float],
    lookback: int = 20,
    entry_zscore: float = 1.0,
) -> np.ndarray:
    prices_array = _as_1d_array(prices, "prices")

    if np.any(prices_array <= 0):
        raise ValueError("prices must be positive.")
    if not isinstance(lookback, int) or lookback < 2:
        raise ValueError("lookback must be at least 2.")
    if lookback >= len(prices_array):
        raise ValueError("lookback must be smaller than the number of prices.")
    if entry_zscore <= 0:
        raise ValueError("entry_zscore must be positive.")

    signal = np.zeros(len(prices_array), dtype=float)

    for index in range(lookback, len(prices_array)):
        window = prices_array[index - lookback:index]
        mean = float(np.mean(window))
        std = float(np.std(window, ddof=1))

        if std == 0:
            continue

        zscore = (prices_array[index] - mean) / std

        if zscore > entry_zscore:
            signal[index] = -1.0
        elif zscore < -entry_zscore:
            signal[index] = 1.0

    return signal


def position_size(
    signal: Sequence[float],
    volatility: Sequence[float],
    target_volatility: float = 0.10,
    max_position: float = 1.0,
) -> np.ndarray:
    signal_array = _as_1d_array(signal, "signal")
    volatility_array = _as_1d_array(volatility, "volatility")

    if len(signal_array) != len(volatility_array):
        raise ValueError("signal and volatility must have equal lengths.")
    if target_volatility <= 0:
        raise ValueError("target_volatility must be positive.")
    if max_position <= 0:
        raise ValueError("max_position must be positive.")

    positions = np.zeros_like(signal_array)

    valid = volatility_array > 0
    positions[valid] = (
        signal_array[valid] * target_volatility / volatility_array[valid]
    )

    return np.clip(positions, -max_position, max_position)


def _validate_execution_config(config: ExecutionConfig) -> None:
    if config.transaction_cost_bps < 0:
        raise ValueError("transaction_cost_bps must be non-negative.")
    if config.slippage_bps < 0:
        raise ValueError("slippage_bps must be non-negative.")
    if config.market_impact_bps < 0:
        raise ValueError("market_impact_bps must be non-negative.")
    if config.impact_exponent <= 0:
        raise ValueError("impact_exponent must be positive.")


def simulate_execution(
    target_positions: Sequence[float],
    asset_returns: Sequence[float],
    config: ExecutionConfig | None = None,
) -> tuple[np.ndarray, np.ndarray, float]:
    positions = _as_1d_array(target_positions, "target_positions")
    returns = _as_1d_array(asset_returns, "asset_returns")

    if len(positions) != len(returns):
        raise ValueError("target_positions and asset_returns must have equal lengths.")

    config = config or ExecutionConfig()
    _validate_execution_config(config)

    previous = 0.0
    strategy_returns = np.zeros(len(positions), dtype=float)
    turnovers = np.zeros(len(positions), dtype=float)
    costs = np.zeros(len(positions), dtype=float)

    base_cost_rate = (
        config.transaction_cost_bps + config.slippage_bps
    ) / 10_000.0
    impact_rate = config.market_impact_bps / 10_000.0

    for index, position in enumerate(positions):
        turnover = abs(position - previous)
        impact = impact_rate * turnover ** config.impact_exponent
        cost = turnover * base_cost_rate + turnover * impact

        strategy_returns[index] = position * returns[index] - cost
        turnovers[index] = turnover
        costs[index] = cost
        previous = position

    return strategy_returns, turnovers, float(np.sum(costs))


def _annualized_return(returns: np.ndarray, periods_per_year: int) -> float:
    cumulative = float(np.prod(1.0 + returns))

    if cumulative <= 0:
        return -1.0

    return cumulative ** (periods_per_year / len(returns)) - 1.0


def _annualized_volatility(returns: np.ndarray, periods_per_year: int) -> float:
    if len(returns) < 2:
        return 0.0

    return float(np.std(returns, ddof=1) * np.sqrt(periods_per_year))


def _sharpe_ratio(
    returns: np.ndarray,
    periods_per_year: int,
    risk_free_rate: float,
) -> float:
    excess = returns - risk_free_rate / periods_per_year
    volatility = np.std(excess, ddof=1)

    if volatility == 0:
        return 0.0

    return float(
        np.mean(excess) / volatility * np.sqrt(periods_per_year)
    )


def _maximum_drawdown(returns: np.ndarray) -> float:
    equity = np.cumprod(1.0 + returns)

    if np.any(equity <= 0):
        return -1.0

    running_max = np.maximum.accumulate(equity)
    drawdowns = equity / running_max - 1.0

    return float(np.min(drawdowns))


def evaluate_strategy(
    target_positions: Sequence[float],
    asset_returns: Sequence[float],
    execution: ExecutionConfig | None = None,
    periods_per_year: int = 252,
    risk_free_rate: float = 0.0,
) -> ResearchResult:
    if not isinstance(periods_per_year, int) or periods_per_year < 1:
        raise ValueError("periods_per_year must be a positive integer.")

    returns, turnovers, total_cost = simulate_execution(
        target_positions=target_positions,
        asset_returns=asset_returns,
        config=execution,
    )

    cumulative_return = float(np.prod(1.0 + returns) - 1.0)

    return ResearchResult(
        strategy_returns=returns,
        cumulative_return=cumulative_return,
        annualized_return=_annualized_return(
            returns,
            periods_per_year,
        ),
        annualized_volatility=_annualized_volatility(
            returns,
            periods_per_year,
        ),
        sharpe_ratio=_sharpe_ratio(
            returns,
            periods_per_year,
            risk_free_rate,
        ),
        maximum_drawdown=_maximum_drawdown(returns),
        total_turnover=float(np.sum(turnovers)),
        total_cost=total_cost,
        observations=len(returns),
    )


def walk_forward_splits(
    observations: int,
    train_size: int,
    test_size: int,
    step_size: int | None = None,
) -> list[WalkForwardSplit]:
    if not isinstance(observations, int) or observations < 2:
        raise ValueError("observations must be at least 2.")
    if not isinstance(train_size, int) or train_size < 1:
        raise ValueError("train_size must be positive.")
    if not isinstance(test_size, int) or test_size < 1:
        raise ValueError("test_size must be positive.")

    step = step_size if step_size is not None else test_size

    if not isinstance(step, int) or step < 1:
        raise ValueError("step_size must be positive.")
    if train_size + test_size > observations:
        raise ValueError("train_size + test_size exceeds observations.")

    splits = []
    train_end = train_size

    while train_end + test_size <= observations:
        splits.append(
            WalkForwardSplit(
                train_start=0,
                train_end=train_end,
                test_start=train_end,
                test_end=train_end + test_size,
            )
        )
        train_end += step

    return splits

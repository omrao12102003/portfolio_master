from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BacktestResult:
    equity_curve: pd.Series
    portfolio_returns: pd.Series
    turnover: pd.Series
    transaction_costs: pd.Series
    weights: pd.DataFrame


def validate_prices(prices: pd.DataFrame) -> None:
    if prices.empty:
        raise ValueError("Prices cannot be empty.")

    if prices.isna().any().any():
        raise ValueError("Prices cannot contain missing values.")

    if (prices <= 0).any().any():
        raise ValueError("Prices must be positive.")

    if not prices.index.is_monotonic_increasing:
        raise ValueError("Price index must be sorted chronologically.")

    if prices.index.has_duplicates:
        raise ValueError("Price index cannot contain duplicates.")


def validate_target_weights(weights: pd.Series) -> None:
    if weights.empty:
        raise ValueError("Weights cannot be empty.")

    if weights.isna().any():
        raise ValueError("Weights cannot contain missing values.")

    if (weights < 0).any():
        raise ValueError("Negative weights are not supported.")

    if not np.isclose(weights.sum(), 1.0):
        raise ValueError("Weights must sum to 1.")


def run_backtest(
    prices: pd.DataFrame,
    target_weights: pd.Series,
    initial_capital: float = 100_000.0,
    transaction_cost_bps: float = 5.0,
    rebalance_frequency: str = "daily",
) -> BacktestResult:
    validate_prices(prices)
    validate_target_weights(target_weights)

    if initial_capital <= 0:
        raise ValueError("Initial capital must be positive.")

    if transaction_cost_bps < 0:
        raise ValueError("Transaction costs cannot be negative.")

    missing_assets = target_weights.index.difference(prices.columns)
    if not missing_assets.empty:
        raise ValueError(
            f"Missing price data for assets: {list(missing_assets)}"
        )

    prices = prices.loc[:, target_weights.index].copy()

    asset_returns = prices.pct_change().fillna(0.0)

    rebalance_mask = _rebalance_mask(
        prices.index,
        rebalance_frequency,
    )

    current_weights = pd.Series(
        0.0,
        index=target_weights.index,
        dtype=float,
    )

    portfolio_returns: list[float] = []
    turnover_values: list[float] = []
    cost_values: list[float] = []
    weight_rows: list[pd.Series] = []

    equity = initial_capital
    equity_values = [equity]

    for i, date in enumerate(prices.index):
        if i == 0:
            turnover = float(target_weights.abs().sum())
            cost = turnover * transaction_cost_bps / 10_000.0
            current_weights = target_weights.copy()
            portfolio_return = -cost
        else:
            drifted = current_weights * (1.0 + asset_returns.loc[date])
            drifted_total = float(drifted.sum())

            if drifted_total <= 0:
                raise ValueError("Portfolio value became non-positive.")

            drifted = drifted / drifted_total

            if rebalance_mask[i]:
                turnover = float((target_weights - drifted).abs().sum())
                cost = turnover * transaction_cost_bps / 10_000.0
                current_weights = target_weights.copy()
            else:
                turnover = 0.0
                cost = 0.0
                current_weights = drifted

            portfolio_return = float(
                np.dot(
                    current_weights.values,
                    asset_returns.loc[date].values,
                )
                - cost
            )

        equity *= 1.0 + portfolio_return

        portfolio_returns.append(portfolio_return)
        turnover_values.append(turnover)
        cost_values.append(cost)
        weight_rows.append(current_weights.copy())
        if i > 0:
            equity_values.append(equity)

    equity_curve = pd.Series(
        equity_values,
        index=prices.index,
        name="equity",
    )

    return BacktestResult(
        equity_curve=equity_curve,
        portfolio_returns=pd.Series(
            portfolio_returns,
            index=prices.index,
            name="portfolio_return",
        ),
        turnover=pd.Series(
            turnover_values,
            index=prices.index,
            name="turnover",
        ),
        transaction_costs=pd.Series(
            cost_values,
            index=prices.index,
            name="transaction_cost",
        ),
        weights=pd.DataFrame(
            weight_rows,
            index=prices.index,
        ),
    )


def backtest_summary(result: BacktestResult) -> dict[str, float]:
    returns = result.portfolio_returns

    cumulative_return = float(
        result.equity_curve.iloc[-1] / result.equity_curve.iloc[0] - 1.0
    )

    periods = len(returns)
    annualized_return = (
        float((1.0 + cumulative_return) ** (252 / periods) - 1.0)
        if periods > 0 and 1.0 + cumulative_return > 0
        else float("nan")
    )

    annualized_volatility = float(returns.std(ddof=1) * np.sqrt(252))

    running_max = result.equity_curve.cummax()
    drawdown = result.equity_curve / running_max - 1.0
    maximum_drawdown = float(drawdown.min())

    return {
        "initial_capital": float(result.equity_curve.iloc[0]),
        "final_capital": float(result.equity_curve.iloc[-1]),
        "cumulative_return": cumulative_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "maximum_drawdown": maximum_drawdown,
        "total_turnover": float(result.turnover.sum()),
        "total_transaction_cost": float(result.transaction_costs.sum()),
    }


def _rebalance_mask(index: pd.Index, frequency: str) -> np.ndarray:
    if frequency not in {"daily", "weekly", "monthly"}:
        raise ValueError(
            "Rebalance frequency must be daily, weekly, or monthly."
        )

    if frequency == "daily":
        return np.ones(len(index), dtype=bool)

    dates = pd.DatetimeIndex(index)

    if frequency == "weekly":
        periods = dates.to_period("W")
    else:
        periods = dates.to_period("M")

    mask = np.zeros(len(index), dtype=bool)
    mask[0] = True

    if len(index) > 1:
        mask[1:] = periods[1:] != periods[:-1]

    return mask

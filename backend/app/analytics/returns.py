from __future__ import annotations

import numpy as np
import pandas as pd


def simple_returns(prices: pd.Series) -> pd.Series:
    return prices.pct_change()


def log_returns(prices: pd.Series) -> pd.Series:
    if (prices.dropna() <= 0).any():
        raise ValueError("Prices must be positive for log returns.")
    return np.log(prices / prices.shift(1))


def cumulative_returns(returns: pd.Series) -> pd.Series:
    return (1 + returns.fillna(0)).cumprod() - 1


def annualized_return(
    returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    clean = returns.dropna()

    if clean.empty:
        return float("nan")

    growth = (1 + clean).prod()

    if growth <= 0:
        return float("nan")

    return float(growth ** (periods_per_year / len(clean)) - 1)


def annualized_volatility(
    returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    clean = returns.dropna()

    if len(clean) < 2:
        return float("nan")

    return float(clean.std(ddof=1) * np.sqrt(periods_per_year))


def downside_volatility(
    returns: pd.Series,
    periods_per_year: int = 252,
    minimum_return: float = 0.0,
) -> float:
    clean = returns.dropna()
    downside = np.minimum(clean - minimum_return, 0.0)

    if clean.empty:
        return float("nan")

    return float(np.sqrt(np.mean(downside**2)) * np.sqrt(periods_per_year))


def sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    clean = returns.dropna()

    if len(clean) < 2:
        return float("nan")

    periodic_rf = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    excess = clean - periodic_rf
    volatility = excess.std(ddof=1)

    if volatility == 0:
        return float("nan")

    return float(excess.mean() / volatility * np.sqrt(periods_per_year))


def sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    clean = returns.dropna()

    if clean.empty:
        return float("nan")

    periodic_rf = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
    excess = clean - periodic_rf
    downside = np.minimum(excess, 0.0)
    downside_deviation = np.sqrt(np.mean(downside**2))

    if downside_deviation == 0:
        return float("nan")

    return float(excess.mean() / downside_deviation * np.sqrt(periods_per_year))


def drawdown(returns: pd.Series) -> pd.Series:
    wealth = (1 + returns.fillna(0)).cumprod()
    running_peak = wealth.cummax()
    return wealth / running_peak - 1


def maximum_drawdown(returns: pd.Series) -> float:
    dd = drawdown(returns)

    if dd.empty:
        return float("nan")

    return float(dd.min())


def rolling_volatility(
    returns: pd.Series,
    window: int = 21,
    periods_per_year: int = 252,
) -> pd.Series:
    if window <= 1:
        raise ValueError("window must be greater than 1")

    return returns.rolling(window).std(ddof=1) * np.sqrt(periods_per_year)

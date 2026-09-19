from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PortfolioState:
    weights: np.ndarray
    portfolio_value: float
    step: int


class PortfolioEnvironment:
    def __init__(
        self,
        returns: pd.DataFrame,
        initial_capital: float = 100_000.0,
        transaction_cost_bps: float = 5.0,
    ) -> None:
        if returns.empty:
            raise ValueError("Returns cannot be empty.")
        if returns.isna().any().any():
            raise ValueError("Returns cannot contain missing values.")
        if len(returns) < 2:
            raise ValueError("Returns must contain at least two observations.")
        if initial_capital <= 0:
            raise ValueError("Initial capital must be positive.")
        if transaction_cost_bps < 0:
            raise ValueError("Transaction costs cannot be negative.")

        self.returns = returns.copy()
        self.initial_capital = float(initial_capital)
        self.transaction_cost_bps = float(transaction_cost_bps)
        self.asset_count = returns.shape[1]
        self.reset()

    def reset(self) -> PortfolioState:
        self.current_step = 0
        self.portfolio_value = self.initial_capital
        self.weights = np.full(
            self.asset_count,
            1.0 / self.asset_count,
            dtype=float,
        )
        return self._state()

    def step(self, target_weights: np.ndarray) -> tuple[PortfolioState, float, bool]:
        target_weights = self._validate_weights(target_weights)

        current_returns = self.returns.iloc[self.current_step].to_numpy(
            dtype=float
        )

        turnover = float(np.abs(target_weights - self.weights).sum())
        transaction_cost = (
            turnover * self.transaction_cost_bps / 10_000.0
        )

        portfolio_return = float(
            np.dot(target_weights, current_returns)
        )

        reward = portfolio_return - transaction_cost
        self.portfolio_value *= 1.0 + reward
        self.weights = target_weights

        self.current_step += 1
        done = self.current_step >= len(self.returns)

        return self._state(), reward, done

    def _state(self) -> PortfolioState:
        return PortfolioState(
            weights=self.weights.copy(),
            portfolio_value=self.portfolio_value,
            step=self.current_step,
        )

    def _validate_weights(self, weights: np.ndarray) -> np.ndarray:
        weights = np.asarray(weights, dtype=float)

        if weights.shape != (self.asset_count,):
            raise ValueError("Weight dimensions do not match assets.")
        if not np.isfinite(weights).all():
            raise ValueError("Weights must be finite.")
        if (weights < 0).any():
            raise ValueError("Negative weights are not supported.")
        if not np.isclose(weights.sum(), 1.0):
            raise ValueError("Weights must sum to 1.")

        return weights.copy()

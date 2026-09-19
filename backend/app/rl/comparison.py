from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from app.optimization.classical import (
    maximum_sharpe,
    minimum_volatility,
    risk_parity,
)
from app.rl.agent import DiscretePortfolioAgent
from app.rl.baselines import equal_weight_action
from app.rl.trainer import RLEvaluation, evaluate_agent


@dataclass(frozen=True)
class StrategyEvaluation:
    name: str
    evaluation: RLEvaluation


def evaluate_strategies(
    fit_returns: pd.DataFrame,
    evaluation_returns: pd.DataFrame,
    agent: DiscretePortfolioAgent,
    selected_action: int,
    initial_capital: float = 100_000.0,
    transaction_cost_bps: float = 5.0,
    risk_free_rate: float = 0.0,
) -> list[StrategyEvaluation]:
    if fit_returns.empty:
        raise ValueError("Fit returns cannot be empty.")
    if evaluation_returns.empty:
        raise ValueError("Evaluation returns cannot be empty.")
    if list(fit_returns.columns) != list(evaluation_returns.columns):
        raise ValueError("Fit and evaluation assets must match.")

    expected_returns = fit_returns.mean()
    covariance = fit_returns.cov()

    strategies: list[tuple[str, np.ndarray]] = [
        ("RL", agent.select_action(selected_action).weights),
        (
            "Equal Weight",
            equal_weight_action(fit_returns.shape[1]),
        ),
        (
            "Minimum Volatility",
            minimum_volatility(
                expected_returns,
                covariance,
            ).to_numpy(),
        ),
        (
            "Maximum Sharpe",
            maximum_sharpe(
                expected_returns,
                covariance,
                risk_free_rate=risk_free_rate,
            ).to_numpy(),
        ),
        (
            "Risk Parity",
            risk_parity(
                expected_returns,
                covariance,
            ).to_numpy(),
        ),
    ]

    results: list[StrategyEvaluation] = []

    for name, weights in strategies:
        strategy_agent = DiscretePortfolioAgent([weights])
        evaluation = evaluate_agent(
            evaluation_returns,
            strategy_agent,
            0,
            initial_capital=initial_capital,
            transaction_cost_bps=transaction_cost_bps,
        )
        results.append(
            StrategyEvaluation(
                name=name,
                evaluation=evaluation,
            )
        )

    return results

from __future__ import annotations


def portfolio_reward(
    portfolio_return: float,
    transaction_cost: float = 0.0,
    risk_penalty: float = 0.0,
    turnover_penalty: float = 0.0,
) -> float:
    return (
        portfolio_return
        - transaction_cost
        - risk_penalty
        - turnover_penalty
    )

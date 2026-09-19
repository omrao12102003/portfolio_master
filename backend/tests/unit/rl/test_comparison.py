import numpy as np
import pandas as pd
import pytest

from app.rl.agent import DiscretePortfolioAgent
from app.rl.comparison import evaluate_strategies


def test_evaluate_strategies():
    fit_returns = pd.DataFrame(
        [
            [0.01, 0.02, 0.015],
            [0.02, 0.01, 0.01],
            [0.00, 0.03, 0.012],
            [0.01, 0.01, 0.008],
        ],
        columns=["A", "B", "C"],
    )
    evaluation_returns = pd.DataFrame(
        [
            [0.02, 0.01, 0.012],
            [0.01, 0.02, 0.011],
            [0.015, 0.01, 0.013],
            [0.00, 0.02, 0.010],
        ],
        columns=["A", "B", "C"],
    )

    agent = DiscretePortfolioAgent(
        [
            np.array([0.5, 0.3, 0.2]),
            np.array([0.2, 0.6, 0.2]),
        ]
    )

    results = evaluate_strategies(
        fit_returns,
        evaluation_returns,
        agent,
        selected_action=1,
        transaction_cost_bps=0,
    )

    assert [result.name for result in results] == [
        "RL",
        "Equal Weight",
        "Minimum Volatility",
        "Maximum Sharpe",
        "Risk Parity",
    ]
    assert len(results) == 5

    for result in results:
        assert result.evaluation.final_value > 0


def test_strategy_weights_are_valid():
    fit_returns = pd.DataFrame(
        [
            [0.01, 0.02, 0.015],
            [0.02, 0.01, 0.01],
            [0.00, 0.03, 0.012],
            [0.01, 0.01, 0.008],
        ],
        columns=["A", "B", "C"],
    )
    evaluation_returns = fit_returns.copy()

    agent = DiscretePortfolioAgent(
        [np.array([1 / 3, 1 / 3, 1 / 3])]
    )

    results = evaluate_strategies(
        fit_returns,
        evaluation_returns,
        agent,
        selected_action=0,
        transaction_cost_bps=0,
    )

    for result in results:
        assert result.evaluation.final_value > 0


def test_fit_period_is_used_for_classical_weights():
    fit_returns = pd.DataFrame(
        [
            [0.020, 0.010, 0.015],
            [0.030, 0.005, 0.010],
            [0.010, 0.015, 0.020],
            [0.025, 0.008, 0.012],
            [0.015, 0.020, 0.008],
            [0.005, 0.012, 0.018],
        ],
        columns=["A", "B", "C"],
    )

    evaluation_returns = pd.DataFrame(
        [
            [-0.50, 0.50, 0.00],
            [-0.50, 0.50, 0.00],
        ],
        columns=["A", "B", "C"],
    )

    agent = DiscretePortfolioAgent(
        [np.array([1 / 3, 1 / 3, 1 / 3])]
    )

    fit_results = evaluate_strategies(
        fit_returns,
        evaluation_returns,
        agent,
        selected_action=0,
        transaction_cost_bps=0,
    )

    contaminated_results = evaluate_strategies(
        evaluation_returns,
        evaluation_returns,
        agent,
        selected_action=0,
        transaction_cost_bps=0,
    )

    fit_values = {
        result.name: result.evaluation.final_value
        for result in fit_results
    }
    contaminated_values = {
        result.name: result.evaluation.final_value
        for result in contaminated_results
    }

    assert fit_values["Minimum Volatility"] != contaminated_values["Minimum Volatility"]


def test_mismatched_assets_raise():
    fit_returns = pd.DataFrame(
        [[0.01, 0.02], [0.02, 0.01]],
        columns=["A", "B"],
    )
    evaluation_returns = pd.DataFrame(
        [[0.01, 0.02], [0.02, 0.01]],
        columns=["A", "C"],
    )

    agent = DiscretePortfolioAgent(
        [np.array([0.5, 0.5])]
    )

    with pytest.raises(ValueError, match="assets must match"):
        evaluate_strategies(
            fit_returns,
            evaluation_returns,
            agent,
            selected_action=0,
        )

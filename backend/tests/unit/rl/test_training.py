import numpy as np
import pandas as pd
import pytest

from app.rl.trainer import train_discrete_agent


def test_training_selects_best_training_action():
    returns = pd.DataFrame(
        [
            [0.04, 0.01],
            [0.03, 0.00],
            [0.02, -0.01],
        ],
        columns=["A", "B"],
    )

    actions = [
        np.array([0.5, 0.5]),
        np.array([1.0, 0.0]),
    ]

    _, result = train_discrete_agent(
        returns,
        actions,
        transaction_cost_bps=0,
    )

    assert result.selected_action == 1
    assert result.training_rewards[1] > result.training_rewards[0]


def test_training_rejects_empty_data():
    returns = pd.DataFrame(columns=["A", "B"])

    with pytest.raises(ValueError, match="Training returns cannot be empty"):
        train_discrete_agent(
            returns,
            [np.array([0.5, 0.5])],
        )

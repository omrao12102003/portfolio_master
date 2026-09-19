import numpy as np
import pandas as pd

from app.rl.pipeline import run_rl_pipeline


def test_rl_pipeline_includes_q_learning_evaluation():
    returns = pd.DataFrame(
        [
            [0.02, 0.01, 0.015],
            [0.03, 0.005, 0.01],
            [0.01, 0.02, 0.015],
            [0.025, 0.01, 0.012],
            [0.015, 0.02, 0.01],
            [0.01, 0.015, 0.02],
            [-0.01, 0.02, 0.01],
            [0.02, -0.01, 0.015],
            [0.015, 0.01, 0.02],
            [0.01, 0.02, 0.015],
        ],
        columns=["A", "B", "C"],
    )

    actions = [
        np.array([1 / 3, 1 / 3, 1 / 3]),
        np.array([0.6, 0.2, 0.2]),
        np.array([0.2, 0.6, 0.2]),
    ]

    result = run_rl_pipeline(returns, actions)

    assert result.selected_action in range(3)
    assert result.validation.final_value > 0
    assert result.test.final_value > 0
    assert result.q_learning_validation.final_value > 0
    assert result.q_learning_test.final_value > 0

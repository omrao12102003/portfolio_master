import numpy as np

from app.rl.baselines import equal_weight_action


def test_equal_weight_action():
    result = equal_weight_action(4)

    assert np.allclose(result, [0.25, 0.25, 0.25, 0.25])

from __future__ import annotations

import numpy as np


def equal_weight_action(asset_count: int) -> np.ndarray:
    if asset_count < 2:
        raise ValueError("At least two assets are required.")

    return np.full(
        asset_count,
        1.0 / asset_count,
        dtype=float,
    )

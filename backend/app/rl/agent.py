from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DiscreteAction:
    weights: np.ndarray


class DiscretePortfolioAgent:
    def __init__(self, actions: list[np.ndarray]) -> None:
        if not actions:
            raise ValueError("At least one action is required.")

        self.actions = [
            self._validate_action(action)
            for action in actions
        ]

    def select_action(self, index: int) -> DiscreteAction:
        if index < 0 or index >= len(self.actions):
            raise IndexError("Action index is out of range.")

        return DiscreteAction(self.actions[index].copy())

    @staticmethod
    def _validate_action(action: np.ndarray) -> np.ndarray:
        weights = np.asarray(action, dtype=float)

        if weights.ndim != 1:
            raise ValueError("Action weights must be one-dimensional.")
        if len(weights) < 2:
            raise ValueError("At least two assets are required.")
        if not np.isfinite(weights).all():
            raise ValueError("Action weights must be finite.")
        if (weights < 0).any():
            raise ValueError("Action weights cannot be negative.")
        if not np.isclose(weights.sum(), 1.0):
            raise ValueError("Action weights must sum to 1.")

        return weights.copy()

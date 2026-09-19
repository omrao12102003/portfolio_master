from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RLDataSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def chronological_split(
    returns: pd.DataFrame,
    train_ratio: float = 0.6,
    validation_ratio: float = 0.2,
) -> RLDataSplit:
    if returns.empty:
        raise ValueError("Returns cannot be empty.")
    if returns.isna().any().any():
        raise ValueError("Returns cannot contain missing values.")
    if not 0 < train_ratio < 1:
        raise ValueError("Train ratio must be between 0 and 1.")
    if not 0 < validation_ratio < 1:
        raise ValueError("Validation ratio must be between 0 and 1.")
    if train_ratio + validation_ratio >= 1:
        raise ValueError("Train and validation ratios must sum to less than 1.")

    train_end = int(len(returns) * train_ratio)
    validation_end = train_end + int(len(returns) * validation_ratio)

    if train_end == 0 or validation_end >= len(returns):
        raise ValueError("Dataset is too small for the requested split.")

    return RLDataSplit(
        train=returns.iloc[:train_end].copy(),
        validation=returns.iloc[train_end:validation_end].copy(),
        test=returns.iloc[validation_end:].copy(),
    )

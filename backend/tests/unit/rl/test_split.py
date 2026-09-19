import pandas as pd
import pytest

from app.rl.split import chronological_split


def test_chronological_split_preserves_order():
    returns = pd.DataFrame(
        {"A": range(10)},
        index=pd.date_range("2024-01-01", periods=10),
    )

    result = chronological_split(
        returns,
        train_ratio=0.6,
        validation_ratio=0.2,
    )

    assert len(result.train) == 6
    assert len(result.validation) == 2
    assert len(result.test) == 2
    assert result.train.index[-1] < result.validation.index[0]
    assert result.validation.index[-1] < result.test.index[0]


def test_split_rejects_invalid_ratios():
    returns = pd.DataFrame({"A": range(10)})

    with pytest.raises(ValueError):
        chronological_split(returns, train_ratio=0.8, validation_ratio=0.3)

from __future__ import annotations

from collections.abc import Sequence


def precision_at_k(
    retrieved: Sequence[str],
    relevant: set[str],
    k: int,
) -> float:
    if k < 1:
        raise ValueError("k must be positive.")

    selected = list(retrieved[:k])
    if not selected:
        return 0.0

    return sum(item in relevant for item in selected) / len(selected)


def recall_at_k(
    retrieved: Sequence[str],
    relevant: set[str],
    k: int,
) -> float:
    if k < 1:
        raise ValueError("k must be positive.")

    if not relevant:
        return 0.0

    selected = set(retrieved[:k])
    return len(selected & relevant) / len(relevant)


def mean_reciprocal_rank(
    retrieved: Sequence[str],
    relevant: set[str],
) -> float:
    if not relevant:
        return 0.0

    for index, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / index

    return 0.0

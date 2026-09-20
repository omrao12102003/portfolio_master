import pytest

from app.research.retrieval_evaluation import (
    mean_reciprocal_rank,
    precision_at_k,
    recall_at_k,
)


def test_precision_at_k():
    assert precision_at_k(["a", "b", "c"], {"a", "c"}, 3) == pytest.approx(2 / 3)


def test_recall_at_k():
    assert recall_at_k(["a", "b", "c"], {"a", "c"}, 2) == pytest.approx(0.5)


def test_reciprocal_rank():
    assert mean_reciprocal_rank(["x", "b", "c"], {"b"}) == pytest.approx(0.5)


def test_no_relevant_results():
    assert mean_reciprocal_rank(["x", "y"], {"a"}) == 0.0


def test_empty_relevant_set():
    assert recall_at_k(["a"], set(), 1) == 0.0


def test_invalid_k():
    with pytest.raises(ValueError):
        precision_at_k(["a"], {"a"}, 0)

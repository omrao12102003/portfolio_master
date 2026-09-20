from types import SimpleNamespace

import pytest

from app.research.hybrid_retrieval import HybridResearchRetriever
from app.research.semantic_retrieval import RetrievalFilters


def make_result(
    chunk_id: str,
    distance: float,
    content: str,
    title: str = "Annual Report",
    section: str = "Business",
):
    return SimpleNamespace(
        chunk_id=chunk_id,
        document_id="doc-1",
        title=title,
        source="SEC EDGAR",
        published_date="2025-01-01",
        section=section,
        content=content,
        distance=distance,
    )


class FakeRetriever:
    def __init__(self, results):
        self.results = results

    def retrieve(self, query, *, limit=5, filters=None):
        return self.results[:limit]


def test_hybrid_retrieval_combines_scores():
    results = [
        make_result(
            "b",
            0.05,
            "Revenue increased and operating income improved.",
        ),
        make_result(
            "a",
            0.01,
            "The company discusses unrelated market conditions.",
        ),
    ]

    retriever = HybridResearchRetriever(FakeRetriever(results))

    ranked = retriever.retrieve("revenue operating income", limit=2)

    assert len(ranked) == 2
    assert ranked[0].chunk_id == "b"
    assert 0 <= ranked[0].final_score <= 1


def test_hybrid_retrieval_is_deterministic():
    results = [
        make_result("b", 0.1, "Revenue discussion."),
        make_result("a", 0.1, "Revenue discussion."),
    ]

    retriever = HybridResearchRetriever(FakeRetriever(results))

    first = retriever.retrieve("revenue", limit=2)
    second = retriever.retrieve("revenue", limit=2)

    assert [item.chunk_id for item in first] == [
        item.chunk_id for item in second
    ]


def test_hybrid_retrieval_respects_limit():
    results = [
        make_result(str(index), 0.1, "Revenue discussion.")
        for index in range(5)
    ]

    retriever = HybridResearchRetriever(FakeRetriever(results))

    assert len(retriever.retrieve("revenue", limit=3)) == 3


def test_empty_query_rejected():
    retriever = HybridResearchRetriever(FakeRetriever([]))

    with pytest.raises(ValueError, match="Query cannot be empty"):
        retriever.retrieve("")


def test_invalid_weights_rejected():
    with pytest.raises(ValueError):
        HybridResearchRetriever(FakeRetriever([]), semantic_weight=0, lexical_weight=0)


def test_weights_are_normalized():
    retriever = HybridResearchRetriever(
        FakeRetriever([]),
        semantic_weight=2,
        lexical_weight=1,
    )

    assert retriever.semantic_weight == pytest.approx(2 / 3)
    assert retriever.lexical_weight == pytest.approx(1 / 3)


def test_filters_are_forwarded():
    class RecordingRetriever:
        def __init__(self):
            self.filters = None

        def retrieve(self, query, *, limit=5, filters=None):
            self.filters = filters
            return []

    underlying = RecordingRetriever()
    retriever = HybridResearchRetriever(underlying)
    filters = RetrievalFilters(ticker="AAPL")

    retriever.retrieve("revenue", filters=filters)

    assert underlying.filters == filters

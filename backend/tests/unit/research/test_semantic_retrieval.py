from unittest.mock import Mock

import pytest

from app.research.embeddings import HashEmbeddingProvider
from app.research.semantic_retrieval import (
    RetrievalFilters,
    SemanticResearchRetriever,
)


def test_retriever_embeds_query_and_searches():
    provider = HashEmbeddingProvider(dimension=32)
    store = Mock()
    store.search.return_value = []

    retriever = SemanticResearchRetriever(store, provider)

    results = retriever.retrieve("revenue growth", limit=3)

    assert results == []
    store.search.assert_called_once()

    args, kwargs = store.search.call_args

    assert len(args[0]) == 32
    assert kwargs["limit"] == 3


def test_retriever_passes_filters():
    provider = HashEmbeddingProvider(dimension=32)
    store = Mock()
    store.search.return_value = []

    retriever = SemanticResearchRetriever(store, provider)

    filters = RetrievalFilters(
        company="Apple",
        ticker="AAPL",
        document_type="10-K",
        published_before="2025-12-31",
        section="Risk Factors",
    )

    retriever.retrieve(
        "supply chain risk",
        limit=7,
        filters=filters,
    )

    _, kwargs = store.search.call_args

    assert kwargs["limit"] == 7
    assert kwargs["company"] == "Apple"
    assert kwargs["ticker"] == "AAPL"
    assert kwargs["document_type"] == "10-K"
    assert kwargs["published_before"] == "2025-12-31"
    assert kwargs["section"] == "Risk Factors"


def test_empty_query_is_rejected():
    provider = HashEmbeddingProvider(dimension=32)
    store = Mock()

    retriever = SemanticResearchRetriever(store, provider)

    with pytest.raises(ValueError, match="Query cannot be empty"):
        retriever.retrieve("")


def test_invalid_limit_is_rejected():
    provider = HashEmbeddingProvider(dimension=32)
    store = Mock()

    retriever = SemanticResearchRetriever(store, provider)

    with pytest.raises(ValueError, match="limit must be positive"):
        retriever.retrieve("revenue", limit=0)

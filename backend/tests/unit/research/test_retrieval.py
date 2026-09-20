import pytest

from app.research.retrieval import ResearchDocument, ResearchRetriever


@pytest.fixture
def retriever():
    documents = [
        ResearchDocument(
            document_id="doc-1",
            title="Annual Report",
            source="company.com/report",
            content=(
                "Revenue increased by 12 percent during the year. "
                "Operating margin also improved."
            ),
            published_date="2025-12-31",
        ),
        ResearchDocument(
            document_id="doc-2",
            title="Investor Presentation",
            source="company.com/investor",
            content=(
                "Management expects stronger demand and continued revenue growth."
            ),
            published_date="2026-01-15",
        ),
    ]
    return ResearchRetriever(documents)


def test_retrieval_returns_relevant_documents(retriever):
    results = retriever.retrieve("revenue growth", top_k=2)

    assert len(results) == 2
    assert results[0].document_id in {"doc-1", "doc-2"}
    assert results[0].source


def test_retrieval_preserves_metadata(retriever):
    results = retriever.retrieve("operating margin")

    assert len(results) == 1
    assert results[0].document_id == "doc-1"
    assert results[0].title == "Annual Report"
    assert results[0].source == "company.com/report"
    assert results[0].published_date == "2025-12-31"
    assert results[0].chunk_index == 0


def test_top_k_is_respected(retriever):
    results = retriever.retrieve("revenue", top_k=1)

    assert len(results) == 1


@pytest.mark.parametrize("query", ["", "   "])
def test_empty_query_is_rejected(retriever, query):
    with pytest.raises(ValueError, match="Research query"):
        retriever.retrieve(query)


def test_invalid_top_k_is_rejected(retriever):
    with pytest.raises(ValueError, match="top_k"):
        retriever.retrieve("revenue", top_k=0)


def test_no_matching_documents_returns_empty(retriever):
    assert retriever.retrieve("quantum computing") == []

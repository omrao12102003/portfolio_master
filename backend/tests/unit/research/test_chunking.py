from app.research.chunking import FinancialDocumentChunker
from app.research.retrieval import ResearchDocument


def make_document(content: str) -> ResearchDocument:
    return ResearchDocument(
        document_id="doc-1",
        title="Annual Report",
        source="SEC EDGAR",
        content=content,
        published_date="2025-01-01",
    )


def test_chunker_preserves_document_metadata():
    document = make_document(
        "ITEM 1. BUSINESS\n"
        "Revenue increased significantly during the year. "
        "The company expanded its operations and invested in technology."
    )

    chunks = FinancialDocumentChunker(chunk_size=20, overlap=5).chunk(document)

    assert chunks
    assert all(chunk.document_id == "doc-1" for chunk in chunks)
    assert all(chunk.title == "Annual Report" for chunk in chunks)
    assert all(chunk.source == "SEC EDGAR" for chunk in chunks)
    assert all(chunk.published_date == "2025-01-01" for chunk in chunks)


def test_chunker_assigns_unique_chunk_ids():
    document = make_document(
        "ITEM 1. BUSINESS\n" + "Revenue increased. " * 100
    )

    chunks = FinancialDocumentChunker(
        chunk_size=20,
        overlap=5,
    ).chunk(document)

    ids = [chunk.chunk_id for chunk in chunks]

    assert len(ids) > 1
    assert len(ids) == len(set(ids))
    assert ids == [f"doc-1-{index}" for index in range(len(ids))]


def test_chunker_detects_financial_sections():
    document = make_document(
        "ITEM 1. BUSINESS\n"
        "The company operates globally.\n"
        "ITEM 1A. RISK FACTORS\n"
        "Market volatility may affect results.\n"
        "ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS\n"
        "Revenue increased during the period."
    )

    chunks = FinancialDocumentChunker(chunk_size=100).chunk(document)

    sections = {chunk.section for chunk in chunks}

    assert "ITEM 1. BUSINESS" in sections
    assert "ITEM 1A. RISK FACTORS" in sections
    assert "ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS" in sections


def test_chunker_applies_overlap():
    document = make_document(
        " ".join(f"word{i}" for i in range(100))
    )

    chunks = FinancialDocumentChunker(
        chunk_size=20,
        overlap=5,
    ).chunk(document)

    first_words = chunks[0].content.split()
    second_words = chunks[1].content.split()

    assert first_words[-5:] == second_words[:5]


def test_chunker_rejects_invalid_configuration():
    try:
        FinancialDocumentChunker(chunk_size=10, overlap=10)
    except ValueError as exc:
        assert "overlap must be smaller" in str(exc)
    else:
        raise AssertionError("Expected invalid overlap to fail")


def test_chunker_rejects_empty_document():
    document = make_document("")

    try:
        FinancialDocumentChunker().chunk(document)
    except ValueError as exc:
        assert "Document content cannot be empty" in str(exc)
    else:
        raise AssertionError("Expected empty document to fail")

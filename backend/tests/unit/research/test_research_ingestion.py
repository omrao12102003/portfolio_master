import pytest

from app.research.ingestion import ResearchDocumentLoader


def test_load_text_document(tmp_path):
    path = tmp_path / "annual_report.txt"
    path.write_text(
        "Revenue increased during the reporting period.",
        encoding="utf-8",
    )

    document = ResearchDocumentLoader().load(
        path=path,
        document_id="annual-2025",
        title="Annual Report 2025",
        source="company.com/report",
        published_date="2025-12-31",
    )

    assert document.document_id == "annual-2025"
    assert document.title == "Annual Report 2025"
    assert document.source == "company.com/report"
    assert document.content.startswith("Revenue increased")
    assert document.published_date == "2025-12-31"


def test_load_markdown_document(tmp_path):
    path = tmp_path / "research.md"
    path.write_text("# Revenue\nRevenue increased.", encoding="utf-8")

    document = ResearchDocumentLoader().load(
        path,
        "research-1",
        "Research Note",
        "internal",
    )

    assert document.content.startswith("# Revenue")


def test_missing_document_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError, match="Document not found"):
        ResearchDocumentLoader().load(
            tmp_path / "missing.txt",
            "doc-1",
            "Missing",
            "source",
        )


def test_empty_document_is_rejected(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="content cannot be empty"):
        ResearchDocumentLoader().load(
            path,
            "doc-1",
            "Empty",
            "source",
        )


def test_invalid_pdf_is_rejected(tmp_path):
    path = tmp_path / "report.pdf"
    path.write_text("PDF placeholder", encoding="utf-8")

    with pytest.raises(Exception):
        ResearchDocumentLoader().load(
            path,
            "doc-1",
            "Report",
            "source",
        )


def test_missing_metadata_is_rejected(tmp_path):
    path = tmp_path / "report.txt"
    path.write_text("Revenue increased.", encoding="utf-8")

    with pytest.raises(ValueError, match="Document ID"):
        ResearchDocumentLoader().load(
            path,
            "",
            "Report",
            "source",
        )

from pypdf import PdfReader, PdfWriter

from app.research.ingestion import ResearchDocumentLoader


def create_pdf(path):
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)

    with path.open("wb") as handle:
        writer.write(handle)


def test_pdf_extension_is_supported(tmp_path, monkeypatch):
    path = tmp_path / "report.pdf"
    create_pdf(path)

    monkeypatch.setattr(
        ResearchDocumentLoader,
        "_read_pdf",
        staticmethod(lambda _: "Revenue increased by 12 percent."),
    )

    document = ResearchDocumentLoader().load(
        path,
        "annual-2025",
        "Annual Report 2025",
        "company.com/report",
        "2025-12-31",
    )

    assert document.document_id == "annual-2025"
    assert document.title == "Annual Report 2025"
    assert document.source == "company.com/report"
    assert "Revenue increased" in document.content


def test_pdf_reader_dependency_is_available(tmp_path):
    path = tmp_path / "report.pdf"
    create_pdf(path)

    reader = PdfReader(str(path))

    assert len(reader.pages) == 1

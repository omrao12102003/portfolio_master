from __future__ import annotations

from pathlib import Path

from app.research.retrieval import ResearchDocument


class ResearchDocumentLoader:
    supported_extensions = {".txt", ".md", ".html", ".htm", ".pdf"}

    def load(
        self,
        path: str | Path,
        document_id: str,
        title: str,
        source: str,
        published_date: str | None = None,
    ) -> ResearchDocument:
        file_path = Path(path)

        if file_path.suffix.lower() not in self.supported_extensions:
            raise ValueError(
                f"Unsupported document type: {file_path.suffix or 'unknown'}."
            )

        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            content = self._read_pdf(file_path)
        elif suffix in {".html", ".htm"}:
            content = self._read_html(file_path)
        else:
            content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            raise ValueError("Document content cannot be empty.")

        if not document_id.strip():
            raise ValueError("Document ID cannot be empty.")

        if not title.strip():
            raise ValueError("Document title cannot be empty.")

        if not source.strip():
            raise ValueError("Document source cannot be empty.")

        return ResearchDocument(
            document_id=document_id.strip(),
            title=title.strip(),
            source=source.strip(),
            content=content,
            published_date=published_date,
        )

    @staticmethod
    def _read_html(file_path: Path) -> str:
        try:
            from bs4 import BeautifulSoup
        except ImportError as exc:
            raise RuntimeError(
                "The beautifulsoup4 package is not installed."
            ) from exc

        html = file_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")

        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        block_tags = [
            "br",
            "p",
            "div",
            "li",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "table",
            "tr",
        ]

        for element in soup.find_all(block_tags):
            element.append("\n")

        return soup.get_text("\n", strip=True)


    @staticmethod
    def _read_pdf(file_path: Path) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("The pypdf package is not installed.") from exc

        reader = PdfReader(str(file_path))
        pages = [
            page.extract_text() or ""
            for page in reader.pages
        ]

        return "\n".join(pages).strip()

import json
from pathlib import Path

from app.research.ingestion import ResearchDocumentLoader

ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "data" / "research" / "metadata" / "corpus.json"


def test_real_sec_corpus_metadata_is_valid():
    metadata = json.loads(CORPUS.read_text())

    assert len(metadata["documents"]) == 3

    for document in metadata["documents"]:
        assert document["source"] == "SEC EDGAR"
        assert document["document_type"] == "10-K"
        assert document["published_date"]
        assert document["source_url"].startswith("https://www.sec.gov/")
        assert Path(ROOT / document["path"]).exists()


def test_real_sec_filings_extract_text():
    metadata = json.loads(CORPUS.read_text())
    loader = ResearchDocumentLoader()

    for item in metadata["documents"]:
        document = loader.load(
            ROOT / item["path"],
            item["document_id"],
            item["title"],
            item["source_url"],
            item["published_date"],
        )

        assert len(document.content) > 10000
        assert item["company"] in document.content or item["ticker"] in document.content
        assert document.published_date == item["published_date"]

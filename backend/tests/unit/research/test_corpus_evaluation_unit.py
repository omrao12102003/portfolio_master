from pathlib import Path

from app.research.chunking import FinancialDocumentChunker
from app.research.corpus_evaluation import build_real_corpus

ROOT = Path(__file__).resolve().parents[4]
METADATA = Path(__file__).resolve().parents[3] / "data/research/metadata/corpus.json"


def test_corpus_metadata_contains_primary_sources():
    chunks, metadata = build_real_corpus(
        METADATA,
        FinancialDocumentChunker(),
    )

    assert chunks
    assert metadata

    for item in metadata:
        assert item["company"]
        assert item["ticker"]
        assert item["document_type"]

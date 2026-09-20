from pathlib import Path

from app.research.chunking import FinancialDocumentChunker
from app.research.corpus_indexer import FinancialCorpusIndexer
from app.research.embeddings import HashEmbeddingProvider


def test_indexer_has_reproducible_configuration():
    indexer = FinancialCorpusIndexer(
        store=None,  # type: ignore[arg-type]
        provider=HashEmbeddingProvider(dimension=256),
        chunker=FinancialDocumentChunker(chunk_size=500, overlap=75),
    )

    assert indexer.chunker.chunk_size == 500
    assert indexer.chunker.overlap == 75
    assert indexer.provider.dimension == 256


def test_metadata_path_exists():
    path = (
        Path(__file__).resolve().parents[3]
        / "data/research/metadata/corpus.json"
    )

    assert path.exists()

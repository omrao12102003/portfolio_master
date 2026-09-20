from pathlib import Path

from app.research.chunking import FinancialDocumentChunker
from app.research.corpus_indexer import FinancialCorpusIndexer
from app.research.embeddings import HashEmbeddingProvider
from app.research.vector_store import ResearchVectorStore

METADATA = (
    Path(__file__).resolve().parents[2]
    / "data/research/metadata/corpus.json"
)


def test_financial_corpus_indexer_indexes_real_corpus():
    store = ResearchVectorStore(
        "postgresql://localhost/portfolio_master",
        256,
    )
    store.initialize()

    indexer = FinancialCorpusIndexer(
        store,
        HashEmbeddingProvider(dimension=256),
        FinancialDocumentChunker(chunk_size=500, overlap=75),
    )

    count = indexer.index(METADATA)

    try:
        assert count > 400
        assert store.count() == count
    finally:
        for document_id in (
            "aapl-10k-2025",
            "msft-10k-2025",
            "nvda-10k-2025",
        ):
            store.delete_document(document_id)

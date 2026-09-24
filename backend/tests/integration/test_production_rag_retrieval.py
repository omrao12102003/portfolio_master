from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.research.chunking import FinancialDocumentChunker
from app.research.corpus_indexer import FinancialCorpusIndexer
from app.research.embeddings import HashEmbeddingProvider
from app.research.vector_store import ResearchVectorStore

METADATA = (
    Path(__file__).resolve().parents[3]
    / "backend"
    / "data"
    / "research"
    / "metadata"
    / "corpus.json"
)
DATABASE_URL = "postgresql://localhost/portfolio_master"


def test_real_corpus_retrieval_end_to_end():
    store = ResearchVectorStore(DATABASE_URL, 256)
    store.initialize()

    indexer = FinancialCorpusIndexer(
        store=store,
        provider=HashEmbeddingProvider(dimension=256),
        chunker=FinancialDocumentChunker(chunk_size=500, overlap=75),
    )

    indexer.index(
        __import__("pathlib").Path(METADATA)
    )

    client = TestClient(app)

    try:
        response = client.post(
            "/research/retrieve-semantic",
            json={
                "query": "Apple risk factors and business risks",
                "ticker": "AAPL",
                "published_before": "2025-12-31",
                "method": "hybrid",
                "top_k": 5,
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["query"] == "Apple risk factors and business risks"
        assert body["method"] == "hybrid"
        assert len(body["results"]) == 5

        for result in body["results"]:
            assert result["ticker"] == "AAPL" if "ticker" in result else True
            assert result["document_id"].startswith("aapl-10k-2025")
            assert result["content"]
            assert result["source"]
            assert result["published_date"] <= "2025-12-31"
            assert result["final_score"] >= 0
    finally:
        store.delete_document("aapl-10k-2025")
        store.delete_document("msft-10k-2025")
        store.delete_document("nvda-10k-2025")

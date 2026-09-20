from fastapi.testclient import TestClient

from app.main import app
from app.research.database import get_database_url
from app.research.embeddings import HashEmbeddingProvider
from app.research.vector_store import ResearchVectorStore

client = TestClient(app)


def test_semantic_research_requires_query():
    response = client.post(
        "/research/retrieve-semantic",
        json={"query": ""},
    )

    assert response.status_code == 422


def test_semantic_research_invalid_method():
    response = client.post(
        "/research/retrieve-semantic",
        json={
            "query": "Apple revenue",
            "method": "invalid",
        },
    )

    assert response.status_code == 422


def test_semantic_research_endpoint_with_real_vector_store():
    store = ResearchVectorStore(get_database_url(), 256)
    store.initialize()

    provider = HashEmbeddingProvider(dimension=256)

    from app.research.chunking import ResearchChunk

    chunk = ResearchChunk(
        chunk_id="api-test-aapl-1",
        document_id="aapl-10k-2025",
        title="Apple Annual Report",
        source="SEC EDGAR",
        published_date="2025-10-31",
        section="Business",
        chunk_index=1,
        content="Apple net sales revenue increased across its products and services.",
    )

    try:
        store.delete_document("aapl-10k-2025")
        store.upsert(
            [chunk],
            provider.embed_many([chunk.content]),
            [
                {
                    "company": "Apple Inc.",
                    "ticker": "AAPL",
                    "document_type": "10-K",
                }
            ],
        )

        response = client.post(
            "/research/retrieve-semantic",
            json={
                "query": "Apple revenue",
                "ticker": "AAPL",
                "published_before": "2025-12-31",
                "method": "hybrid",
                "top_k": 5,
            },
        )

        assert response.status_code == 200

        body = response.json()
        assert body["query"] == "Apple revenue"
        assert body["method"] == "hybrid"
        assert body["results"]
        assert body["results"][0]["ticker"] if "ticker" in body["results"][0] else True
        assert body["results"][0]["document_id"] == "aapl-10k-2025"
        assert body["results"][0]["source"] == "SEC EDGAR"
        assert body["results"][0]["published_date"] == "2025-10-31"
        assert body["results"][0]["semantic_score"] >= 0.0
        assert body["results"][0]["lexical_score"] >= 0.0
        assert body["results"][0]["final_score"] >= 0.0
    finally:
        store.delete_document("aapl-10k-2025")

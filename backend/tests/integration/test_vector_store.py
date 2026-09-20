import os

import pytest

from app.research.chunking import ResearchChunk
from app.research.embeddings import HashEmbeddingProvider
from app.research.vector_store import ResearchVectorStore, index_chunks

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost/portfolio_master",
)


@pytest.fixture()
def vector_store():
    provider = HashEmbeddingProvider(dimension=256)
    store = ResearchVectorStore(DATABASE_URL, provider.dimension)
    store.initialize()

    with store._connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM research_chunks WHERE document_id = %s",
                ("test-vector-document",),
            )

    yield store, provider

    store.delete_document("test-vector-document")


def make_chunks() -> list[ResearchChunk]:
    return [
        ResearchChunk(
            chunk_id="test-vector-document-0",
            document_id="test-vector-document",
            title="Test Filing",
            source="Test Source",
            published_date="2025-01-01",
            section="Business",
            chunk_index=0,
            content="Revenue increased during the fiscal year.",
        ),
        ResearchChunk(
            chunk_id="test-vector-document-1",
            document_id="test-vector-document",
            title="Test Filing",
            source="Test Source",
            published_date="2025-01-01",
            section="Risk Factors",
            chunk_index=1,
            content="Market risk may affect future results.",
        ),
    ]


def test_vector_extension_and_table_initialize(vector_store):
    store, _ = vector_store

    assert store.count() == 0


def test_upsert_and_count(vector_store):
    store, provider = vector_store
    chunks = make_chunks()

    index_chunks(store, provider, chunks)

    assert store.count() == 2


def test_upsert_is_idempotent(vector_store):
    store, provider = vector_store
    chunks = make_chunks()

    index_chunks(store, provider, chunks)
    index_chunks(store, provider, chunks)

    assert store.count() == 2


def test_similarity_search(vector_store):
    store, provider = vector_store
    chunks = make_chunks()

    index_chunks(store, provider, chunks)

    query = provider.embed("Revenue increased during the year.")
    results = store.search(query, limit=2)

    assert len(results) == 2
    assert results[0].chunk_id == "test-vector-document-0"
    assert results[0].similarity > results[1].similarity


def test_historical_cutoff(vector_store):
    store, provider = vector_store
    chunks = make_chunks()

    chunks.append(
        ResearchChunk(
            chunk_id="test-vector-document-2",
            document_id="test-vector-document",
            title="Future Filing",
            source="Test Source",
            published_date="2026-01-01",
            section="Business",
            chunk_index=2,
            content="Revenue increased significantly.",
        )
    )

    index_chunks(store, provider, chunks)

    query = provider.embed("Revenue increased.")

    results = store.search(
        query,
        limit=10,
        published_before="2025-12-31",
    )

    assert all(result.published_date <= "2025-12-31" for result in results)
    assert all(result.chunk_id != "test-vector-document-2" for result in results)


def test_delete_document(vector_store):
    store, provider = vector_store
    chunks = make_chunks()

    index_chunks(store, provider, chunks)
    assert store.count() == 2

    store.delete_document("test-vector-document")

    assert store.count() == 0

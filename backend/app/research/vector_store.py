from __future__ import annotations

from dataclasses import dataclass

import psycopg
from pgvector.psycopg import register_vector

from app.research.chunking import ResearchChunk
from app.research.embeddings import EmbeddingProvider


@dataclass(frozen=True)
class VectorSearchResult:
    chunk_id: str
    document_id: str
    title: str
    source: str
    published_date: str | None
    section: str
    content: str
    similarity: float


class ResearchVectorStore:
    def __init__(self, database_url: str, dimension: int) -> None:
        if dimension < 2:
            raise ValueError("dimension must be at least 2.")

        self.database_url = database_url
        self.dimension = dimension

    def _connect(self) -> psycopg.Connection:
        connection = psycopg.connect(self.database_url)
        register_vector(connection)
        return connection

    def initialize(self) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
                cursor.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS research_chunks (
                        chunk_id TEXT PRIMARY KEY,
                        document_id TEXT NOT NULL,
                        title TEXT NOT NULL,
                        source TEXT NOT NULL,
                        published_date DATE,
                        section TEXT NOT NULL,
                        chunk_index INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        embedding VECTOR({self.dimension}) NOT NULL
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS research_chunks_document_id_idx
                    ON research_chunks (document_id)
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS research_chunks_published_date_idx
                    ON research_chunks (published_date)
                    """
                )

    def upsert(
        self,
        chunks: list[ResearchChunk],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length.")

        with self._connect() as connection:
            with connection.cursor() as cursor:
                for chunk, embedding in zip(chunks, embeddings, strict=True):
                    if len(embedding) != self.dimension:
                        raise ValueError("Embedding dimension does not match store.")

                    cursor.execute(
                        """
                        INSERT INTO research_chunks (
                            chunk_id,
                            document_id,
                            title,
                            source,
                            published_date,
                            section,
                            chunk_index,
                            content,
                            embedding
                        )
                        VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (chunk_id) DO UPDATE SET
                            document_id = EXCLUDED.document_id,
                            title = EXCLUDED.title,
                            source = EXCLUDED.source,
                            published_date = EXCLUDED.published_date,
                            section = EXCLUDED.section,
                            chunk_index = EXCLUDED.chunk_index,
                            content = EXCLUDED.content,
                            embedding = EXCLUDED.embedding
                        """,
                        (
                            chunk.chunk_id,
                            chunk.document_id,
                            chunk.title,
                            chunk.source,
                            chunk.published_date,
                            chunk.section,
                            chunk.chunk_index,
                            chunk.content,
                            embedding,
                        ),
                    )

    def count(self) -> int:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM research_chunks")
                row = cursor.fetchone()

        return int(row[0])

    def delete_document(self, document_id: str) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM research_chunks WHERE document_id = %s",
                    (document_id,),
                )

    def search(
        self,
        query_embedding: list[float],
        limit: int = 5,
        published_before: str | None = None,
    ) -> list[VectorSearchResult]:
        if len(query_embedding) != self.dimension:
            raise ValueError("Embedding dimension does not match store.")

        if limit < 1:
            raise ValueError("limit must be positive.")

        with self._connect() as connection:
            with connection.cursor() as cursor:
                if published_before is None:
                    cursor.execute(
                        """
                        SELECT
                            chunk_id,
                            document_id,
                            title,
                            source,
                            published_date,
                            section,
                            content,
                            1 - (embedding <=> %s::vector) AS similarity
                        FROM research_chunks
                        ORDER BY embedding <=> %s::vector, chunk_id
                        LIMIT %s
                        """,
                        (query_embedding, query_embedding, limit),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT
                            chunk_id,
                            document_id,
                            title,
                            source,
                            published_date,
                            section,
                            content,
                            1 - (embedding <=> %s::vector) AS similarity
                        FROM research_chunks
                        WHERE published_date <= %s
                        ORDER BY embedding <=> %s::vector, chunk_id
                        LIMIT %s
                        """,
                        (
                            query_embedding,
                            published_before,
                            query_embedding,
                            limit,
                        ),
                    )

                rows = cursor.fetchall()

        return [
            VectorSearchResult(
                chunk_id=row[0],
                document_id=row[1],
                title=row[2],
                source=row[3],
                published_date=row[4].isoformat() if row[4] else None,
                section=row[5],
                content=row[6],
                similarity=float(row[7]),
            )
            for row in rows
        ]


def index_chunks(
    store: ResearchVectorStore,
    provider: EmbeddingProvider,
    chunks: list[ResearchChunk],
) -> None:
    embeddings = provider.embed_many([chunk.content for chunk in chunks])
    store.upsert(chunks, embeddings)

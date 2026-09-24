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
                        embedding VECTOR({self.dimension}) NOT NULL,
                        company TEXT,
                        ticker TEXT,
                        document_type TEXT
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
        metadata: list[dict[str, str | None]] | None = None,
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length.")

        if metadata is not None and len(metadata) != len(chunks):
            raise ValueError("metadata must have the same length as chunks.")

        rows = []
        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings, strict=True)
        ):
            if len(embedding) != self.dimension:
                raise ValueError("Embedding dimension does not match store.")

            rows.append(
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
                    (
                        metadata[index].get("company")
                        if metadata is not None
                        else None
                    ),
                    (
                        metadata[index].get("ticker")
                        if metadata is not None
                        else None
                    ),
                    (
                        metadata[index].get("document_type")
                        if metadata is not None
                        else None
                    ),
                )
            )

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(
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
                        embedding,
                        company,
                        ticker,
                        document_type
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s
                    )
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        document_id = EXCLUDED.document_id,
                        title = EXCLUDED.title,
                        source = EXCLUDED.source,
                        published_date = EXCLUDED.published_date,
                        section = EXCLUDED.section,
                        chunk_index = EXCLUDED.chunk_index,
                        content = EXCLUDED.content,
                        embedding = EXCLUDED.embedding,
                        company = EXCLUDED.company,
                        ticker = EXCLUDED.ticker,
                        document_type = EXCLUDED.document_type
                    """,
                    rows,
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
        company: str | None = None,
        ticker: str | None = None,
        document_type: str | None = None,
        section: str | None = None,
    ) -> list[VectorSearchResult]:
        if len(query_embedding) != self.dimension:
            raise ValueError("Embedding dimension does not match store.")

        if limit < 1:
            raise ValueError("limit must be positive.")

        filters = []
        params: list[object] = [query_embedding]

        if published_before is not None:
            filters.append("published_date < %s")
            params.append(published_before)

        if company is not None:
            filters.append("company = %s")
            params.append(company)

        if ticker is not None:
            filters.append("ticker = %s")
            params.append(ticker)

        if document_type is not None:
            filters.append("document_type = %s")
            params.append(document_type)

        if section is not None:
            filters.append("section = %s")
            params.append(section)

        where_clause = ""
        if filters:
            where_clause = "WHERE " + " AND ".join(filters)

        params.extend([query_embedding, limit])

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
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
                    {where_clause}
                    ORDER BY embedding <=> %s::vector, chunk_id
                    LIMIT %s
                    """,
                    params,
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
    metadata: list[dict[str, str | None]] | None = None,
) -> None:
    embeddings = provider.embed_many([chunk.content for chunk in chunks])
    store.upsert(chunks, embeddings, metadata)

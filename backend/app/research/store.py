from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import psycopg

from app.research.retrieval import ResearchDocument


@dataclass(frozen=True)
class StoredResearchDocument:
    document_id: str
    title: str
    source: str
    content: str
    published_date: str | None
    created_at: datetime


class ResearchDocumentStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def initialize(self) -> None:
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS research_documents (
                    document_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content TEXT NOT NULL,
                    published_date DATE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            connection.commit()

    def upsert(self, document: ResearchDocument) -> None:
        with psycopg.connect(self.database_url) as connection:
            connection.execute(
                """
                INSERT INTO research_documents (
                    document_id,
                    title,
                    source,
                    content,
                    published_date
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (document_id)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    source = EXCLUDED.source,
                    content = EXCLUDED.content,
                    published_date = EXCLUDED.published_date
                """,
                (
                    document.document_id,
                    document.title,
                    document.source,
                    document.content,
                    document.published_date,
                ),
            )
            connection.commit()

    def get(self, document_id: str) -> ResearchDocument | None:
        with psycopg.connect(self.database_url) as connection:
            row = connection.execute(
                """
                SELECT document_id, title, source, content, published_date
                FROM research_documents
                WHERE document_id = %s
                """,
                (document_id,),
            ).fetchone()

        if row is None:
            return None

        return ResearchDocument(
            document_id=row[0],
            title=row[1],
            source=row[2],
            content=row[3],
            published_date=row[4].isoformat() if row[4] else None,
        )

    def list_documents(self) -> list[ResearchDocument]:
        with psycopg.connect(self.database_url) as connection:
            rows = connection.execute(
                """
                SELECT document_id, title, source, content, published_date
                FROM research_documents
                ORDER BY created_at DESC, document_id
                """
            ).fetchall()

        return [
            ResearchDocument(
                document_id=row[0],
                title=row[1],
                source=row[2],
                content=row[3],
                published_date=row[4].isoformat() if row[4] else None,
            )
            for row in rows
        ]

    def delete(self, document_id: str) -> bool:
        with psycopg.connect(self.database_url) as connection:
            cursor = connection.execute(
                """
                DELETE FROM research_documents
                WHERE document_id = %s
                """,
                (document_id,),
            )
            connection.commit()

        return cursor.rowcount > 0

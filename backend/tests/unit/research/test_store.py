from __future__ import annotations

from datetime import date, datetime

from app.research.retrieval import ResearchDocument
from app.research.store import ResearchDocumentStore


class FakeCursor:
    def __init__(self, rows=None, rowcount=0):
        self._rows = rows or []
        self.rowcount = rowcount

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return self._rows


class FakeConnection:
    def __init__(self, rows=None, rowcount=0):
        self.cursor = FakeCursor(rows, rowcount)
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))
        return self.cursor

    def commit(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def test_initialize_creates_table(monkeypatch):
    connection = FakeConnection()
    monkeypatch.setattr(
        "app.research.store.psycopg.connect",
        lambda _: connection,
    )

    ResearchDocumentStore("postgresql://test").initialize()

    assert "CREATE TABLE IF NOT EXISTS research_documents" in connection.executed[0][0]


def test_upsert_writes_document(monkeypatch):
    connection = FakeConnection()
    monkeypatch.setattr(
        "app.research.store.psycopg.connect",
        lambda _: connection,
    )

    document = ResearchDocument(
        document_id="doc-1",
        title="Annual Report",
        source="example.com/report",
        content="Revenue increased.",
        published_date="2025-12-31",
    )

    ResearchDocumentStore("postgresql://test").upsert(document)

    assert "INSERT INTO research_documents" in connection.executed[0][0]
    assert connection.executed[0][1][0] == "doc-1"


def test_get_returns_document(monkeypatch):
    connection = FakeConnection(
        rows=[
            (
                "doc-1",
                "Annual Report",
                "example.com/report",
                "Revenue increased.",
                date(2025, 12, 31),
            )
        ]
    )
    monkeypatch.setattr(
        "app.research.store.psycopg.connect",
        lambda _: connection,
    )

    document = ResearchDocumentStore("postgresql://test").get("doc-1")

    assert document is not None
    assert document.document_id == "doc-1"
    assert document.published_date == "2025-12-31"


def test_get_returns_none_for_missing_document(monkeypatch):
    connection = FakeConnection()
    monkeypatch.setattr(
        "app.research.store.psycopg.connect",
        lambda _: connection,
    )

    assert ResearchDocumentStore("postgresql://test").get("missing") is None


def test_list_documents(monkeypatch):
    connection = FakeConnection(
        rows=[
            (
                "doc-1",
                "Annual Report",
                "example.com/report",
                "Revenue increased.",
                date(2025, 12, 31),
            )
        ]
    )
    monkeypatch.setattr(
        "app.research.store.psycopg.connect",
        lambda _: connection,
    )

    documents = ResearchDocumentStore("postgresql://test").list_documents()

    assert len(documents) == 1
    assert documents[0].title == "Annual Report"


def test_delete_returns_true_when_document_deleted(monkeypatch):
    connection = FakeConnection(rowcount=1)
    monkeypatch.setattr(
        "app.research.store.psycopg.connect",
        lambda _: connection,
    )

    assert ResearchDocumentStore("postgresql://test").delete("doc-1") is True


def test_delete_returns_false_when_document_missing(monkeypatch):
    connection = FakeConnection(rowcount=0)
    monkeypatch.setattr(
        "app.research.store.psycopg.connect",
        lambda _: connection,
    )

    assert ResearchDocumentStore("postgresql://test").delete("missing") is False


def test_stored_document_shape():
    stored = (
        "doc-1",
        "Annual Report",
        "example.com/report",
        "Revenue increased.",
        "2025-12-31",
        datetime.now(),
    )

    assert stored[0] == "doc-1"

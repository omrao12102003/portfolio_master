from app.research.database import get_database_url


def test_database_url_uses_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example/test")
    assert get_database_url() == "postgresql://example/test"


def test_database_url_has_default(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    assert get_database_url() == "postgresql://localhost/portfolio_master"


def test_database_url_rejects_empty_value(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "   ")

    try:
        get_database_url()
    except RuntimeError as exc:
        assert str(exc) == "DATABASE_URL is not configured."
    else:
        raise AssertionError("Expected RuntimeError")

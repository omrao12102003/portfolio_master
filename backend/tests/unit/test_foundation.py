import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings, settings
from app.core.paths import BACKEND_DIR, REPO_ROOT


def test_default_settings_use_portfolio_master_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ("APP_NAME", "APP_ENVIRONMENT", "API_PORT", "DATABASE_URL"):
        monkeypatch.delenv(key, raising=False)
    loaded = Settings(_env_file=None)
    assert loaded.app_name == "Portfolio Master"
    assert loaded.app_environment == "development"
    assert "portfolio_master" in loaded.database_url
    assert loaded.api_port == 8000


def test_settings_read_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENVIRONMENT", "test")
    monkeypatch.setenv("API_PORT", "9000")
    loaded = Settings(_env_file=None)
    assert loaded.app_environment == "test"
    assert loaded.api_port == 9000


def test_invalid_api_port_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_PORT", "not-a-port")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_repository_paths_resolve_from_this_package() -> None:
    assert (REPO_ROOT / "README.md").is_file()
    assert (BACKEND_DIR / "pyproject.toml").is_file()


def test_root_payload(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == settings.app_name
    assert payload["status"] == "running"
    assert payload["version"] == "0.1.0"
    assert payload["environment"] == settings.app_environment


def test_openapi_exposes_health_routes(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/health" in paths
    assert "/api/health" in paths

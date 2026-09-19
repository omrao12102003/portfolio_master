from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.paths import BACKEND_DIR, REPO_ROOT


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables and optional .env files."""

    app_name: str = "Portfolio Master"
    app_environment: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = Field(
        default="postgresql+psycopg://portfolio:portfolio@localhost:5432/portfolio_master",
        description="SQLAlchemy-style database URL. Unused by application logic in Stage 1A.",
    )

    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()

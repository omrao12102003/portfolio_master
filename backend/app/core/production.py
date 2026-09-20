import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProductionConfig:
    environment: str
    debug: bool
    database_url: str
    cors_origins: tuple[str, ...]
    max_report_metrics: int
    max_report_evidence: int
    max_retrieval_k: int


def get_production_config() -> ProductionConfig:
    environment = os.getenv("APP_ENV", "development").strip().lower()
    debug = os.getenv("APP_DEBUG", "false").strip().lower() in {
        "1",
        "true",
        "yes",
    }

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://localhost/portfolio_master",
    ).strip()

    origins_raw = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173",
    )

    cors_origins = tuple(
        origin.strip()
        for origin in origins_raw.split(",")
        if origin.strip()
    )

    if not database_url:
        raise ValueError("DATABASE_URL must not be empty")

    if not cors_origins:
        raise ValueError("CORS_ORIGINS must contain at least one origin")

    return ProductionConfig(
        environment=environment,
        debug=debug,
        database_url=database_url,
        cors_origins=cors_origins,
        max_report_metrics=50,
        max_report_evidence=20,
        max_retrieval_k=20,
    )


def validate_production_config(config: ProductionConfig) -> None:
    if config.environment == "production" and config.debug:
        raise ValueError("APP_DEBUG must be false in production")

    if config.max_report_metrics <= 0:
        raise ValueError("max_report_metrics must be positive")

    if config.max_report_evidence <= 0:
        raise ValueError("max_report_evidence must be positive")

    if not 1 <= config.max_retrieval_k <= 100:
        raise ValueError("max_retrieval_k must be between 1 and 100")

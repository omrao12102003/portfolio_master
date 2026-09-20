import pytest

from app.core.production import (
    ProductionConfig,
    get_production_config,
    validate_production_config,
)


def test_default_production_config():
    config = get_production_config()

    assert config.environment == "development"
    assert config.database_url
    assert config.cors_origins
    assert config.max_retrieval_k == 20


def test_production_debug_is_rejected():
    config = ProductionConfig(
        environment="production",
        debug=True,
        database_url="postgresql://localhost/portfolio_master",
        cors_origins=("http://localhost:5173",),
        max_report_metrics=50,
        max_report_evidence=20,
        max_retrieval_k=20,
    )

    with pytest.raises(ValueError, match="APP_DEBUG"):
        validate_production_config(config)


def test_production_config_accepts_safe_values():
    config = ProductionConfig(
        environment="production",
        debug=False,
        database_url="postgresql://localhost/portfolio_master",
        cors_origins=("https://example.com",),
        max_report_metrics=50,
        max_report_evidence=20,
        max_retrieval_k=20,
    )

    validate_production_config(config)

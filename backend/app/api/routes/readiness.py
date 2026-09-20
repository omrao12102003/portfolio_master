from fastapi import APIRouter

from app.core.production import get_production_config

router = APIRouter(
    prefix="/api",
    tags=["system"],
)


@router.get("/readiness")
def readiness() -> dict:
    config = get_production_config()

    return {
        "status": "ready",
        "environment": config.environment,
        "database_configured": bool(config.database_url),
        "cors_configured": bool(config.cors_origins),
    }

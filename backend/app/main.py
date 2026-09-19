from fastapi import FastAPI

from app.api.router import api_router
from app.api.routes.health import health
from app.core.config import settings
from app.schemas.system import HealthResponse, RootResponse

APP_VERSION = "0.1.0"

app = FastAPI(
    title=settings.app_name,
    version=APP_VERSION,
    description=(
        "Quantitative investment research and portfolio-management platform. "
        "Stage 1 establishes the software foundation; quantitative engines are not implemented yet."
    ),
)

app.include_router(api_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def root_health() -> HealthResponse:
    """Process-level liveness probe. The same payload is also available at /api/health."""
    return health()


@app.get("/", response_model=RootResponse, tags=["system"])
def root() -> RootResponse:
    return RootResponse(
        name=settings.app_name,
        version=APP_VERSION,
        status="running",
        environment=settings.app_environment,
    )

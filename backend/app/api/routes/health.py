from fastapi import APIRouter

from app.schemas.system import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Liveness probe used by local development and Docker health checks."""
    return HealthResponse(status="healthy")

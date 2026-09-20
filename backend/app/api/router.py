from fastapi import APIRouter

from app.api.routes.advanced_risk import router as advanced_risk_router
from app.api.routes.derivatives import router as derivatives_router
from app.api.routes.factor_time_series import router as factor_time_series_router
from app.api.routes.health import router as health_router
from app.api.routes.quant import router as quant_router
from app.api.routes.research import router as research_router
from app.api.routes.rl import router as rl_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/api")
api_router.include_router(quant_router)
api_router.include_router(advanced_risk_router)
api_router.include_router(factor_time_series_router)
api_router.include_router(research_router)
api_router.include_router(rl_router)
api_router.include_router(derivatives_router)

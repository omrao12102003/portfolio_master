from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.analytics.factors.capm import capm_analysis
from app.analytics.factors.fama_french import fama_french_3_factor
from app.analytics.garch import garch_forecast
from app.analytics.time_series import arima_forecast

router = APIRouter(prefix="/quant", tags=["factor-time-series"])


class CAPMRequest(BaseModel):
    asset_returns: list[float] = Field(min_length=2)
    market_returns: list[float] = Field(min_length=2)
    risk_free_returns: list[float] | None = None


class FamaFrenchRequest(BaseModel):
    asset_returns: list[float] = Field(min_length=4)
    market_excess_returns: list[float] = Field(min_length=4)
    smb_returns: list[float] = Field(min_length=4)
    hml_returns: list[float] = Field(min_length=4)
    annualization_factor: float | None = Field(default=None, gt=0)


class ARIMARequest(BaseModel):
    values: list[float] = Field(min_length=10)
    p: int = Field(default=1, ge=0)
    d: int = Field(default=1, ge=0)
    q: int = Field(default=0, ge=0)
    steps: int = Field(default=5, ge=1)
    alpha: float = Field(default=0.05, gt=0, lt=1)


class GARCHRequest(BaseModel):
    returns: list[float] = Field(min_length=30)
    steps: int = Field(default=5, ge=1)
    annualization_factor: float = Field(default=252.0, gt=0)


@router.post("/capm")
def calculate_capm(request: CAPMRequest) -> dict[str, object]:
    try:
        result = capm_analysis(
            np.asarray(request.asset_returns, dtype=float),
            np.asarray(request.market_returns, dtype=float),
            (
                np.asarray(request.risk_free_returns, dtype=float)
                if request.risk_free_returns is not None
                else None
            ),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "alpha": result.alpha,
        "beta": result.beta,
        "r_squared": result.r_squared,
        "observations": result.observations,
    }


@router.post("/fama-french")
def calculate_fama_french(
    request: FamaFrenchRequest,
) -> dict[str, object]:
    try:
        result = fama_french_3_factor(
            np.asarray(request.asset_returns, dtype=float),
            np.asarray(request.market_excess_returns, dtype=float),
            np.asarray(request.smb_returns, dtype=float),
            np.asarray(request.hml_returns, dtype=float),
            annualization_factor=request.annualization_factor,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "alpha": result.alpha,
        "market_beta": result.market_beta,
        "smb_beta": result.smb_beta,
        "hml_beta": result.hml_beta,
        "r_squared": result.r_squared,
        "residual_volatility": result.residual_volatility,
        "observations": result.observations,
    }


@router.post("/arima")
def calculate_arima(request: ARIMARequest) -> dict[str, object]:
    try:
        result = arima_forecast(
            np.asarray(request.values, dtype=float),
            (request.p, request.d, request.q),
            request.steps,
            alpha=request.alpha,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "order": list(result.order),
        "forecast": result.forecast.tolist(),
        "lower": result.lower.tolist(),
        "upper": result.upper.tolist(),
    }


@router.post("/garch")
def calculate_garch(request: GARCHRequest) -> dict[str, object]:
    try:
        result = garch_forecast(
            np.asarray(request.returns, dtype=float),
            request.steps,
            annualization_factor=request.annualization_factor,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "conditional_volatility": result.conditional_volatility.tolist(),
        "forecast_variance": result.forecast_variance.tolist(),
        "forecast_volatility": result.forecast_volatility.tolist(),
        "annualized_forecast_volatility": (
            result.annualized_forecast_volatility.tolist()
        ),
    }

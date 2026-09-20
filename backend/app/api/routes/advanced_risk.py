from __future__ import annotations

import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.risk.advanced import (
    factor_risk,
    monte_carlo_var,
    risk_attribution,
    stress_test,
)

router = APIRouter(prefix="/quant", tags=["advanced-risk"])


class MonteCarloVaRRequest(BaseModel):
    returns: list[float] = Field(min_length=30)
    confidence: float = Field(default=0.95, gt=0, lt=1)
    simulations: int = Field(default=10_000, ge=100)
    seed: int | None = 42


class StressTestRequest(BaseModel):
    weights: list[float] = Field(min_length=1)
    scenario_returns: list[float] = Field(min_length=1)
    scenario_name: str = "custom"


class FactorRiskRequest(BaseModel):
    factor_exposures: list[float] = Field(min_length=1)
    factor_covariance: list[list[float]]
    residual_variance: float = Field(ge=0)


class RiskAttributionRequest(BaseModel):
    weights: list[float] = Field(min_length=1)
    covariance: list[list[float]]


@router.post("/risk/monte-carlo-var")
def calculate_monte_carlo_var(
    request: MonteCarloVaRRequest,
) -> dict[str, object]:
    try:
        result = monte_carlo_var(
            np.asarray(request.returns, dtype=float),
            confidence=request.confidence,
            simulations=request.simulations,
            seed=request.seed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "var": result.var,
        "expected_shortfall": result.expected_shortfall,
        "confidence": result.confidence,
        "simulations": result.simulations,
    }


@router.post("/risk/stress-test")
def calculate_stress_test(
    request: StressTestRequest,
) -> dict[str, object]:
    try:
        result = stress_test(
            np.asarray(request.weights, dtype=float),
            np.asarray(request.scenario_returns, dtype=float),
            request.scenario_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "portfolio_return": result.portfolio_return,
        "asset_returns": result.asset_returns.tolist(),
        "scenario_name": result.scenario_name,
    }


@router.post("/risk/factor")
def calculate_factor_risk(
    request: FactorRiskRequest,
) -> dict[str, object]:
    try:
        result = factor_risk(
            np.asarray(request.factor_exposures, dtype=float),
            np.asarray(request.factor_covariance, dtype=float),
            request.residual_variance,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "factor_contributions": result.factor_contributions.tolist(),
        "systematic_variance": result.systematic_variance,
        "idiosyncratic_variance": result.idiosyncratic_variance,
        "total_variance": result.total_variance,
        "systematic_percentage": result.systematic_percentage,
        "idiosyncratic_percentage": result.idiosyncratic_percentage,
    }


@router.post("/risk/attribution")
def calculate_risk_attribution(
    request: RiskAttributionRequest,
) -> dict[str, object]:
    try:
        result = risk_attribution(
            np.asarray(request.weights, dtype=float),
            np.asarray(request.covariance, dtype=float),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "marginal_contributions": result.marginal_contributions.tolist(),
        "component_contributions": result.component_contributions.tolist(),
        "percentage_contributions": result.percentage_contributions.tolist(),
        "total_risk": result.total_risk,
    }

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.fixed_income.bonds import (
    bond_price,
    bond_yield_to_maturity,
    convexity,
    duration,
    modified_duration,
    rate_sensitivity,
    yield_curve,
)

router = APIRouter(prefix="/quant/fixed-income", tags=["fixed-income"])


class BondRequest(BaseModel):
    face_value: float
    coupon_rate: float
    yield_rate: float
    maturity: float
    frequency: int = Field(default=2, ge=1)


class YTMRequest(BaseModel):
    price: float
    face_value: float
    coupon_rate: float
    maturity: float
    frequency: int = Field(default=2, ge=1)


class YieldCurveRequest(BaseModel):
    maturities: list[float]
    spot_rates: list[float]


class RateSensitivityRequest(BaseModel):
    price: float
    modified_duration: float
    convexity: float
    yield_change: float


@router.post("/price")
def calculate_bond_price(request: BondRequest) -> dict[str, float]:
    return {
        "price": bond_price(**request.model_dump()),
    }


@router.post("/ytm")
def calculate_ytm(request: YTMRequest) -> dict[str, float]:
    return {
        "yield_to_maturity": bond_yield_to_maturity(**request.model_dump()),
    }


@router.post("/analytics")
def calculate_bond_analytics(request: BondRequest) -> dict[str, float]:
    values = request.model_dump()

    price = bond_price(**values)
    ytm = values["yield_rate"]
    macaulay = duration(**values)
    modified = modified_duration(**values)
    convexity_value = convexity(**values)

    return {
        "price": price,
        "yield_to_maturity": ytm,
        "macaulay_duration": macaulay,
        "modified_duration": modified,
        "convexity": convexity_value,
    }


@router.post("/yield-curve")
def calculate_yield_curve(
    request: YieldCurveRequest,
) -> dict[str, list[float]]:
    result = yield_curve(
        maturities=request.maturities,
        spot_rates=request.spot_rates,
    )

    return {
        "maturities": result.maturities.tolist(),
        "spot_rates": result.spot_rates.tolist(),
        "discount_factors": result.discount_factors.tolist(),
    }


@router.post("/rate-sensitivity")
def calculate_rate_sensitivity(
    request: RateSensitivityRequest,
) -> dict[str, float]:
    return {
        "estimated_price": rate_sensitivity(
            price=request.price,
            modified_duration_value=request.modified_duration,
            convexity_value=request.convexity,
            yield_change=request.yield_change,
        )
    }

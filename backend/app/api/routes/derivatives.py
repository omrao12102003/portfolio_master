from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.derivatives.pricing import (
    binomial_option,
    black_scholes,
    forward_price,
    futures_price,
    implied_volatility,
    put_call_parity,
)

router = APIRouter(prefix="/quant/derivatives", tags=["derivatives"])


class ForwardRequest(BaseModel):
    spot: float
    rate: float
    time_to_maturity: float
    dividend_yield: float = 0.0


class FuturesRequest(BaseModel):
    spot: float
    rate: float
    time_to_maturity: float
    convenience_yield: float = 0.0
    storage_cost: float = 0.0


class PutCallParityRequest(BaseModel):
    call_price: float
    spot: float
    strike: float
    rate: float
    time_to_maturity: float
    dividend_yield: float = 0.0


class BlackScholesRequest(BaseModel):
    spot: float
    strike: float
    rate: float
    volatility: float
    time_to_maturity: float
    option_type: str = Field(default="call")
    dividend_yield: float = 0.0


class BinomialRequest(BlackScholesRequest):
    steps: int = Field(default=100, ge=1)
    american: bool = False


class ImpliedVolatilityRequest(BaseModel):
    market_price: float
    spot: float
    strike: float
    rate: float
    time_to_maturity: float
    option_type: str = Field(default="call")
    dividend_yield: float = 0.0


@router.post("/forward")
def calculate_forward(request: ForwardRequest) -> dict[str, float]:
    result = forward_price(**request.model_dump())
    return {"forward_price": result.forward_price}


@router.post("/futures")
def calculate_futures(request: FuturesRequest) -> dict[str, float]:
    result = futures_price(**request.model_dump())
    return {"futures_price": result.futures_price}


@router.post("/put-call-parity")
def calculate_put_call_parity(
    request: PutCallParityRequest,
) -> dict[str, float]:
    return {
        "put_price": put_call_parity(**request.model_dump()),
    }


@router.post("/black-scholes")
def calculate_black_scholes(request: BlackScholesRequest) -> dict:
    result = black_scholes(**request.model_dump())
    return {
        "price": result.price,
        "greeks": {
            "delta": result.greeks.delta,
            "gamma": result.greeks.gamma,
            "theta": result.greeks.theta,
            "vega": result.greeks.vega,
            "rho": result.greeks.rho,
        },
    }


@router.post("/binomial")
def calculate_binomial(request: BinomialRequest) -> dict[str, float | int]:
    result = binomial_option(**request.model_dump())
    return {
        "price": result.price,
        "steps": result.steps,
    }


@router.post("/implied-volatility")
def calculate_implied_volatility(
    request: ImpliedVolatilityRequest,
) -> dict[str, float]:
    volatility = implied_volatility(**request.model_dump())
    return {"implied_volatility": volatility}

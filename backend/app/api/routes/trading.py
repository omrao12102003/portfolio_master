from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.trading.research import (
    ExecutionConfig,
    evaluate_strategy,
    mean_reversion_signal,
    momentum_signal,
    position_size,
    walk_forward_splits,
)

router = APIRouter(prefix="/quant/trading", tags=["trading"])


class MomentumRequest(BaseModel):
    prices: list[float]
    lookback: int = Field(default=20, ge=1)


class MeanReversionRequest(BaseModel):
    prices: list[float]
    lookback: int = Field(default=20, ge=2)
    entry_zscore: float = Field(default=1.0, gt=0)


class PositionSizingRequest(BaseModel):
    signal: list[float]
    volatility: list[float]
    target_volatility: float = Field(default=0.10, gt=0)
    max_position: float = Field(default=1.0, gt=0)


class StrategyEvaluationRequest(BaseModel):
    target_positions: list[float]
    asset_returns: list[float]
    transaction_cost_bps: float = Field(default=5.0, ge=0)
    slippage_bps: float = Field(default=2.0, ge=0)
    market_impact_bps: float = Field(default=0.0, ge=0)
    impact_exponent: float = Field(default=0.5, gt=0)
    periods_per_year: int = Field(default=252, ge=1)
    risk_free_rate: float = 0.0


class WalkForwardRequest(BaseModel):
    observations: int = Field(gt=1)
    train_size: int = Field(gt=0)
    test_size: int = Field(gt=0)
    step_size: int | None = Field(default=None, gt=0)


@router.post("/signals/momentum")
def calculate_momentum(request: MomentumRequest) -> dict[str, list[float]]:
    signal = momentum_signal(
        prices=request.prices,
        lookback=request.lookback,
    )

    return {"signal": signal.tolist()}


@router.post("/signals/mean-reversion")
def calculate_mean_reversion(
    request: MeanReversionRequest,
) -> dict[str, list[float]]:
    signal = mean_reversion_signal(
        prices=request.prices,
        lookback=request.lookback,
        entry_zscore=request.entry_zscore,
    )

    return {"signal": signal.tolist()}


@router.post("/position-sizing")
def calculate_position_sizing(
    request: PositionSizingRequest,
) -> dict[str, list[float]]:
    positions = position_size(
        signal=request.signal,
        volatility=request.volatility,
        target_volatility=request.target_volatility,
        max_position=request.max_position,
    )

    return {"positions": positions.tolist()}


@router.post("/evaluate")
def evaluate(request: StrategyEvaluationRequest) -> dict:
    result = evaluate_strategy(
        target_positions=request.target_positions,
        asset_returns=request.asset_returns,
        execution=ExecutionConfig(
            transaction_cost_bps=request.transaction_cost_bps,
            slippage_bps=request.slippage_bps,
            market_impact_bps=request.market_impact_bps,
            impact_exponent=request.impact_exponent,
        ),
        periods_per_year=request.periods_per_year,
        risk_free_rate=request.risk_free_rate,
    )

    return {
        "cumulative_return": result.cumulative_return,
        "annualized_return": result.annualized_return,
        "annualized_volatility": result.annualized_volatility,
        "sharpe_ratio": result.sharpe_ratio,
        "maximum_drawdown": result.maximum_drawdown,
        "total_turnover": result.total_turnover,
        "total_cost": result.total_cost,
        "observations": result.observations,
        "strategy_returns": result.strategy_returns.tolist(),
    }


@router.post("/walk-forward")
def calculate_walk_forward(
    request: WalkForwardRequest,
) -> dict[str, list[dict[str, int]]]:
    splits = walk_forward_splits(
        observations=request.observations,
        train_size=request.train_size,
        test_size=request.test_size,
        step_size=request.step_size,
    )

    return {
        "splits": [
            {
                "train_start": split.train_start,
                "train_end": split.train_end,
                "test_start": split.test_start,
                "test_end": split.test_end,
            }
            for split in splits
        ]
    }

from __future__ import annotations

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.rl.agent import DiscretePortfolioAgent
from app.rl.comparison import evaluate_strategies
from app.rl.pipeline import run_rl_pipeline

router = APIRouter(prefix="/rl", tags=["reinforcement-learning"])


class RLRequest(BaseModel):
    returns: list[list[float]] = Field(min_length=6)
    assets: list[str] = Field(min_length=2)
    actions: list[list[float]] = Field(min_length=2)
    initial_capital: float = Field(default=100_000.0, gt=0)
    transaction_cost_bps: float = Field(default=5.0, ge=0)
    risk_free_rate: float = 0.0


class RLEvaluationResponse(BaseModel):
    final_value: float
    cumulative_return: float
    average_reward: float
    total_turnover: float


class RLStrategyResponse(BaseModel):
    name: str
    final_value: float
    cumulative_return: float
    average_reward: float
    total_turnover: float


class RLResponse(BaseModel):
    selected_action: int
    training_rewards: dict[str, float]
    validation: RLEvaluationResponse
    test: RLEvaluationResponse
    q_learning_validation: RLEvaluationResponse
    q_learning_test: RLEvaluationResponse
    strategies: list[RLStrategyResponse]


@router.post("/evaluate", response_model=RLResponse)
def evaluate_rl(request: RLRequest) -> RLResponse:
    if not request.returns:
        raise HTTPException(
            status_code=400,
            detail="Returns cannot be empty.",
        )

    if any(len(row) != len(request.assets) for row in request.returns):
        raise HTTPException(
            status_code=400,
            detail="Return columns must match assets.",
        )

    returns = pd.DataFrame(request.returns, columns=request.assets)

    actions = [
        np.asarray(action, dtype=float)
        for action in request.actions
    ]

    for action in actions:
        if len(action) != len(request.assets):
            raise HTTPException(
                status_code=400,
                detail="Action weights must match assets.",
            )

    pipeline = run_rl_pipeline(
        returns,
        actions,
        initial_capital=request.initial_capital,
        transaction_cost_bps=request.transaction_cost_bps,
    )

    from app.rl.split import chronological_split

    split = chronological_split(returns)

    agent = DiscretePortfolioAgent(actions)

    strategies = evaluate_strategies(
        split.train,
        split.test,
        agent,
        pipeline.selected_action,
        initial_capital=request.initial_capital,
        transaction_cost_bps=request.transaction_cost_bps,
        risk_free_rate=request.risk_free_rate,
    )

    def evaluation_response(evaluation) -> RLEvaluationResponse:
        return RLEvaluationResponse(
            final_value=evaluation.final_value,
            cumulative_return=evaluation.cumulative_return,
            average_reward=evaluation.average_reward,
            total_turnover=evaluation.total_turnover,
        )

    return RLResponse(
        selected_action=pipeline.selected_action,
        training_rewards={
            str(index): value
            for index, value in pipeline.training_rewards.items()
        },
        validation=evaluation_response(pipeline.validation),
        test=evaluation_response(pipeline.test),
        q_learning_validation=evaluation_response(
            pipeline.q_learning_validation
        ),
        q_learning_test=evaluation_response(
            pipeline.q_learning_test
        ),
        strategies=[
            RLStrategyResponse(
                name=result.name,
                final_value=result.evaluation.final_value,
                cumulative_return=result.evaluation.cumulative_return,
                average_reward=result.evaluation.average_reward,
                total_turnover=result.evaluation.total_turnover,
            )
            for result in strategies
        ],
    )

from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.analytics.returns import (
    annualized_volatility,
    cumulative_returns,
    maximum_drawdown,
    sharpe_ratio,
    sortino_ratio,
)
from app.backtest.engine import backtest_summary, run_backtest
from app.optimization.classical import (
    equal_weight,
    maximum_sharpe,
    minimum_volatility,
    risk_parity,
)
from app.optimization.frontier import efficient_frontier
from app.risk.metrics import (
    concentration,
    expected_shortfall,
    historical_var,
    parametric_var,
)

router = APIRouter(prefix="/quant", tags=["quant"])


class ReturnsRequest(BaseModel):
    returns: list[float] = Field(min_length=2)


class PortfolioRequest(BaseModel):
    assets: list[str] = Field(min_length=2)
    expected_returns: list[float] = Field(min_length=2)
    covariance: list[list[float]] = Field(min_length=2)


class PortfolioDataRequest(BaseModel):
    assets: list[str]
    start_date: str
    end_date: str


class BacktestRequest(BaseModel):
    dates: list[str] = Field(min_length=2)
    assets: list[str] = Field(min_length=2)
    prices: list[list[float]] = Field(min_length=2)
    weights: list[float] = Field(min_length=2)
    initial_capital: float = Field(default=100_000.0, gt=0)
    transaction_cost_bps: float = Field(default=5.0, ge=0)


def _portfolio_inputs(request: PortfolioRequest):
    if (
        len(request.assets) != len(request.expected_returns)
        or len(request.assets) != len(request.covariance)
        or any(len(row) != len(request.assets) for row in request.covariance)
    ):
        raise HTTPException(
            status_code=400,
            detail="Asset, return, and covariance dimensions must match.",
        )

    assets = pd.Index(request.assets)

    if not assets.is_unique:
        raise HTTPException(
            status_code=400,
            detail="Asset names must be unique.",
        )

    expected_returns = pd.Series(
        request.expected_returns,
        index=assets,
        dtype=float,
    )

    covariance = pd.DataFrame(
        request.covariance,
        index=assets,
        columns=assets,
        dtype=float,
    )

    return assets, expected_returns, covariance


@router.post("/returns")
def calculate_returns(request: ReturnsRequest) -> dict[str, float]:
    series = pd.Series(request.returns, dtype=float)

    return {
        "cumulative_return": float(cumulative_returns(series).iloc[-1]),
        "annualized_volatility": float(annualized_volatility(series)),
        "sharpe_ratio": float(sharpe_ratio(series)),
        "sortino_ratio": float(sortino_ratio(series)),
        "maximum_drawdown": float(maximum_drawdown(series)),
    }


@router.post("/risk")
def calculate_risk(request: ReturnsRequest) -> dict[str, float]:
    series = pd.Series(request.returns, dtype=float)

    return {
        "historical_var_95": historical_var(series, 0.95),
        "parametric_var_95": parametric_var(series, 0.95),
        "expected_shortfall_95": expected_shortfall(series, 0.95),
    }


@router.post("/optimize")
def optimize_portfolio(
    request: PortfolioRequest,
) -> dict[str, dict[str, float]]:
    _, expected_returns, covariance = _portfolio_inputs(request)

    portfolios = {
        "equal_weight": equal_weight(expected_returns),
        "minimum_volatility": minimum_volatility(
            expected_returns,
            covariance,
        ),
        "maximum_sharpe": maximum_sharpe(
            expected_returns,
            covariance,
        ),
        "risk_parity": risk_parity(
            expected_returns,
            covariance,
        ),
    }

    return {
        name: weights.to_dict()
        for name, weights in portfolios.items()
    }


@router.post("/frontier")
def calculate_frontier(
    request: PortfolioRequest,
) -> list[dict[str, float]]:
    _, expected_returns, covariance = _portfolio_inputs(request)

    result = efficient_frontier(
        expected_returns,
        covariance,
        points=20,
    )

    return result.to_dict(orient="records")


@router.post("/backtest")
def calculate_backtest(request: BacktestRequest) -> dict:
    if len(request.prices) != len(request.dates):
        raise HTTPException(
            status_code=400,
            detail="Price rows and dates must match.",
        )

    if len(request.weights) != len(request.assets):
        raise HTTPException(
            status_code=400,
            detail="Weights and assets must match.",
        )

    if len(set(request.assets)) != len(request.assets):
        raise HTTPException(
            status_code=400,
            detail="Asset names must be unique.",
        )

    prices = pd.DataFrame(
        request.prices,
        index=pd.to_datetime(request.dates),
        columns=request.assets,
        dtype=float,
    )

    weights = pd.Series(
        request.weights,
        index=request.assets,
        dtype=float,
    )

    result = run_backtest(
        prices,
        weights,
        initial_capital=request.initial_capital,
        transaction_cost_bps=request.transaction_cost_bps,
    )

    return {
        "summary": backtest_summary(result),
        "equity_curve": result.equity_curve.to_dict(),
        "portfolio_returns": result.portfolio_returns.to_dict(),
    }


@router.post("/concentration")
def calculate_concentration(
    request: PortfolioRequest,
) -> dict[str, float]:
    assets, _, _ = _portfolio_inputs(request)

    weights = equal_weight(
        pd.Series(
            1.0,
            index=assets,
            dtype=float,
        )
    )

    return {"herfindahl_index": concentration(weights)}


@router.post("/portfolio-data")
def portfolio_data(request: PortfolioDataRequest) -> dict:
    """Build optimization inputs from validated historical market data."""
    from datetime import date

    from app.analytics.portfolio import covariance_matrix, mean_returns
    from app.data.ingestion import MarketDataIngestionService
    from app.data.providers.yahoo import YahooFinanceProvider

    if len(request.assets) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least two assets are required.",
        )

    if len(set(request.assets)) != len(request.assets):
        raise HTTPException(
            status_code=400,
            detail="Asset names must be unique.",
        )

    try:
        start_date = date.fromisoformat(request.start_date)
        end_date = date.fromisoformat(request.end_date)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="Dates must use YYYY-MM-DD format.",
        ) from exc

    if start_date >= end_date:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before end_date.",
        )

    try:
        service = MarketDataIngestionService(YahooFinanceProvider())

        frames: dict[str, pd.Series] = {}

        for asset in request.assets:
            result = service.ingest(
                symbol=asset,
                start_date=start_date,
                end_date=end_date,
            )

            frame = result.data.sort_values("timestamp")

            if len(frame) < 2:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient historical data for {asset}.",
                )

            frames[asset] = (
                frame.set_index("timestamp")["adjusted_close"]
                .astype(float)
                .sort_index()
            )

        prices = pd.concat(frames, axis=1).dropna()

        if len(prices) < 2:
            raise HTTPException(
                status_code=400,
                detail="Insufficient overlapping historical data across assets.",
            )

        returns = prices.pct_change().dropna()

        if returns.empty:
            raise HTTPException(
                status_code=400,
                detail="Unable to calculate historical returns.",
            )

        expected = mean_returns(returns)
        covariance = covariance_matrix(returns)

        return {
            "assets": list(request.assets),
            "expected_returns": expected.tolist(),
            "covariance": covariance.to_numpy().tolist(),
            "start_date": request.start_date,
            "end_date": request.end_date,
            "observations": len(returns),
            "source": "yahoo_finance",
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Market data retrieval failed: {exc}",
        ) from exc

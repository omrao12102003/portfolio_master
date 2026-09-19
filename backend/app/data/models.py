from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

AssetType = Literal["equity", "etf"]


class MarketDataPoint(BaseModel):
    symbol: str = Field(min_length=1)
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    adjusted_close: float | None = None
    volume: float = Field(ge=0)
    asset_type: AssetType = "equity"
    source: str = Field(min_length=1)

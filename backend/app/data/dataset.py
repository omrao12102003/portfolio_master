from dataclasses import dataclass
from datetime import UTC, datetime

import pandas as pd

from app.data.storage import MarketDataStore
from app.data.validation import DataQualityReport, validate_market_data


@dataclass(frozen=True)
class DatasetMetadata:
    symbol: str
    source: str
    row_count: int
    date_min: str | None
    date_max: str | None
    ingested_at: str
    quality_valid: bool


class MarketDatasetManager:
    def __init__(self, store: MarketDataStore) -> None:
        self.store = store

    def save_validated(
        self,
        symbol: str,
        data: pd.DataFrame,
    ) -> DatasetMetadata:
        report: DataQualityReport = validate_market_data(data)

        if not report.valid:
            raise ValueError(
                f"Cannot store invalid market data: {report}"
            )

        self.store.save(symbol, data)

        return DatasetMetadata(
            symbol=symbol,
            source=str(data["source"].iloc[0]) if not data.empty else "unknown",
            row_count=report.row_count,
            date_min=report.date_min,
            date_max=report.date_max,
            ingested_at=datetime.now(UTC).isoformat(),
            quality_valid=report.valid,
        )

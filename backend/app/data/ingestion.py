from dataclasses import dataclass
from datetime import date

import pandas as pd

from app.data.normalization import normalize_market_data
from app.data.providers.base import MarketDataProvider
from app.data.validation import DataQualityReport, validate_market_data


@dataclass(frozen=True)
class IngestionResult:
    data: pd.DataFrame
    quality_report: DataQualityReport


class MarketDataIngestionService:
    def __init__(self, provider: MarketDataProvider) -> None:
        self.provider = provider

    def ingest(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> IngestionResult:
        raw_data = self.provider.get_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
        )

        frame = self._to_dataframe(raw_data)
        normalized = normalize_market_data(frame)
        quality_report = validate_market_data(normalized)

        if not quality_report.valid:
            raise ValueError(
                f"Market data validation failed: {quality_report}"
            )

        return IngestionResult(
            data=normalized,
            quality_report=quality_report,
        )

    @staticmethod
    def _to_dataframe(data: list) -> pd.DataFrame:
        if not data:
            return pd.DataFrame(
                columns=[
                    "symbol",
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "adjusted_close",
                    "volume",
                    "asset_type",
                    "source",
                ]
            )

        return pd.DataFrame(
            [
                item.model_dump() if hasattr(item, "model_dump") else item
                for item in data
            ]
        )

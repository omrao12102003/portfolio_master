from datetime import date
from pathlib import Path

import pandas as pd

from app.data.models import MarketDataPoint
from app.data.providers.base import MarketDataProvider


class CSVMarketDataProvider(MarketDataProvider):
    def __init__(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)

    def get_historical_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[MarketDataPoint]:
        if start_date > end_date:
            raise ValueError("start_date must be on or before end_date")

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Market data file not found: {self.file_path}"
            )

        frame = pd.read_csv(self.file_path)

        required_columns = {
            "symbol",
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "source",
        }

        missing = required_columns - set(frame.columns)
        if missing:
            raise ValueError(
                f"Missing required columns: {sorted(missing)}"
            )

        frame["timestamp"] = pd.to_datetime(
            frame["timestamp"],
            errors="raise",
        )

        start = pd.Timestamp(start_date)
        end = pd.Timestamp(end_date)

        frame = frame[
            (frame["symbol"] == symbol)
            & (frame["timestamp"] >= start)
            & (frame["timestamp"] < end + pd.Timedelta(value=1, unit="D"))
        ]

        points: list[MarketDataPoint] = []

        for _, row in frame.sort_values("timestamp").iterrows():
            adjusted_close = row.get("adjusted_close")

            if pd.isna(adjusted_close):
                adjusted_close = None
            else:
                adjusted_close = float(adjusted_close)

            points.append(
                MarketDataPoint(
                    symbol=str(row["symbol"]),
                    timestamp=row["timestamp"].to_pydatetime(),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    adjusted_close=adjusted_close,
                    volume=float(row["volume"]),
                    asset_type="equity",
                    source=str(row["source"]),
                )
            )

        return points

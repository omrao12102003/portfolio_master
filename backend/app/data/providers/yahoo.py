from datetime import date

import yfinance as yf

from app.data.models import MarketDataPoint
from app.data.providers.base import MarketDataProvider


class YahooFinanceProvider(MarketDataProvider):
    """Optional external provider.

    This adapter is deliberately isolated from the rest of the data pipeline.
    Yahoo availability is not treated as guaranteed.
    """

    def get_historical_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[MarketDataPoint]:
        if start_date > end_date:
            raise ValueError("start_date must be on or before end_date")

        try:
            frame = yf.Ticker(symbol).history(
                start=start_date,
                end=end_date,
                auto_adjust=False,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Yahoo Finance data request failed for {symbol}: {exc}"
            ) from exc

        if frame.empty:
            return []

        points: list[MarketDataPoint] = []

        for timestamp, row in frame.iterrows():
            points.append(
                MarketDataPoint(
                    symbol=symbol,
                    timestamp=timestamp.to_pydatetime(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    adjusted_close=float(row["Adj Close"]),
                    volume=float(row["Volume"]),
                    asset_type="equity",
                    source="yahoo_finance",
                )
            )

        return points

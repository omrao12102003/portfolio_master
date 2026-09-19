from datetime import date, datetime

from app.data.models import MarketDataPoint
from app.data.providers.base import MarketDataProvider


class MockMarketDataProvider(MarketDataProvider):
    def get_historical_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[MarketDataPoint]:
        if start_date > end_date:
            raise ValueError("start_date must be on or before end_date")

        return [
            MarketDataPoint(
                symbol=symbol,
                timestamp=datetime(2024, 1, 2),
                open=100.0,
                high=105.0,
                low=99.0,
                close=103.0,
                adjusted_close=102.5,
                volume=1000,
                asset_type="equity",
                source="mock",
            ),
            MarketDataPoint(
                symbol=symbol,
                timestamp=datetime(2024, 1, 3),
                open=102.0,
                high=106.0,
                low=101.0,
                close=104.0,
                adjusted_close=103.5,
                volume=1200,
                asset_type="equity",
                source="mock",
            ),
        ]

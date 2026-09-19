from abc import ABC, abstractmethod
from datetime import date

from app.data.models import MarketDataPoint


class MarketDataProvider(ABC):
    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[MarketDataPoint]:
        """Return validated provider-level market data for a symbol."""
        raise NotImplementedError

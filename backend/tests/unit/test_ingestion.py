from datetime import date

import pandas as pd
import pytest

from app.data.ingestion import MarketDataIngestionService
from app.data.models import MarketDataPoint
from app.data.providers.base import MarketDataProvider
from app.data.providers.mock import MockMarketDataProvider


class InvalidMarketDataProvider(MarketDataProvider):
    def get_historical_data(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[MarketDataPoint]:
        return [
            MarketDataPoint(
                symbol=symbol,
                timestamp=pd.Timestamp("2024-01-02").to_pydatetime(),
                open=100.0,
                high=90.0,
                low=99.0,
                close=103.0,
                volume=1000,
                asset_type="equity",
                source="test",
            )
        ]


def test_mock_provider_returns_deterministic_data():
    provider = MockMarketDataProvider()

    result = provider.get_historical_data(
        symbol="AAPL",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 5),
    )

    assert len(result) == 2
    assert result[0].symbol == "AAPL"
    assert result[0].source == "mock"
    assert result[0].close == 103.0


def test_mock_provider_rejects_invalid_date_range():
    provider = MockMarketDataProvider()

    with pytest.raises(ValueError, match="start_date"):
        provider.get_historical_data(
            symbol="AAPL",
            start_date=date(2024, 1, 5),
            end_date=date(2024, 1, 1),
        )


def test_ingestion_normalizes_and_validates_data():
    service = MarketDataIngestionService(MockMarketDataProvider())

    result = service.ingest(
        symbol="AAPL",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 5),
    )

    assert isinstance(result.data, pd.DataFrame)
    assert len(result.data) == 2
    assert list(result.data["symbol"]) == ["AAPL", "AAPL"]
    assert result.quality_report.valid is True
    assert result.quality_report.row_count == 2


def test_ingestion_rejects_invalid_provider_data():
    service = MarketDataIngestionService(InvalidMarketDataProvider())

    with pytest.raises(ValueError, match="validation failed"):
        service.ingest(
            symbol="AAPL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
        )


def test_ingestion_handles_empty_provider_result():
    class EmptyProvider(MarketDataProvider):
        def get_historical_data(
            self,
            symbol: str,
            start_date: date,
            end_date: date,
        ) -> list[MarketDataPoint]:
            return []

    service = MarketDataIngestionService(EmptyProvider())

    result = service.ingest(
        symbol="AAPL",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 5),
    )

    assert result.data.empty
    assert result.quality_report.valid is True
    assert result.quality_report.row_count == 0

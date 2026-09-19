from datetime import date
from pathlib import Path

import pytest

from app.data.providers.csv import CSVMarketDataProvider

FIXTURE = Path(__file__).parents[1] / "fixtures" / "market_data.csv"


def test_csv_provider_loads_and_filters_data():
    provider = CSVMarketDataProvider(FIXTURE)

    result = provider.get_historical_data(
        symbol="AAPL",
        start_date=date(2024, 1, 2),
        end_date=date(2024, 1, 3),
    )

    assert len(result) == 2
    assert result[0].timestamp.day == 2
    assert result[0].close == 103.0
    assert result[0].adjusted_close == 102.5
    assert result[0].source == "test_csv"


def test_csv_provider_filters_symbol():
    provider = CSVMarketDataProvider(FIXTURE)

    result = provider.get_historical_data(
        symbol="MSFT",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 5),
    )

    assert len(result) == 1
    assert result[0].symbol == "MSFT"


def test_csv_provider_returns_empty_for_missing_symbol():
    provider = CSVMarketDataProvider(FIXTURE)

    result = provider.get_historical_data(
        symbol="NVDA",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 5),
    )

    assert result == []


def test_csv_provider_rejects_invalid_date_range():
    provider = CSVMarketDataProvider(FIXTURE)

    with pytest.raises(ValueError, match="start_date"):
        provider.get_historical_data(
            symbol="AAPL",
            start_date=date(2024, 1, 5),
            end_date=date(2024, 1, 1),
        )


def test_csv_provider_rejects_missing_file(tmp_path):
    provider = CSVMarketDataProvider(tmp_path / "missing.csv")

    with pytest.raises(FileNotFoundError, match="Market data file not found"):
        provider.get_historical_data(
            symbol="AAPL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
        )


def test_csv_provider_rejects_missing_columns(tmp_path):
    file_path = tmp_path / "invalid.csv"
    file_path.write_text(
        "symbol,timestamp,open,high,low,close,volume\n"
        "AAPL,2024-01-02,100,105,99,103,1000\n"
    )

    provider = CSVMarketDataProvider(file_path)

    with pytest.raises(ValueError, match="Missing required columns"):
        provider.get_historical_data(
            symbol="AAPL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
        )

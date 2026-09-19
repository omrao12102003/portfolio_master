from datetime import date
from unittest.mock import patch

import pandas as pd
import pytest

from app.data.providers.yahoo import YahooFinanceProvider


def yahoo_history_fixture() -> pd.DataFrame:
    index = pd.DatetimeIndex(
        [
            "2024-01-02",
            "2024-01-03",
        ],
        name="Date",
    )

    return pd.DataFrame(
        {
            "Open": [100.0, 102.0],
            "High": [105.0, 106.0],
            "Low": [99.0, 101.0],
            "Close": [103.0, 104.0],
            "Adj Close": [102.5, 103.5],
            "Volume": [1000, 1200],
        },
        index=index,
    )


@patch("app.data.providers.yahoo.yf.Ticker")
def test_yahoo_provider_maps_history_to_market_data_points(mock_ticker):
    mock_ticker.return_value.history.return_value = yahoo_history_fixture()

    provider = YahooFinanceProvider()

    result = provider.get_historical_data(
        symbol="AAPL",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 5),
    )

    assert len(result) == 2
    assert result[0].symbol == "AAPL"
    assert result[0].open == 100.0
    assert result[0].close == 103.0
    assert result[0].adjusted_close == 102.5
    assert result[0].volume == 1000.0
    assert result[0].source == "yahoo_finance"

    mock_ticker.assert_called_once_with("AAPL")
    mock_ticker.return_value.history.assert_called_once_with(
        start=date(2024, 1, 1),
        end=date(2024, 1, 5),
        auto_adjust=False,
    )


@patch("app.data.providers.yahoo.yf.Ticker")
def test_yahoo_provider_returns_empty_list_for_empty_history(mock_ticker):
    mock_ticker.return_value.history.return_value = pd.DataFrame()

    provider = YahooFinanceProvider()

    result = provider.get_historical_data(
        symbol="UNKNOWN",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 5),
    )

    assert result == []


@patch("app.data.providers.yahoo.yf.Ticker")
def test_yahoo_provider_wraps_external_failure(mock_ticker):
    mock_ticker.return_value.history.side_effect = RuntimeError(
        "temporary Yahoo failure"
    )

    provider = YahooFinanceProvider()

    with pytest.raises(RuntimeError, match="Yahoo Finance data request failed"):
        provider.get_historical_data(
            symbol="AAPL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
        )


@patch("app.data.providers.yahoo.yf.Ticker")
def test_yahoo_provider_rejects_malformed_history(mock_ticker):
    index = pd.DatetimeIndex(["2024-01-02"])

    mock_ticker.return_value.history.return_value = pd.DataFrame(
        {
            "Open": [100.0],
            "High": [105.0],
            "Low": [99.0],
            "Close": [103.0],
            "Volume": [1000],
        },
        index=index,
    )

    provider = YahooFinanceProvider()

    with pytest.raises((KeyError, ValueError)):
        provider.get_historical_data(
            symbol="AAPL",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
        )


def test_yahoo_provider_rejects_invalid_date_range():
    provider = YahooFinanceProvider()

    with pytest.raises(ValueError, match="start_date"):
        provider.get_historical_data(
            symbol="AAPL",
            start_date=date(2024, 1, 5),
            end_date=date(2024, 1, 1),
        )

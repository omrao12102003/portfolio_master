import pandas as pd
import pytest

from app.data.normalization import normalize_market_data
from app.data.validation import validate_market_data


def valid_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "symbol": ["AAPL", "AAPL"],
            "timestamp": [
                "2024-01-02",
                "2024-01-03",
            ],
            "open": [100.0, 102.0],
            "high": [105.0, 106.0],
            "low": [99.0, 101.0],
            "close": [103.0, 104.0],
            "volume": [1000, 1200],
            "source": ["test", "test"],
        }
    )


def test_valid_market_data_passes():
    report = validate_market_data(valid_data())

    assert report.valid is True
    assert report.row_count == 2
    assert report.symbols == ("AAPL",)


def test_missing_required_column_fails():
    data = valid_data().drop(columns=["volume"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_market_data(data)


def test_duplicate_timestamp_is_detected():
    data = valid_data()
    data.loc[1, "timestamp"] = data.loc[0, "timestamp"]

    report = validate_market_data(data)

    assert report.duplicate_timestamps == 1
    assert report.valid is False


def test_negative_price_is_detected():
    data = valid_data()
    data.loc[0, "close"] = -1

    report = validate_market_data(data)

    assert report.invalid_prices == 1
    assert report.valid is False


def test_invalid_ohlc_relationship_is_detected():
    data = valid_data()
    data.loc[0, "high"] = 98

    report = validate_market_data(data)

    assert report.invalid_ohlc == 1
    assert report.valid is False


def test_negative_volume_is_detected():
    data = valid_data()
    data.loc[0, "volume"] = -10

    report = validate_market_data(data)

    assert report.invalid_volume == 1
    assert report.valid is False


def test_missing_values_are_detected():
    data = valid_data()
    data.loc[0, "close"] = None

    report = validate_market_data(data)

    assert report.missing_values > 0
    assert report.valid is False


def test_normalization_standardizes_columns_and_order():
    data = pd.DataFrame(
        {
            "symbol": ["AAPL", "AAPL"],
            "Date": ["2024-01-03", "2024-01-02"],
            "Open": [102.0, 100.0],
            "High": [106.0, 105.0],
            "Low": [101.0, 99.0],
            "Close": [104.0, 103.0],
            "Volume": [1200, 1000],
        }
    )

    normalized = normalize_market_data(
        data.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }
        )
    )

    assert list(normalized["timestamp"].dt.strftime("%Y-%m-%d")) == [
        "2024-01-02",
        "2024-01-03",
    ]
    assert list(normalized["symbol"]) == ["AAPL", "AAPL"]


def test_normalization_preserves_adjusted_close():
    data = pd.DataFrame(
        {
            "symbol": ["AAPL"],
            "Date": ["2024-01-02"],
            "open": [100.0],
            "high": [105.0],
            "low": [99.0],
            "close": [103.0],
            "Adj Close": [102.5],
            "volume": [1000],
        }
    )

    normalized = normalize_market_data(data)

    assert "adjusted_close" in normalized.columns
    assert normalized.loc[0, "adjusted_close"] == 102.5


def test_normalization_rejects_missing_required_column():
    data = valid_data().drop(columns=["close"])

    with pytest.raises(ValueError, match="Missing required columns"):
        normalize_market_data(data)




def test_missing_source_is_detected():
    data = valid_data().drop(columns=["source"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_market_data(data)

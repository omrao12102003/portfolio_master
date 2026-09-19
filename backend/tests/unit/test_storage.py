import pandas as pd
import pytest

from app.data.storage import MarketDataStore


def test_market_data_store_round_trip(tmp_path):
    store = MarketDataStore(tmp_path)

    data = pd.DataFrame(
        {
            "symbol": ["AAPL", "AAPL"],
            "timestamp": pd.to_datetime(
                ["2024-01-02", "2024-01-03"],
                utc=True,
            ),
            "open": [100.0, 102.0],
            "high": [105.0, 106.0],
            "low": [99.0, 101.0],
            "close": [103.0, 104.0],
            "adjusted_close": [102.5, 103.5],
            "volume": [1000.0, 1200.0],
            "asset_type": ["equity", "equity"],
            "source": ["test", "test"],
        }
    )

    path = store.save("AAPL", data)
    loaded = store.load("AAPL")

    assert path.exists()
    pd.testing.assert_frame_equal(loaded, data)


def test_market_data_store_missing_dataset(tmp_path):
    store = MarketDataStore(tmp_path)

    with pytest.raises(FileNotFoundError):
        store.load("AAPL")

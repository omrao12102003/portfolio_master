import pandas as pd
import pytest

from app.data.dataset import MarketDatasetManager
from app.data.storage import MarketDataStore


def valid_data() -> pd.DataFrame:
    return pd.DataFrame(
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


def test_dataset_manager_stores_validated_dataset(tmp_path):
    manager = MarketDatasetManager(MarketDataStore(tmp_path))

    metadata = manager.save_validated("AAPL", valid_data())

    assert metadata.symbol == "AAPL"
    assert metadata.source == "test"
    assert metadata.row_count == 2
    assert metadata.quality_valid is True
    assert metadata.date_min is not None
    assert metadata.date_max is not None


def test_dataset_manager_rejects_invalid_dataset(tmp_path):
    manager = MarketDatasetManager(MarketDataStore(tmp_path))

    data = valid_data()
    data.loc[0, "close"] = -1

    with pytest.raises(ValueError, match="Cannot store invalid"):
        manager.save_validated("AAPL", data)

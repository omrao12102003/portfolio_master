from datetime import date

from app.data.dataset import MarketDatasetManager
from app.data.ingestion import MarketDataIngestionService
from app.data.providers.mock import MockMarketDataProvider
from app.data.storage import MarketDataStore


def test_complete_market_data_pipeline(tmp_path):
    ingestion = MarketDataIngestionService(MockMarketDataProvider())
    store = MarketDataStore(tmp_path)
    manager = MarketDatasetManager(store)

    result = ingestion.ingest(
        symbol="AAPL",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 5),
    )

    metadata = manager.save_validated("AAPL", result.data)
    loaded = store.load("AAPL")

    assert result.quality_report.valid is True
    assert metadata.quality_valid is True
    assert metadata.row_count == 2
    assert len(loaded) == 2
    assert list(loaded["symbol"]) == ["AAPL", "AAPL"]
    assert list(loaded["source"]) == ["mock", "mock"]

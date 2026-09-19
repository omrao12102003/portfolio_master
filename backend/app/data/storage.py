from pathlib import Path

import pandas as pd


class MarketDataStore:
    def __init__(self, base_path: str | Path = "data/market") -> None:
        self.base_path = Path(base_path)

    def save(self, symbol: str, data: pd.DataFrame) -> Path:
        self.base_path.mkdir(parents=True, exist_ok=True)
        path = self.base_path / f"{symbol.upper()}.parquet"
        data.to_parquet(path, index=False)
        return path

    def load(self, symbol: str) -> pd.DataFrame:
        path = self.base_path / f"{symbol.upper()}.parquet"

        if not path.exists():
            raise FileNotFoundError(f"Market dataset not found: {path}")

        return pd.read_parquet(path)

from dataclasses import dataclass

import pandas as pd

REQUIRED_COLUMNS = {
    "symbol",
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "source",
}


@dataclass(frozen=True)
class DataQualityReport:
    row_count: int
    missing_values: int
    duplicate_timestamps: int
    invalid_prices: int
    invalid_ohlc: int
    invalid_volume: int
    date_min: str | None
    date_max: str | None
    symbols: tuple[str, ...]
    valid: bool


def validate_market_data(data: pd.DataFrame) -> DataQualityReport:
    missing_columns = REQUIRED_COLUMNS - set(data.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    frame = data.copy()

    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")

    numeric_columns = ["open", "high", "low", "close", "volume"]

    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    missing_values = int(
        frame[list(REQUIRED_COLUMNS)].isna().sum().sum()
    )

    duplicate_timestamps = int(
        frame.duplicated(subset=["symbol", "timestamp"]).sum()
    )

    invalid_prices = int(
        (
            (frame["open"] <= 0)
            | (frame["high"] <= 0)
            | (frame["low"] <= 0)
            | (frame["close"] <= 0)
        ).fillna(False).sum()
    )

    invalid_ohlc = int(
        (
            (frame["high"] < frame["low"])
            | (frame["high"] < frame["open"])
            | (frame["high"] < frame["close"])
            | (frame["low"] > frame["open"])
            | (frame["low"] > frame["close"])
        ).fillna(False).sum()
    )

    invalid_volume = int((frame["volume"] < 0).fillna(False).sum())

    valid_timestamps = frame["timestamp"].dropna()

    date_min = (
        valid_timestamps.min().isoformat()
        if not valid_timestamps.empty
        else None
    )
    date_max = (
        valid_timestamps.max().isoformat()
        if not valid_timestamps.empty
        else None
    )

    symbols = tuple(
        sorted(
            str(symbol)
            for symbol in frame["symbol"].dropna().unique()
        )
    )

    valid = (
        missing_values == 0
        and duplicate_timestamps == 0
        and invalid_prices == 0
        and invalid_ohlc == 0
        and invalid_volume == 0
    )

    return DataQualityReport(
        row_count=len(frame),
        missing_values=missing_values,
        duplicate_timestamps=duplicate_timestamps,
        invalid_prices=invalid_prices,
        invalid_ohlc=invalid_ohlc,
        invalid_volume=invalid_volume,
        date_min=date_min,
        date_max=date_max,
        symbols=symbols,
        valid=valid,
    )

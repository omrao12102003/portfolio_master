import pandas as pd

COLUMN_MAP = {
    "Date": "timestamp",
    "date": "timestamp",
    "Datetime": "timestamp",
    "datetime": "timestamp",
    "Adj Close": "adjusted_close",
    "adj_close": "adjusted_close",
}


def normalize_market_data(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()

    frame = frame.rename(columns=COLUMN_MAP)

    required_columns = [
        "symbol",
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    missing = set(required_columns) - set(frame.columns)
    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    frame["symbol"] = frame["symbol"].astype(str)
    frame["timestamp"] = pd.to_datetime(
        frame["timestamp"],
        errors="raise",
    )

    for column in ["open", "high", "low", "close", "volume"]:
        frame[column] = pd.to_numeric(
            frame[column],
            errors="raise",
        )

    if "adjusted_close" in frame.columns:
        frame["adjusted_close"] = pd.to_numeric(
            frame["adjusted_close"],
            errors="raise",
        )

    sort_columns = ["symbol", "timestamp"]

    return (
        frame.sort_values(sort_columns, kind="stable")
        .reset_index(drop=True)
    )

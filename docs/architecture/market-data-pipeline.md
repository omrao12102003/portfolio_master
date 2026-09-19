# Market Data Pipeline

## Purpose

The market data layer provides a provider-independent pipeline for acquiring,
normalizing, validating, and storing historical market data.

## Flow

Provider -> Ingestion -> Normalization -> Validation -> Dataset Store

## Providers

- Mock provider: deterministic automated testing.
- CSV provider: reproducible local datasets.
- Yahoo Finance provider: optional external historical data acquisition.

External providers are isolated behind `MarketDataProvider`.

## Validation

The pipeline checks:

- Required columns
- Missing values
- Duplicate symbol/timestamps
- Positive OHLC prices
- Valid OHLC relationships
- Non-negative volume
- Data provenance

Invalid data is rejected before storage.

## Storage

Validated datasets are stored as Parquet files.

This provides reproducible local datasets for future:

- Return calculations
- Risk analysis
- Portfolio optimization
- Backtesting
- Reinforcement learning

## Reproducibility

Quantitative research modules should consume validated stored datasets
rather than requesting external market data directly.

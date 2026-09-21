import { useState } from "react";
import { api } from "../services/api";
import type {
  OptimizationResponse,
  PortfolioRequest,
} from "../types/api";

const DEFAULT_ASSETS = ["SPY", "QQQ", "TLT"];

const DEFAULT_EXPECTED_RETURNS = [0.08, 0.12, 0.05];

function formatPercent(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

function formatRatio(value: number) {
  return Number.isFinite(value) ? value.toFixed(2) : "N/A";
}

function ResultCard({
  title,
  result,
  assets,
}: {
  title: string;
  result: {
    weights: number[];
    expected_return: number;
    volatility: number;
    sharpe_ratio: number;
  };
  assets: string[];
}) {
  return (
    <div className="optimization-result">
      <div className="optimization-result-header">
        <strong>{title}</strong>
        <span>Sharpe {formatRatio(result.sharpe_ratio)}</span>
      </div>

      <div className="result-metrics">
        <div>
          <span>Return</span>
          <strong>{formatPercent(result.expected_return)}</strong>
        </div>
        <div>
          <span>Volatility</span>
          <strong>{formatPercent(result.volatility)}</strong>
        </div>
      </div>

      <div className="weights-list">
        {result.weights.map((weight, index) => (
          <div className="weight-row" key={assets[index] ?? index}>
            <span>{assets[index] ?? `Asset ${index + 1}`}</span>
            <strong>{formatPercent(weight)}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

export function OptimizationPanel() {
  const [assets, setAssets] = useState(DEFAULT_ASSETS);
  const [expectedReturns, setExpectedReturns] = useState<number[]>(
    DEFAULT_EXPECTED_RETURNS,
  );
  const [minWeight, setMinWeight] = useState(0);
  const [maxWeight, setMaxWeight] = useState(1);
  const [results, setResults] = useState<OptimizationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateAsset = (index: number, value: string) => {
    setAssets((current) =>
      current.map((asset, i) => (i === index ? value.toUpperCase() : asset)),
    );
  };

  const updateExpectedReturn = (index: number, value: string) => {
    const numericValue = Number(value) / 100;

    setExpectedReturns((current) =>
      current.map((item, i) => (i === index ? numericValue : item)),
    );
  };

  const runOptimization = async () => {
    setLoading(true);
    setError(null);

    try {
      const portfolioData = await api.getPortfolioData({
        assets,
        start_date: "2024-01-01",
        end_date: "2024-12-31",
      });

      setExpectedReturns(portfolioData.expected_returns);

      const payload: PortfolioRequest = {
        assets: portfolioData.assets,
        expected_returns: portfolioData.expected_returns,
        covariance: portfolioData.covariance,
        risk_free_rate: 0.02,
        min_weight: minWeight,
        max_weight: maxWeight,
      };

      const response = await api.optimizePortfolio(payload);
      setResults(response);
    } catch (err) {
      setResults(null);
      setError(
        err instanceof Error
          ? err.message
          : "Optimization failed. Check the market data API.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <div className="page-heading">
        <div>
          <h2>Portfolio Optimization</h2>
          <p>
            Configure portfolio assumptions and run the quantitative
            optimization engine through the FastAPI backend.
          </p>
        </div>
      </div>

      <div className="optimization-layout">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Portfolio Inputs</h3>
              <p>Three-asset research portfolio</p>
            </div>
          </div>

          <div className="input-table">
            {assets.map((asset, index) => (
              <div className="input-row" key={index}>
                <label>
                  Asset
                  <input
                    value={asset}
                    onChange={(event) =>
                      updateAsset(index, event.target.value)
                    }
                  />
                </label>

                <label>
                  Expected return
                  <input
                    type="number"
                    step="0.5"
                    value={((expectedReturns[index] ?? 0) * 100).toFixed(2)}
                    onChange={(event) =>
                      updateExpectedReturn(index, event.target.value)
                    }
                  />
                </label>
              </div>
            ))}
          </div>

          <div className="bounds-grid">
            <label>
              Minimum weight
              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={minWeight}
                onChange={(event) => setMinWeight(Number(event.target.value))}
              />
            </label>

            <label>
              Maximum weight
              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={maxWeight}
                onChange={(event) => setMaxWeight(Number(event.target.value))}
              />
            </label>
          </div>

          <button
            className="primary-button optimize-button"
            type="button"
            onClick={runOptimization}
            disabled={loading}
          >
            {loading ? "Running optimization..." : "Run Optimization"}
          </button>

          {error && <div className="form-error">{error}</div>}
        </div>

        <div className="panel methodology-panel">
          <h3>Optimization Methods</h3>
          <p>
            The backend evaluates multiple portfolio construction approaches
            using the same return, covariance and constraint assumptions.
          </p>

          <div className="method-list">
            <div>
              <strong>Equal Weight</strong>
              <span>Baseline allocation</span>
            </div>
            <div>
              <strong>Minimum Volatility</strong>
              <span>Minimize portfolio risk</span>
            </div>
            <div>
              <strong>Maximum Sharpe</strong>
              <span>Optimize risk-adjusted return</span>
            </div>
            <div>
              <strong>Risk Parity</strong>
              <span>Balance portfolio risk contribution</span>
            </div>
          </div>
        </div>
      </div>

      {results && (
        <div className="optimization-results">
          <div className="section-title">
            <div>
              <h3>Optimization Results</h3>
              <p>Calculated by the quantitative optimization engine</p>
            </div>
          </div>

          <div className="result-grid">
            <ResultCard title="Equal Weight" result={results.equal_weight} assets={assets} />
            <ResultCard
              title="Minimum Volatility"
              result={results.minimum_volatility}
              assets={assets}
            />
            <ResultCard
              title="Maximum Sharpe"
              result={results.maximum_sharpe}
              assets={assets}
            />
            <ResultCard title="Risk Parity" result={results.risk_parity} assets={assets} />
          </div>
        </div>
      )}
    </section>
  );
}

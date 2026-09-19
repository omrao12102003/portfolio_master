import { useMemo, useState } from "react";
import { api } from "../services/api";
import type { BacktestResponse } from "../types/backtest";

const ASSETS = ["SPY", "QQQ", "TLT"];

function formatPercent(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

function formatMoney(value: number) {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
    maximumFractionDigits: 0,
  }).format(value);
}

function EquityChart({ result }: { result: BacktestResponse }) {
  const entries = Object.entries(result.equity_curve);

  if (!entries.length) {
    return null;
  }

  const width = 760;
  const height = 320;
  const padding = 48;
  const values = entries.map(([, value]) => value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const x = (index: number) =>
    padding +
    (index / Math.max(entries.length - 1, 1)) * (width - padding * 2);

  const y = (value: number) =>
    height -
    padding -
    ((value - min) / range) * (height - padding * 2);

  const path = entries
    .map(([, value], index) => {
      const command = index === 0 ? "M" : "L";
      return `${command} ${x(index)} ${y(value)}`;
    })
    .join(" ");

  return (
    <div className="backtest-chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Portfolio equity curve">
        <line
          x1={padding}
          y1={height - padding}
          x2={width - padding}
          y2={height - padding}
          className="chart-axis"
        />
        <line
          x1={padding}
          y1={padding}
          x2={padding}
          y2={height - padding}
          className="chart-axis"
        />
        <path d={path} className="backtest-line" fill="none" />
        <text x={width / 2} y={height - 12} textAnchor="middle">
          Time
        </text>
        <text
          x="14"
          y={height / 2}
          textAnchor="middle"
          transform={`rotate(-90 14 ${height / 2})`}
        >
          Portfolio Value
        </text>
      </svg>
    </div>
  );
}

export function BacktestDashboard() {
  const [result, setResult] = useState<BacktestResponse | null>(null);
  const [rebalanceFrequency, setRebalanceFrequency] = useState<
    "daily" | "weekly" | "monthly"
  >("monthly");
  const [transactionCostBps, setTransactionCostBps] = useState(5);
  const [initialCapital, setInitialCapital] = useState(100000);
  const [loading, setLoading] = useState(false);
  const [observations, setObservations] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const weights = useMemo(
    () => ASSETS.map(() => 1 / ASSETS.length),
    [],
  );

  const runBacktest = async () => {
    setLoading(true);
    setError(null);

    try {
      const portfolio = await api.getPortfolioData({
        assets: ASSETS,
        start_date: "2024-01-01",
        end_date: "2024-12-31",
      });

      const response = await api.runBacktest({
        assets: portfolio.assets,
        dates: portfolio.historical_dates,
        prices: portfolio.historical_prices,
        weights,
        initial_capital: initialCapital,
        transaction_cost_bps: transactionCostBps,
        rebalance_frequency: rebalanceFrequency,
      });

      setResult(response);
      setObservations(portfolio.observations);
    } catch (err) {
      setResult(null);
      setError(
        err instanceof Error
          ? err.message
          : "Backtest failed. Check the market data API.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <div className="page-heading">
        <div>
          <h2>Historical Backtesting</h2>
          <p>
            Evaluate portfolio performance with historical prices, transaction
            costs and configurable rebalancing.
          </p>
        </div>
      </div>

      <div className="backtest-layout">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Backtest Configuration</h3>
              <p>{ASSETS.join(" / ")} equal-weight portfolio</p>
            </div>
          </div>

          <div className="backtest-inputs">
            <label>
              Initial capital
              <input
                type="number"
                min="1"
                value={initialCapital}
                onChange={(event) =>
                  setInitialCapital(Number(event.target.value))
                }
              />
            </label>

            <label>
              Transaction cost (bps)
              <input
                type="number"
                min="0"
                step="0.5"
                value={transactionCostBps}
                onChange={(event) =>
                  setTransactionCostBps(Number(event.target.value))
                }
              />
            </label>

            <label>
              Rebalance frequency
              <select
                value={rebalanceFrequency}
                onChange={(event) =>
                  setRebalanceFrequency(
                    event.target.value as "daily" | "weekly" | "monthly",
                  )
                }
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </label>
          </div>

          <button
            className="primary-button optimize-button"
            type="button"
            onClick={() => void runBacktest()}
            disabled={loading}
          >
            {loading ? "Running backtest..." : "Run Backtest"}
          </button>

          {error && <div className="form-error">{error}</div>}
        </div>

        <div className="panel">
          <h3>Backtest Dataset</h3>
          <div className="backtest-dataset">
            <div>
              <span>Assets</span>
              <strong>{ASSETS.join(" / ")}</strong>
            </div>
            <div>
              <span>Period</span>
              <strong>2024</strong>
            </div>
            <div>
              <span>Observations</span>
              <strong>{observations || "Not loaded"}</strong>
            </div>
          </div>
        </div>
      </div>

      {result && (
        <>
          <div className="backtest-metrics">
            <div className="panel">
              <span>Final Capital</span>
              <strong>{formatMoney(result.summary.final_capital)}</strong>
            </div>
            <div className="panel">
              <span>Cumulative Return</span>
              <strong>{formatPercent(result.summary.cumulative_return)}</strong>
            </div>
            <div className="panel">
              <span>Annualized Return</span>
              <strong>{formatPercent(result.summary.annualized_return)}</strong>
            </div>
            <div className="panel">
              <span>Volatility</span>
              <strong>
                {formatPercent(result.summary.annualized_volatility)}
              </strong>
            </div>
            <div className="panel">
              <span>Maximum Drawdown</span>
              <strong>{formatPercent(result.summary.maximum_drawdown)}</strong>
            </div>
            <div className="panel">
              <span>Transaction Costs</span>
              <strong>{formatPercent(result.summary.total_transaction_cost)}</strong>
            </div>
          </div>

          <div className="panel backtest-panel">
            <div className="panel-header">
              <div>
                <h3>Equity Curve</h3>
                <p>Historical portfolio value after transaction costs.</p>
              </div>
            </div>
            <EquityChart result={result} />
          </div>
        </>
      )}
    </section>
  );
}

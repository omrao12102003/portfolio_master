import { useEffect, useState } from "react";
import { MetricCard } from "../components/MetricCard";
import { api } from "../services/api";
import type { ReturnsResponse } from "../types/api";

const SAMPLE_RETURNS = [
  0.004,
  0.002,
  -0.003,
  0.006,
  0.003,
  -0.001,
  0.005,
  0.002,
  -0.002,
  0.004,
  0.003,
  0.001,
];

function formatPercent(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

function formatRatio(value: number) {
  return Number.isFinite(value) ? value.toFixed(2) : "N/A";
}

export function Dashboard() {
  const [metrics, setMetrics] = useState<ReturnsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .calculateReturns(SAMPLE_RETURNS)
      .then(setMetrics)
      .catch(() => {
        setError("Unable to load portfolio analytics from the API.");
      })
      .finally(() => setLoading(false));
  }, []);

  const metricCards = metrics
    ? [
        {
          label: "Cumulative Return",
          value: formatPercent(metrics.total_return),
          description: "Calculated by the quantitative backend",
        },
        {
          label: "Annualized Return",
          value: formatPercent(metrics.annualized_return),
          description: "Annualized historical return",
        },
        {
          label: "Volatility",
          value: formatPercent(metrics.annualized_volatility),
          description: "Annualized portfolio volatility",
        },
        {
          label: "Sharpe Ratio",
          value: formatRatio(metrics.sharpe_ratio),
          description: "Risk-adjusted return",
        },
      ]
    : [];

  return (
    <section>
      <div className="page-heading">
        <div>
          <h2>Investment Dashboard</h2>
          <p>
            Monitor portfolio performance, risk, optimization and research
            signals from one workspace.
          </p>
        </div>

        <button className="primary-button" type="button">
          Build Portfolio
        </button>
      </div>

      {loading && (
        <div className="panel state-panel">
          <strong>Loading quantitative analytics...</strong>
          <span>Requesting metrics from the FastAPI backend.</span>
        </div>
      )}

      {error && (
        <div className="panel state-panel error-panel">
          <strong>Analytics unavailable</strong>
          <span>{error}</span>
        </div>
      )}

      {!loading && !error && metrics && (
        <>
          <div className="metric-grid">
            {metricCards.map((metric) => (
              <MetricCard key={metric.label} {...metric} />
            ))}
          </div>

          <div className="dashboard-grid">
            <div className="panel performance-panel">
              <div className="panel-header">
                <div>
                  <h3>Quantitative Performance</h3>
                  <p>Metrics returned directly from the FastAPI analytics engine</p>
                </div>
              </div>

              <div className="analytics-table">
                <div>
                  <span>Downside Volatility</span>
                  <strong>{formatPercent(metrics.downside_volatility)}</strong>
                </div>
                <div>
                  <span>Sortino Ratio</span>
                  <strong>{formatRatio(metrics.sortino_ratio)}</strong>
                </div>
                <div>
                  <span>Maximum Drawdown</span>
                  <strong>{formatPercent(metrics.maximum_drawdown)}</strong>
                </div>
              </div>
            </div>

            <div className="panel">
              <div className="panel-header">
                <div>
                  <h3>Backend Status</h3>
                  <p>Live application architecture</p>
                </div>
              </div>

              <div className="backend-status">
                <div className="status-check">✓</div>
                <div>
                  <strong>Quant API operational</strong>
                  <span>Frontend → FastAPI → Analytics Engine</span>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </section>
  );
}

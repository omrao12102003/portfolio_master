import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { RiskResponse } from "../types/risk";

const sampleReturns = [
  0.012,
  0.006,
  -0.008,
  0.014,
  -0.003,
  0.009,
];

function formatPercent(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

export function RiskDashboard() {
  const [risk, setRisk] = useState<RiskResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .calculateRisk({
        returns: sampleReturns,
        risk_free_rate: 0.02,
      })
      .then(setRisk)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <section className="page">
      <div className="page-header">
        <div>
          <h1>Risk Analytics</h1>
          <p>Portfolio risk measures calculated by the quantitative risk engine.</p>
        </div>
      </div>

      {error && <div className="status-card error">{error}</div>}

      {!risk && !error && <div className="status-card">Calculating risk metrics...</div>}

      {risk && (
        <div className="metric-grid">
          <article className="metric-card">
            <span>Volatility</span>
            <strong>{formatPercent(risk.volatility)}</strong>
          </article>
          <article className="metric-card">
            <span>Downside Volatility</span>
            <strong>{formatPercent(risk.downside_volatility)}</strong>
          </article>
          <article className="metric-card">
            <span>Sharpe Ratio</span>
            <strong>{risk.sharpe_ratio.toFixed(2)}</strong>
          </article>
          <article className="metric-card">
            <span>Sortino Ratio</span>
            <strong>{risk.sortino_ratio.toFixed(2)}</strong>
          </article>
          <article className="metric-card">
            <span>Maximum Drawdown</span>
            <strong>{formatPercent(risk.maximum_drawdown)}</strong>
          </article>
          <article className="metric-card">
            <span>Historical VaR 95%</span>
            <strong>{formatPercent(risk.historical_var_95)}</strong>
          </article>
          <article className="metric-card">
            <span>Parametric VaR 95%</span>
            <strong>{formatPercent(risk.parametric_var_95)}</strong>
          </article>
          <article className="metric-card">
            <span>Expected Shortfall 95%</span>
            <strong>{formatPercent(risk.expected_shortfall_95)}</strong>
          </article>
        </div>
      )}
    </section>
  );
}

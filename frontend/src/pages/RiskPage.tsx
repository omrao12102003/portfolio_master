import { useState } from "react"
import MetricCard from "../components/MetricCard"
import { calculateRisk } from "../services/api"
import type { RiskResponse } from "../types/api"

const returns = [
  0.004, -0.002, 0.006, 0.003, -0.001, 0.005,
  0.002, -0.003, 0.004, 0.006, -0.002, 0.003,
]

export default function RiskPage() {
  const [risk, setRisk] = useState<RiskResponse | null>(null)
  const [loading, setLoading] = useState(false)

  async function loadRisk() {
    setLoading(true)
    try {
      setRisk(await calculateRisk(returns))
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">Risk analytics</span>
          <h2>Risk Dashboard</h2>
          <p>Deterministic portfolio risk measurements.</p>
        </div>
        <button onClick={() => void loadRisk()} disabled={loading}>
          {loading ? "Calculating..." : "Calculate Risk"}
        </button>
      </div>

      <div className="metric-grid">
        <MetricCard
          label="Volatility"
          value={risk ? `${(risk.volatility * 100).toFixed(2)}%` : "—"}
        />
        <MetricCard
          label="Sharpe"
          value={risk?.sharpe_ratio.toFixed(2) ?? "—"}
        />
        <MetricCard
          label="Historical VaR 95%"
          value={risk ? `${(risk.historical_var_95 * 100).toFixed(2)}%` : "—"}
        />
        <MetricCard
          label="Expected Shortfall"
          value={risk ? `${(risk.expected_shortfall_95 * 100).toFixed(2)}%` : "—"}
        />
      </div>

      <section className="panel">
        <div className="stat-list">
          <div>
            <span>Downside volatility</span>
            <strong>{risk ? `${(risk.downside_volatility * 100).toFixed(2)}%` : "—"}</strong>
          </div>
          <div>
            <span>Sortino</span>
            <strong>{risk?.sortino_ratio.toFixed(2) ?? "—"}</strong>
          </div>
          <div>
            <span>Parametric VaR 95%</span>
            <strong>{risk ? `${(risk.parametric_var_95 * 100).toFixed(2)}%` : "—"}</strong>
          </div>
          <div>
            <span>Maximum drawdown</span>
            <strong>{risk ? `${(risk.maximum_drawdown * 100).toFixed(2)}%` : "—"}</strong>
          </div>
        </div>
      </section>
    </>
  )
}

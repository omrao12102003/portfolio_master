import { useEffect, useState } from "react"
import MetricCard from "../components/MetricCard"
import ConnectionStatus from "../components/ConnectionStatus"
import { calculateReturns, getHealth, getReadiness } from "../services/api"
import type { ReturnsResponse } from "../types/api"

const sampleReturns = [
  0.004, -0.002, 0.006, 0.003, -0.001, 0.005, 0.002,
  -0.003, 0.004, 0.006, -0.002, 0.003,
]

export default function Dashboard() {
  const [connected, setConnected] = useState(false)
  const [environment, setEnvironment] = useState("—")
  const [metrics, setMetrics] = useState<ReturnsResponse | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    async function load() {
      try {
        const [, readiness, returns] = await Promise.all([
          getHealth(),
          getReadiness(),
          calculateReturns(sampleReturns),
        ])

        setConnected(true)
        setEnvironment(readiness.environment)
        setMetrics(returns)
      } catch (err) {
        setConnected(false)
        setError(err instanceof Error ? err.message : "API unavailable")
      }
    }

    void load()
  }, [])

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">Overview</span>
          <h2>Portfolio Dashboard</h2>
          <p>Live quantitative analytics from the Portfolio Master API.</p>
        </div>
        <ConnectionStatus connected={connected} />
      </div>

      {error && <div className="alert">{error}</div>}

      <div className="metric-grid">
        <MetricCard
          label="Cumulative Return"
          value={metrics ? `${(metrics.cumulative_return * 100).toFixed(2)}%` : "—"}
        />
        <MetricCard
          label="Annualized Return"
          value={metrics ? `${(metrics.annualized_return * 100).toFixed(2)}%` : "—"}
        />
        <MetricCard
          label="Volatility"
          value={metrics ? `${(metrics.annualized_volatility * 100).toFixed(2)}%` : "—"}
        />
        <MetricCard
          label="Sharpe Ratio"
          value={metrics ? metrics.sharpe_ratio.toFixed(2) : "—"}
        />
      </div>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Risk profile</span>
              <h3>Portfolio Statistics</h3>
            </div>
          </div>

          <div className="stat-list">
            <div>
              <span>Downside volatility</span>
              <strong>
                {metrics?.downside_volatility
                  ? `${(metrics.downside_volatility * 100).toFixed(2)}%`
                  : "—"}
              </strong>
            </div>
            <div>
              <span>Sortino ratio</span>
              <strong>
                {metrics?.sortino_ratio?.toFixed(2) ?? "—"}
              </strong>
            </div>
            <div>
              <span>Maximum drawdown</span>
              <strong>
                {metrics?.maximum_drawdown
                  ? `${(metrics.maximum_drawdown * 100).toFixed(2)}%`
                  : "—"}
              </strong>
            </div>
            <div>
              <span>Environment</span>
              <strong>{environment}</strong>
            </div>
          </div>
        </section>

        <section className="panel">
          <span className="eyebrow">Workflow</span>
          <h3>Research Pipeline</h3>
          <div className="workflow-list">
            <span>01 · Market data</span>
            <span>02 · Portfolio analytics</span>
            <span>03 · Risk & optimization</span>
            <span>04 · Historical backtest</span>
            <span>05 · SEC research & RAG</span>
            <span>06 · Grounded reporting</span>
          </div>
        </section>
      </div>
    </>
  )
}

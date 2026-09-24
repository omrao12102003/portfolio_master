import { useEffect, useState } from "react"
import MetricCard from "../components/MetricCard"
import ConnectionStatus from "../components/ConnectionStatus"
import {
  calculateReturns,
  calculateRisk,
  getPortfolioData,
  getReadiness,
} from "../services/api"
import type { ReturnsResponse, RiskResponse } from "../types/api"

const ASSETS = ["SPY", "QQQ", "TLT"]
const START_DATE = "2024-01-01"
const END_DATE = "2024-12-31"
const RISK_FREE_RATE = 0.02

function formatPercent(value: number | undefined) {
  return value !== undefined && Number.isFinite(value)
    ? `${(value * 100).toFixed(2)}%`
    : "—"
}

function formatNumber(value: number | undefined) {
  return value !== undefined && Number.isFinite(value)
    ? value.toFixed(2)
    : "—"
}

export default function Dashboard() {
  const [connected, setConnected] = useState(false)
  const [environment, setEnvironment] = useState("—")
  const [metrics, setMetrics] = useState<ReturnsResponse | null>(null)
  const [risk, setRisk] = useState<RiskResponse | null>(null)
  const [observations, setObservations] = useState(0)
  const [error, setError] = useState("")

  useEffect(() => {
    async function load() {
      setError("")

      try {
        const readiness = await getReadiness()
        setConnected(true)
        setEnvironment(readiness.environment)
      } catch (err) {
        setConnected(false)
        setError(
          err instanceof Error
            ? `Backend connection failed: ${err.message}`
            : "Backend connection failed",
        )
        return
      }

      try {
        const portfolio = await getPortfolioData({
          assets: ASSETS,
          start_date: START_DATE,
          end_date: END_DATE,
        })

        setObservations(portfolio.observations)

        const [returns, riskMetrics] = await Promise.all([
          calculateReturns(portfolio.portfolio_returns, RISK_FREE_RATE),
          calculateRisk(portfolio.portfolio_returns, RISK_FREE_RATE),
        ])

        setMetrics(returns)
        setRisk(riskMetrics)
      } catch (err) {
        setError(
          err instanceof Error
            ? `Portfolio analytics failed: ${err.message}`
            : "Portfolio analytics failed",
        )
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
          <p>
            Historical portfolio analytics for SPY, QQQ and TLT using market
            data from {START_DATE} to {END_DATE}.
          </p>
        </div>
        <ConnectionStatus connected={connected} />
      </div>

      {error && <div className="alert">{error}</div>}

      <div className="metric-grid">
        <MetricCard
          label="Cumulative Return"
          value={formatPercent(metrics?.cumulative_return)}
        />
        <MetricCard
          label="Annualized Return"
          value={formatPercent(metrics?.annualized_return)}
        />
        <MetricCard
          label="Volatility"
          value={formatPercent(risk?.volatility)}
        />
        <MetricCard
          label="Sharpe Ratio"
          value={formatNumber(risk?.sharpe_ratio)}
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
                {formatPercent(risk?.downside_volatility)}
              </strong>
            </div>

            <div>
              <span>Sortino ratio</span>
              <strong>
                {formatNumber(risk?.sortino_ratio)}
              </strong>
            </div>

            <div>
              <span>Maximum drawdown</span>
              <strong>
                {formatPercent(risk?.maximum_drawdown)}
              </strong>
            </div>

            <div>
              <span>Observations</span>
              <strong>{observations || "—"}</strong>
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

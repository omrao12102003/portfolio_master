import { useEffect, useState } from "react"
import MetricCard from "../components/MetricCard"
import ConnectionStatus from "../components/ConnectionStatus"
import {
  calculateReturns,
  calculateRisk,
  getHealth,
  getPortfolioData,
  getReadiness,
} from "../services/api"
import type { ReturnsResponse, RiskResponse } from "../types/api"

const ASSETS = ["SPY", "QQQ", "TLT"]
const START_DATE = "2024-01-01"
const END_DATE = "2024-12-31"
const RISK_FREE_RATE = 0.02

export default function Dashboard() {
  const [connected, setConnected] = useState(false)
  const [environment, setEnvironment] = useState("—")
  const [metrics, setMetrics] = useState<ReturnsResponse | null>(null)
  const [risk, setRisk] = useState<RiskResponse | null>(null)
  const [observations, setObservations] = useState(0)
  const [error, setError] = useState("")

  useEffect(() => {
    async function load() {
      try {
        const [, readiness, portfolio] = await Promise.all([
          getHealth(),
          getReadiness(),
          getPortfolioData({
            assets: ASSETS,
            start_date: START_DATE,
            end_date: END_DATE,
          }),
        ])

        const [returns, riskMetrics] = await Promise.all([
          calculateReturns(portfolio.portfolio_returns, RISK_FREE_RATE),
          calculateRisk(
            portfolio.portfolio_returns,
            RISK_FREE_RATE,
          ),
        ])

        setConnected(true)
        setEnvironment(readiness.environment)
        setMetrics(returns)
        setRisk(riskMetrics)
        setObservations(portfolio.observations)
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
          value={
            metrics
              ? `${(metrics.cumulative_return * 100).toFixed(2)}%`
              : "—"
          }
        />
        <MetricCard
          label="Annualized Return"
          value={
            metrics
              ? `${(metrics.annualized_return * 100).toFixed(2)}%`
              : "—"
          }
        />
        <MetricCard
          label="Volatility"
          value={
            risk
              ? `${(risk.volatility * 100).toFixed(2)}%`
              : "—"
          }
        />
        <MetricCard
          label="Sharpe Ratio"
          value={
            risk
              ? risk.sharpe_ratio.toFixed(2)
              : "—"
          }
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
                {risk
                  ? `${(risk.downside_volatility * 100).toFixed(2)}%`
                  : "—"}
              </strong>
            </div>

            <div>
              <span>Sortino ratio</span>
              <strong>
                {risk ? risk.sortino_ratio.toFixed(2) : "—"}
              </strong>
            </div>

            <div>
              <span>Maximum drawdown</span>
              <strong>
                {risk
                  ? `${(risk.maximum_drawdown * 100).toFixed(2)}%`
                  : "—"}
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

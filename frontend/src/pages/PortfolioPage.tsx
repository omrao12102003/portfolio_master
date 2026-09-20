import { useState } from "react"
import MetricCard from "../components/MetricCard"
import { optimizePortfolio } from "../services/api"
import type { OptimizationResult } from "../types/api"

const assets = ["SPY", "QQQ", "TLT"]

const covariance = [
  [0.04, 0.012, 0.006],
  [0.012, 0.09, 0.004],
  [0.006, 0.004, 0.025],
]

export default function PortfolioPage() {
  const [results, setResults] = useState<OptimizationResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  async function optimize() {
    setLoading(true)
    setError("")

    try {
      const response = await optimizePortfolio({
        assets,
        expected_returns: [0.08, 0.12, 0.05],
        covariance,
        risk_free_rate: 0.02,
        min_weight: 0,
        max_weight: 1,
      })

      setResults(response.results)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Optimization failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">Portfolio construction</span>
          <h2>Portfolio Optimizer</h2>
          <p>Run the existing classical optimization engine.</p>
        </div>
        <button onClick={() => void optimize()} disabled={loading}>
          {loading ? "Optimizing..." : "Run Optimization"}
        </button>
      </div>

      {error && <div className="alert">{error}</div>}

      <section className="panel">
        <div className="asset-row">
          {assets.map((asset) => (
            <span className="asset-chip" key={asset}>{asset}</span>
          ))}
        </div>
      </section>

      {results.length > 0 && (
        <div className="result-grid">
          {results.map((result) => (
            <section className="panel" key={result.method}>
              <span className="eyebrow">{result.method}</span>
              <h3>Allocation</h3>

              <div className="weights">
                {assets.map((asset, index) => (
                  <div key={asset}>
                    <span>{asset}</span>
                    <strong>
                      {((result.weights[index] ?? 0) * 100).toFixed(1)}%
                    </strong>
                  </div>
                ))}
              </div>

              <div className="mini-metrics">
                <MetricCard
                  label="Return"
                  value={`${(result.expected_return * 100).toFixed(2)}%`}
                />
                <MetricCard
                  label="Volatility"
                  value={`${(result.volatility * 100).toFixed(2)}%`}
                />
                <MetricCard
                  label="Sharpe"
                  value={result.sharpe_ratio.toFixed(2)}
                />
              </div>
            </section>
          ))}
        </div>
      )}
    </>
  )
}

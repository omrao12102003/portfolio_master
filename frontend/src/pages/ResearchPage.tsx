import { useState } from "react"
import { createInvestmentReport } from "../services/api"
import type { GroundedReportResponse } from "../types/api"

const ASSETS = ["SPY", "QQQ", "TLT"]

export default function ResearchPage() {
  const [question, setQuestion] = useState(
    "Assess the investment risks and relevant company fundamentals.",
  )
  const [ticker, setTicker] = useState("AAPL")
  const [company, setCompany] = useState("Apple")
  const [report, setReport] = useState<
    (GroundedReportResponse & {
      workflow?: {
        evidence_count: number
        sources: string[]
      }
    }) | null
  >(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  async function generate() {
    setLoading(true)
    setError("")

    try {
      const portfolio = await fetch(
        `${(
          import.meta.env.VITE_API_BASE_URL ??
            "https://portfolio-master-api.onrender.com"
        ).replace(/\/$/, "")}/quant/portfolio-data`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            assets: ASSETS,
            start_date: "2024-01-01",
            end_date: "2024-12-31",
          }),
        },
      )

      if (!portfolio.ok) {
        throw new Error("Unable to load portfolio market data.")
      }

      const portfolioData = await portfolio.json()

      const riskResponse = await fetch(
        `${(
          import.meta.env.VITE_API_BASE_URL ??
            "https://portfolio-master-api.onrender.com"
        ).replace(/\/$/, "")}/quant/risk`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            returns: portfolioData.portfolio_returns,
            risk_free_rate: 0.02,
          }),
        },
      )

      if (!riskResponse.ok) {
        throw new Error("Unable to calculate portfolio risk.")
      }

      const risk = await riskResponse.json()

      const result = await createInvestmentReport({
        title: `${ticker.toUpperCase()} Investment Research`,
        question,
        summary:
          "Quantitative portfolio analytics combined with primary-source financial evidence retrieved from the research corpus.",
        metrics: [
          {
            name: "Annualized Portfolio Return",
            value: portfolioData.portfolio_returns.length
              ? portfolioData.portfolio_returns.reduce(
                  (total: number, value: number) => total + value,
                  0,
                ) / portfolioData.portfolio_returns.length
              : 0,
          },
          {
            name: "Portfolio Volatility",
            value: risk.volatility,
          },
          {
            name: "Sharpe Ratio",
            value: risk.sharpe_ratio,
          },
          {
            name: "Maximum Drawdown",
            value: risk.maximum_drawdown,
          },
          {
            name: "Historical VaR 95%",
            value: risk.historical_var_95,
          },
          {
            name: "Expected Shortfall 95%",
            value: risk.expected_shortfall_95,
          },
        ],
        ticker: ticker.trim().toUpperCase() || undefined,
        company: company.trim() || undefined,
        findings: [
          "Quantitative metrics are calculated independently of the language model.",
          "Financial evidence is retrieved from the indexed research corpus.",
          "Historical analysis should not be interpreted as a forecast.",
        ],
        methodology: [
          "Historical market data from the portfolio data pipeline.",
          "Deterministic portfolio risk analytics.",
          "Metadata-filtered financial document retrieval.",
          "Grounded reporting using retrieved evidence.",
        ],
        limitations: [
          "Historical market performance does not guarantee future results.",
          "Retrieved financial filings represent historical disclosures.",
          "The research corpus may not contain every relevant disclosure.",
        ],
        top_k: 5,
      })

      setReport(result)
    } catch (err) {
      setReport(null)
      setError(
        err instanceof Error ? err.message : "Research request failed.",
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">Research copilot</span>
          <h2>Investment Research</h2>
          <p>
            Quantitative portfolio analytics combined with retrieved primary-source
            financial evidence.
          </p>
        </div>
      </div>

      <section className="panel research-input">
        <div className="research-filters">
          <label>
            Ticker
            <input
              value={ticker}
              onChange={(event) =>
                setTicker(event.target.value.toUpperCase())
              }
              placeholder="AAPL"
            />
          </label>

          <label>
            Company
            <input
              value={company}
              onChange={(event) => setCompany(event.target.value)}
              placeholder="Apple"
            />
          </label>
        </div>

        <label htmlFor="question">Research question</label>
        <textarea
          id="question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          rows={4}
        />

        <button onClick={() => void generate()} disabled={loading}>
          {loading ? "Retrieving evidence..." : "Generate Research Report"}
        </button>
      </section>

      {error && <div className="alert">{error}</div>}

      {report && (
        <div className="research-grid">
          <section className="panel">
            <span className="eyebrow">Grounded report</span>
            <h3>{report.title}</h3>
            <p>{report.summary}</p>

            <h4>Quantitative metrics</h4>
            <div className="stat-list">
              {report.metrics.map((metric) => (
                <div key={metric.name}>
                  <span>{metric.name}</span>
                  <strong>
                    {Number(metric.value).toFixed(4)}
                    {metric.unit ? ` ${metric.unit}` : ""}
                  </strong>
                </div>
              ))}
            </div>

            <h4>Findings</h4>
            {report.findings.map((finding) => (
              <p key={finding}>{finding}</p>
            ))}

            {report.workflow && (
              <div className="grounding-badge">
                {report.workflow.evidence_count} retrieved evidence chunks
              </div>
            )}
          </section>

          <section className="panel">
            <span className="eyebrow">Primary-source evidence</span>
            <h3>Research Sources</h3>

            {report.evidence.length === 0 ? (
              <p>No retrieved evidence was returned.</p>
            ) : (
              report.evidence.map((item) => (
                <article
                  className="evidence"
                  key={`${item.title}-${item.source}`}
                >
                  <strong>{item.title}</strong>
                  <span>{item.source}</span>
                  <p>{item.content}</p>
                  <small>
                    Relevance: {Number(item.relevance).toFixed(3)}
                  </small>
                </article>
              ))
            )}

            <div className="grounding-badge">
              {report.grounding.has_primary_source_evidence
                ? "Primary-source evidence present"
                : "No primary-source evidence"}
            </div>

            {report.workflow?.sources.length ? (
              <div className="source-list">
                <h4>Sources</h4>
                {report.workflow.sources.map((source) => (
                  <div key={source}>{source}</div>
                ))}
              </div>
            ) : null}
          </section>
        </div>
      )}
    </>
  )
}

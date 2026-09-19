import { MetricCard } from "../components/MetricCard";

const metrics = [
  {
    label: "Portfolio Value",
    value: "£100,000",
    change: "+4.82%",
    description: "Current simulated capital",
  },
  {
    label: "Annualized Return",
    value: "12.40%",
    change: "+1.84%",
    description: "Based on selected period",
  },
  {
    label: "Volatility",
    value: "14.72%",
    description: "Annualized portfolio risk",
  },
  {
    label: "Sharpe Ratio",
    value: "0.84",
    description: "Risk-adjusted return",
  },
];

export function Dashboard() {
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

      <div className="metric-grid">
        {metrics.map((metric) => (
          <MetricCard key={metric.label} {...metric} />
        ))}
      </div>

      <div className="dashboard-grid">
        <div className="panel performance-panel">
          <div className="panel-header">
            <div>
              <h3>Portfolio Performance</h3>
              <p>Simulated cumulative portfolio value</p>
            </div>
            <select defaultValue="1Y" aria-label="Performance period">
              <option>1M</option>
              <option>3M</option>
              <option>6M</option>
              <option>1Y</option>
            </select>
          </div>

          <div className="chart-placeholder">
            <div className="chart-line" />
            <span>Performance chart</span>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Portfolio Allocation</h3>
              <p>Current target weights</p>
            </div>
          </div>

          <div className="allocation-list">
            {[
              ["Equities", "55%"],
              ["Fixed Income", "25%"],
              ["Alternatives", "12%"],
              ["Cash", "8%"],
            ].map(([name, weight]) => (
              <div className="allocation-row" key={name}>
                <span>{name}</span>
                <strong>{weight}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="panel recent-panel">
        <div className="panel-header">
          <div>
            <h3>Research & Analytics</h3>
            <p>Available quantitative modules</p>
          </div>
        </div>

        <div className="module-grid">
          <div className="module-card">
            <strong>Classical Optimization</strong>
            <span>Minimum volatility, maximum Sharpe and risk parity.</span>
          </div>
          <div className="module-card">
            <strong>Risk Engine</strong>
            <span>VaR, expected shortfall, drawdown and contribution risk.</span>
          </div>
          <div className="module-card">
            <strong>Backtesting</strong>
            <span>Historical portfolio simulation with transaction costs.</span>
          </div>
        </div>
      </div>
    </section>
  );
}

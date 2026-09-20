import { useEffect, useMemo, useState } from "react";
import { api } from "../services/api";
import type { FrontierPoint } from "../types/frontier";
import type { OptimizationResponse } from "../types/api";

function formatPercent(value: number) {
  return `${(value * 100).toFixed(2)}%`;
}

function formatRatio(value: number) {
  return Number.isFinite(value) ? value.toFixed(2) : "N/A";
}

function FrontierChart({ points }: { points: FrontierPoint[] }) {
  const width = 760;
  const height = 340;
  const padding = 52;

  const minX = Math.min(...points.map((point) => point.volatility));
  const maxX = Math.max(...points.map((point) => point.volatility));
  const minY = Math.min(...points.map((point) => point.expected_return));
  const maxY = Math.max(...points.map((point) => point.expected_return));

  const xRange = maxX - minX || 1;
  const yRange = maxY - minY || 1;

  const projectX = (value: number) =>
    padding + ((value - minX) / xRange) * (width - padding * 2);

  const projectY = (value: number) =>
    height - padding - ((value - minY) / yRange) * (height - padding * 2);

  const path = points
    .map((point, index) => {
      const command = index === 0 ? "M" : "L";
      return `${command} ${projectX(point.volatility)} ${projectY(point.expected_return)}`;
    })
    .join(" ");

  return (
    <div className="frontier-chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Efficient frontier">
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

        <path d={path} className="frontier-line" fill="none" />

        {points.map((point, index) => (
          <circle
            key={`${point.volatility}-${point.expected_return}-${index}`}
            cx={projectX(point.volatility)}
            cy={projectY(point.expected_return)}
            r="4"
            className="frontier-point"
          />
        ))}

        <text x={width / 2} y={height - 12} textAnchor="middle">
          Volatility
        </text>

        <text
          x="15"
          y={height / 2}
          textAnchor="middle"
          transform={`rotate(-90 15 ${height / 2})`}
        >
          Expected Return
        </text>
      </svg>
    </div>
  );
}

function MethodRow({
  name,
  result,
}: {
  name: string;
  result: {
    expected_return: number;
    volatility: number;
    sharpe_ratio: number;
  };
}) {
  return (
    <div className="frontier-method-row">
      <strong>{name}</strong>
      <span>{formatPercent(result.expected_return)}</span>
      <span>{formatPercent(result.volatility)}</span>
      <span>{formatRatio(result.sharpe_ratio)}</span>
    </div>
  );
}

export function FrontierDashboard() {
  const [points, setPoints] = useState<FrontierPoint[]>([]);
  const [optimization, setOptimization] =
    useState<OptimizationResponse | null>(null);
  const [assets, setAssets] = useState<string[]>([]);
  const [observations, setObservations] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const summary = useMemo(() => {
    if (!points.length) {
      return null;
    }

    const minimumVolatility = points.reduce((best, point) =>
      point.volatility < best.volatility ? point : best,
    );

    const maximumSharpe = points.reduce((best, point) =>
      (point.expected_return / point.volatility) > (best.expected_return / best.volatility) ? point : best,
    );

    return { minimumVolatility, maximumSharpe };
  }, [points]);

  useEffect(() => {
    const loadFrontier = async () => {
      setLoading(true);
      setError(null);

      try {
        const portfolio = await api.getPortfolioData({
          assets: ["SPY", "QQQ", "TLT"],
          start_date: "2024-01-01",
          end_date: "2024-12-31",
        });

        const payload = {
          assets: portfolio.assets,
          expected_returns: portfolio.expected_returns,
          covariance: portfolio.covariance,
          risk_free_rate: 0.02,
          min_weight: 0,
          max_weight: 1,
        };

        const [frontier, optimized] = await Promise.all([
          api.calculateFrontier(payload),
          api.optimizePortfolio(payload),
        ]);

        setAssets(portfolio.assets);
        setObservations(portfolio.observations);
        setPoints(frontier);
        setOptimization(optimized);
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load efficient frontier.",
        );
      } finally {
        setLoading(false);
      }
    };

    void loadFrontier();
  }, []);

  return (
    <section>
      <div className="page-heading">
        <div>
          <h2>Efficient Frontier</h2>
          <p>
            Risk-return trade-offs calculated from historical market data and
            the portfolio optimization engine.
          </p>
        </div>
      </div>

      {loading && <div className="panel loading-panel">Calculating frontier...</div>}

      {error && <div className="form-error">{error}</div>}

      {!loading && !error && summary && optimization && (
        <>
          <div className="frontier-overview">
            <div className="panel">
              <span>Assets</span>
              <strong>{assets.join(" / ")}</strong>
            </div>
            <div className="panel">
              <span>Observations</span>
              <strong>{observations}</strong>
            </div>
            <div className="panel">
              <span>Frontier Points</span>
              <strong>{points.length}</strong>
            </div>
          </div>

          <div className="panel frontier-panel">
            <div className="panel-header">
              <div>
                <h3>Risk / Return Frontier</h3>
                <p>20 target-return portfolios generated by the backend.</p>
              </div>
            </div>

            <FrontierChart points={points} />

            <div className="frontier-highlights">
              <div>
                <span>Minimum volatility point</span>
                <strong>
                  {formatPercent(summary.minimumVolatility.volatility)}
                </strong>
              </div>
              <div>
                <span>Maximum Sharpe point</span>
                <strong>
                  {formatRatio(summary.maximumSharpe.expected_return / summary.maximumSharpe.volatility)}
                </strong>
              </div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Portfolio Strategy Comparison</h3>
                <p>Same historical inputs and constraints across methods.</p>
              </div>
            </div>

            <div className="frontier-table">
              <div className="frontier-method-row frontier-table-header">
                <strong>Strategy</strong>
                <span>Return</span>
                <span>Volatility</span>
                <span>Sharpe</span>
              </div>

              <MethodRow name="Equal Weight" result={optimization.equal_weight ?? optimization.results[0]!} />
              <MethodRow
                name="Minimum Volatility"
                result={optimization.minimum_volatility ?? optimization.results[1]!}
              />
              <MethodRow
                name="Maximum Sharpe"
                result={optimization.maximum_sharpe ?? optimization.results[2]!}
              />
              <MethodRow name="Risk Parity" result={optimization.risk_parity ?? optimization.results[3]!} />
            </div>
          </div>
        </>
      )}
    </section>
  );
}

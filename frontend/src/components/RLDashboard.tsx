import { useEffect, useState } from "react";

import { evaluateRL } from "../services/api";
import type { RLResponse } from "../types/rl";

const assets = ["SPY", "QQQ", "TLT"];

const returns = [
  [0.010, 0.020, 0.015],
  [0.020, 0.010, 0.012],
  [0.000, 0.030, 0.010],
  [0.015, 0.010, 0.014],
  [0.012, 0.018, 0.011],
  [0.008, 0.012, 0.016],
  [0.010, 0.015, 0.013],
  [0.014, 0.011, 0.012],
  [0.009, 0.020, 0.014],
  [0.013, 0.016, 0.010],
];

const actions = [
  [1 / 3, 1 / 3, 1 / 3],
  [0.6, 0.2, 0.2],
  [0.2, 0.6, 0.2],
];

function percent(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

function money(value: number): string {
  return `£${value.toLocaleString("en-GB", {
    maximumFractionDigits: 0,
  })}`;
}

export default function RLDashboard() {
  const [result, setResult] = useState<RLResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    evaluateRL({
      returns,
      assets,
      actions,
      initial_capital: 100000,
      transaction_cost_bps: 5,
      risk_free_rate: 0,
    })
      .then(setResult)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <section className="page-section">
        <div className="page-header">
          <div>
            <span className="eyebrow">Reinforcement Learning</span>
            <h1>RL Portfolio Management</h1>
          </div>
        </div>
        <div className="panel">
          <p>Running chronological training and evaluation...</p>
        </div>
      </section>
    );
  }

  if (error || !result) {
    return (
      <section className="page-section">
        <div className="page-header">
          <div>
            <span className="eyebrow">Reinforcement Learning</span>
            <h1>RL Portfolio Management</h1>
          </div>
        </div>
        <div className="panel">
          <p className="error-text">{error ?? "Unable to load RL results."}</p>
        </div>
      </section>
    );
  }

  const selectedWeights = actions[result.selected_action] ?? [];

  return (
    <section className="page-section">
      <div className="page-header">
        <div>
          <span className="eyebrow">Reinforcement Learning</span>
          <h1>RL Portfolio Management</h1>
          <p>
            Chronological training, validation and out-of-sample test evaluation.
          </p>
        </div>
      </div>

      <div className="metric-grid">
        <div className="metric-card">
          <span>Selected Policy</span>
          <strong>Action {result.selected_action}</strong>
        </div>

        <div className="metric-card">
          <span>Validation Return</span>
          <strong>{percent(result.validation.cumulative_return)}</strong>
        </div>

        <div className="metric-card">
          <span>Q-Learning Test Return</span>
          <strong>{percent(result.q_learning_test.cumulative_return)}</strong>
        </div>

        <div className="metric-card">
          <span>Q-Learning Final Value</span>
          <strong>{money(result.q_learning_test.final_value)}</strong>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Learned Policy</span>
              <h2>Q-Learning Evaluation</h2>
            </div>
          </div>

          <div className="detail-list">
            <div>
              <span>Validation return</span>
              <strong>
                {percent(result.q_learning_validation.cumulative_return)}
              </strong>
            </div>
            <div>
              <span>Test return</span>
              <strong>
                {percent(result.q_learning_test.cumulative_return)}
              </strong>
            </div>
            <div>
              <span>Test final value</span>
              <strong>{money(result.q_learning_test.final_value)}</strong>
            </div>
            <div>
              <span>Test turnover</span>
              <strong>
                {result.q_learning_test.total_turnover.toFixed(4)}
              </strong>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Baseline Policy</span>
              <h2>Fixed-Action Test</h2>
            </div>
          </div>

          <div className="detail-list">
            <div>
              <span>Final value</span>
              <strong>{money(result.test.final_value)}</strong>
            </div>
            <div>
              <span>Cumulative return</span>
              <strong>{percent(result.test.cumulative_return)}</strong>
            </div>
            <div>
              <span>Average reward</span>
              <strong>{result.test.average_reward.toFixed(6)}</strong>
            </div>
            <div>
              <span>Total turnover</span>
              <strong>{result.test.total_turnover.toFixed(4)}</strong>
            </div>
          </div>
        </div>
      </div>

      <div className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Learned Policy</span>
              <h2>Q-Learning Evaluation</h2>
            </div>
          </div>

          <div className="detail-list">
            <div>
              <span>Validation return</span>
              <strong>
                {percent(result.q_learning_validation.cumulative_return)}
              </strong>
            </div>
            <div>
              <span>Test return</span>
              <strong>
                {percent(result.q_learning_test.cumulative_return)}
              </strong>
            </div>
            <div>
              <span>Test final value</span>
              <strong>{money(result.q_learning_test.final_value)}</strong>
            </div>
            <div>
              <span>Test turnover</span>
              <strong>
                {result.q_learning_test.total_turnover.toFixed(4)}
              </strong>
            </div>
          </div>
        </div>

        <div className="panel">
        <div className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Policy</span>
              <h2>Selected Portfolio</h2>
            </div>
          </div>

          <div className="weight-list">
            {assets.map((asset, index) => (
              <div className="weight-row" key={asset}>
                <span>{asset}</span>
                <strong>{percent(selectedWeights[index] ?? 0)}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">Baseline Policy</span>
              <h2>Fixed-Action Test</h2>
            </div>
          </div>

          <div className="detail-list">
            <div>
              <span>Final value</span>
              <strong>{money(result.test.final_value)}</strong>
            </div>
            <div>
              <span>Cumulative return</span>
              <strong>{percent(result.test.cumulative_return)}</strong>
            </div>
            <div>
              <span>Average reward</span>
              <strong>{result.test.average_reward.toFixed(6)}</strong>
            </div>
            <div>
              <span>Total turnover</span>
              <strong>{result.test.total_turnover.toFixed(4)}</strong>
            </div>
          </div>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Benchmark Analysis</span>
            <h2>Strategy Comparison</h2>
          </div>
        </div>

        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Strategy</th>
                <th>Final Value</th>
                <th>Cumulative Return</th>
                <th>Average Reward</th>
                <th>Turnover</th>
              </tr>
            </thead>
            <tbody>
              {result.strategies.map((strategy) => (
                <tr key={strategy.name}>
                  <td>{strategy.name}</td>
                  <td>{money(strategy.final_value)}</td>
                  <td>{percent(strategy.cumulative_return)}</td>
                  <td>{strategy.average_reward.toFixed(6)}</td>
                  <td>{strategy.total_turnover.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div>
            <span className="eyebrow">Training</span>
            <h2>Action Performance</h2>
          </div>
        </div>

        <div className="training-grid">
          {Object.entries(result.training_rewards).map(([action, reward]) => (
            <div className="training-card" key={action}>
              <span>Action {action}</span>
              <strong>{percent(reward)}</strong>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

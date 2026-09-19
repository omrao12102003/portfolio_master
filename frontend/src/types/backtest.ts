export interface BacktestRequest {
  assets: string[];
  dates: string[];
  prices: number[][];
  weights: number[];
  initial_capital: number;
  transaction_cost_bps: number;
  rebalance_frequency: "daily" | "weekly" | "monthly";
}

export interface BacktestSummary {
  initial_capital: number;
  final_capital: number;
  cumulative_return: number;
  annualized_return: number;
  annualized_volatility: number;
  maximum_drawdown: number;
  total_turnover: number;
  total_transaction_cost: number;
}

export interface BacktestResponse {
  summary: BacktestSummary;
  equity_curve: Record<string, number>;
  portfolio_returns: Record<string, number>;
}

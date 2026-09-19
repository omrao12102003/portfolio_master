export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface ReturnsResponse {
  total_return: number;
  annualized_return: number;
  annualized_volatility: number;
  downside_volatility: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  maximum_drawdown: number;
}

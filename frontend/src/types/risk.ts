export interface RiskRequest {
  returns: number[];
  benchmark_returns?: number[];
  risk_free_rate?: number;
}

export interface RiskResponse {
  volatility: number;
  downside_volatility: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  maximum_drawdown: number;
  historical_var_95: number;
  parametric_var_95: number;
  expected_shortfall_95: number;
  beta?: number;
  tracking_error?: number;
}

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

export interface PortfolioRequest {
  assets: string[];
  expected_returns: number[];
  covariance: number[][];
  risk_free_rate?: number;
  min_weight?: number;
  max_weight?: number;
}

export interface OptimizationResult {
  weights: Record<string, number>;
  expected_return: number;
  volatility: number;
  sharpe_ratio: number;
}

export interface OptimizationResponse {
  equal_weight: OptimizationResult;
  minimum_volatility: OptimizationResult;
  maximum_sharpe: OptimizationResult;
  risk_parity: OptimizationResult;
}


export interface PortfolioDataRequest {
  assets: string[];
  start_date: string;
  end_date: string;
}

export interface PortfolioDataResponse {
  assets: string[];
  expected_returns: number[];
  covariance: number[][];
  portfolio_returns: number[];
  historical_dates: string[];
  historical_prices: number[][];
  start_date: string;
  end_date: string;
  observations: number;
  source: string;
}

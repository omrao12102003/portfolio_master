export interface FrontierPoint {
  target_return: number;
  expected_return: number;
  volatility: number;
}

export interface FrontierRequest {
  assets: string[];
  expected_returns: number[];
  covariance: number[][];
  risk_free_rate?: number;
  min_weight?: number;
  max_weight?: number;
}

export interface FrontierResponse {
  points: FrontierPoint[];
}

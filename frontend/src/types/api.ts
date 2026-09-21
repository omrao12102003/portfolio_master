export interface HealthResponse {
  status: string
  service?: string
  version?: string
}

export interface ReturnsResponse {
  cumulative_return: number
  annualized_return: number
  annualized_volatility: number
  sharpe_ratio: number
  downside_volatility?: number
  sortino_ratio?: number
  maximum_drawdown?: number
}

export interface PortfolioRequest {
  assets: string[]
  expected_returns: number[]
  covariance: number[][]
  risk_free_rate: number
  min_weight: number
  max_weight: number
}

export interface OptimizationResult {
  method: string
  weights: number[]
  expected_return: number
  volatility: number
  sharpe_ratio: number
}

export interface OptimizationResponse {
  results: OptimizationResult[]
  equal_weight: OptimizationResult
  minimum_volatility: OptimizationResult
  maximum_sharpe: OptimizationResult
  risk_parity: OptimizationResult
}

export interface RiskResponse {
  volatility: number
  downside_volatility: number
  sharpe_ratio: number
  sortino_ratio: number
  maximum_drawdown: number
  historical_var_95: number
  parametric_var_95: number
  expected_shortfall_95: number
}

export interface BacktestResponse {
  initial_capital: number
  final_capital: number
  cumulative_return: number
  annualized_return: number
  annualized_volatility: number
  maximum_drawdown: number
  total_turnover: number
  total_transaction_cost: number
}

export interface GroundedReportResponse {
  report_type: string
  title: string
  summary: string
  findings: string[]
  metrics: {
    name: string
    value: number
    unit?: string
  }[]
  evidence: {
    title: string
    source: string
    content: string
    relevance: number
  }[]
  limitations: string[]
  markdown: string
  grounding: {
    evidence_count: number
    sources: string[]
    has_primary_source_evidence: boolean
    quantitative_metric_count: number
  }
}

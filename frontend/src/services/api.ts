import type {
  BacktestResponse,
  GroundedReportResponse,
  HealthResponse,
  OptimizationResponse,
  PortfolioRequest,
  ReturnsResponse,
  RiskResponse,
} from "../types/api"

const API_BASE = (
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/$/, "")

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  })

  if (!response.ok) {
    const detail = await response.text()
    throw new Error(detail || `Request failed: ${response.status}`)
  }

  return response.json() as Promise<T>
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/api/health")
}

export function getReadiness(): Promise<{
  status: string
  environment: string
  database_configured: boolean
  cors_configured: boolean
}> {
  return request("/api/readiness")
}

export function calculateReturns(
  returns: number[],
  riskFreeRate = 0.02,
): Promise<ReturnsResponse> {
  return request("/quant/returns", {
    method: "POST",
    body: JSON.stringify({
      returns,
      risk_free_rate: riskFreeRate,
    }),
  })
}

export async function optimizePortfolio(
  payload: PortfolioRequest,
): Promise<OptimizationResponse> {
  const response = await request<Record<string, Record<string, number>>>(
    "/quant/optimize",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  )

  const methods = [
    ["equal_weight", "Equal Weight"],
    ["minimum_volatility", "Minimum Volatility"],
    ["maximum_sharpe", "Maximum Sharpe"],
    ["risk_parity", "Risk Parity"],
  ] as const

  const buildResult = (
    key: (typeof methods)[number][0],
    method: string,
  ) => {
    const weightsByAsset = response[key] ?? {}
    const weights = payload.assets.map(
      (asset) => weightsByAsset[asset] ?? 0,
    )

    const expectedReturn = weights.reduce(
      (total, weight, index) =>
        total + weight * (payload.expected_returns[index] ?? 0),
      0,
    )

    const variance = weights.reduce(
      (total, weight, row) =>
        total +
        weight *
          weights.reduce(
            (inner, otherWeight, column) =>
              inner +
              otherWeight *
                (payload.covariance[row]?.[column] ?? 0),
            0,
          ),
        0,
    )

    const volatility = Math.sqrt(Math.max(variance, 0))
    const sharpeRatio =
      volatility > 0
        ? (expectedReturn - payload.risk_free_rate) / volatility
        : 0

    return {
      method,
      weights,
      expected_return: expectedReturn,
      volatility,
      sharpe_ratio: sharpeRatio,
    }
  }

  const results = methods.map(([key, method]) =>
    buildResult(key, method),
  )

  return {
    results,
    equal_weight: results[0]!,
    minimum_volatility: results[1]!,
    maximum_sharpe: results[2]!,
    risk_parity: results[3]!,
  }
}

export function calculateRisk(
  returns: number[],
  riskFreeRate = 0.02,
): Promise<RiskResponse> {
  return request("/quant/risk", {
    method: "POST",
    body: JSON.stringify({
      returns,
      risk_free_rate: riskFreeRate,
    }),
  })
}

export function runBacktest(payload: {
  prices: number[][]
  target_weights: number[]
  initial_capital: number
  transaction_cost_bps: number
  rebalance_frequency: string
}): Promise<BacktestResponse> {
  return request("/quant/backtest", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export function createGroundedReport(payload: {
  title: string
  question: string
  summary: string
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
  methodology?: string[]
  limitations?: string[]
}): Promise<GroundedReportResponse> {
  return request("/research/reports/grounded", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export async function getPortfolioData(payload: {
  assets: string[]
  start_date: string
  end_date: string
}): Promise<{
  assets: string[]
  start_date: string
  end_date: string
  observations: number
  dates: string[]
  historical_dates: string[]
  historical_prices: number[][]
  expected_returns: number[]
  covariance: number[][]
  returns: number[][]
  portfolio_returns: number[]
}> {
  return request("/quant/portfolio-data", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export async function calculateFrontier(
  payload: PortfolioRequest,
): Promise<{
  target_return: number
  expected_return: number
  volatility: number
  sharpe_ratio: number
  weights: number[]
}[]> {
  const response = await request<{
    points: {
      expected_return: number
      volatility: number
      sharpe_ratio: number
      weights: number[]
    }[]
  }>("/quant/frontier", {
    method: "POST",
    body: JSON.stringify(payload),
  })

  return response.points.map((point) => ({
    ...point,
    target_return: point.expected_return,
  }))
}

export async function evaluateRL(payload: {
  returns: number[][]
  assets: string[]
  actions: number[][]
  initial_capital: number
  transaction_cost_bps: number
  risk_free_rate: number
}): Promise<import("../types/rl").RLResponse> {
  return request("/rl/evaluate", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export async function createInvestmentReport(payload: {
  title: string
  question: string
  summary: string
  metrics: {
    name: string
    value: number
    unit?: string
  }[]
  ticker?: string
  company?: string
  published_before?: string
  section?: string
  findings?: string[]
  methodology?: string[]
  limitations?: string[]
  top_k?: number
}): Promise<GroundedReportResponse & {
  workflow?: {
    evidence_count: number
    sources: string[]
  }
}> {
  return request("/research/workflow/report", {
    method: "POST",
    body: JSON.stringify(payload),
  })
}

export const api = {
  health: getHealth,
  getHealth,
  getReadiness,
  getPortfolioData,
  calculateReturns,
  optimizePortfolio,
  calculateRisk,
  calculateFrontier,
  runBacktest: async (payload: {
    assets: string[]
    dates: string[]
    prices: number[][]
    weights: number[]
    initial_capital: number
    transaction_cost_bps: number
    rebalance_frequency: string
  }): Promise<import("../types/backtest").BacktestResponse> => {
    return request("/quant/backtest", {
      method: "POST",
      body: JSON.stringify(payload),
    })
  },
  createGroundedReport,
  createInvestmentReport,
}

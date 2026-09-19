import type { HealthResponse, OptimizationResponse, PortfolioRequest, ReturnsResponse } from "../types/api";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>("/api/health"),

  calculateReturns: (returns: number[]) =>
    request<ReturnsResponse>("/quant/returns", {
      method: "POST",
      body: JSON.stringify({ returns }),
    }),

  optimizePortfolio: (portfolio: PortfolioRequest) =>
    request<OptimizationResponse>("/quant/optimize", {
      method: "POST",
      body: JSON.stringify(portfolio),
    }),
};

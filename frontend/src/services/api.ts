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
  health: () => request<{
    status: string;
    service: string;
    version: string;
  }>("/api/health"),

  calculateReturns: (returns: number[]) =>
    request("/quant/returns", {
      method: "POST",
      body: JSON.stringify({ returns }),
    }),
};

# Development Roadmap

Portfolio Master is built in named stages. A stage is complete when its code, tests, and
documentation exist — not when a folder name exists.

Do not start the next stage until the project owner confirms the current stage.

## Stage 1 — Architecture and development environment

| Slice | Scope | Status |
| --- | --- | --- |
| 1A | Architecture docs, package boundaries, reproducible Python project, FastAPI foundation, Vite shell, Compose Postgres + pgvector, README | This slice |
| Later 1.x | Only if the owner requests environment polish (editor settings, extra scripts) | Not started |

Stage 1 does **not** include market data, optimization, risk formulas, backtests, RL, RAG,
or a dashboard.

## Remaining product stages

| Stage | Name | Intent |
| --- | --- | --- |
| 2 | Market-data ingestion and validation | Download/import, cleaning, alignment, no hard-coded single dataset |
| 3 | Return and statistical analytics | Returns, moments, correlation/covariance primitives |
| 4 | Risk management engine | Independent risk metrics (vol, drawdown, VaR, ES, contributions) |
| 5 | Classical portfolio optimization | Equal weight, min vol, max Sharpe, risk parity, constraints |
| 6 | Efficient frontier and portfolio analytics | Frontier, allocation and risk visuals via API |
| 7 | Historical backtesting | Costs, rebalancing, chronological engine |
| 8 | FastAPI domain APIs | Stable `/api` resources for the engines above |
| 9 | Professional React dashboard | Product UI, still calculation-free on the client |
| 10 | Real-time portfolio interaction | Recalculate on weight edits; WebSockets only if justified |
| 11 | RL environment | Sequential state/action/reward, discrete baseline first |
| 12 | RL agent | Simple baseline before PPO/SAC |
| 13 | RL train / validation / test | Chronological splits, no look-ahead |
| 14 | Classical vs RL comparison | Empirical, out-of-sample, no assumed winner |
| 15 | Financial-document ingestion | Filings and reports with metadata |
| 16 | pgvector persistence | Embeddings stored in PostgreSQL |
| 17 | RAG pipeline | Chunk, retrieve, optional rerank, citations |
| 18 | Investment research copilot | Explanation only |
| 19 | Quant + RAG integration | Dual-channel answers |
| 20 | Reports and export | Downloadable research artefacts |
| 21 | Testing and validation | Including leakage tests |
| 22 | Performance | Caching, vectorization, avoid redundant I/O |
| 23 | Dockerization | Full application compose |
| 24 | Deployment preparation | Config, health, no premature production claims |
| 25 | Documentation | Methodology, limitations, reproducibility |
| 26 | GitHub cleanup | No secrets, no artefacts |
| 27 | Portfolio presentation | Honest walkthrough of the system |

## Rules for moving forward

1. Introduce libraries in the stage that first needs them (NumPy/Pandas in Stage 2–3, CVXPY
   in Stage 5, RL libraries in Stage 11–12, embedding/LLM SDKs in Stage 16–18).
2. Add tests in the same stage as the code, especially for leakage and constraints.
3. Keep the LLM and RAG out of the calculation path.
4. Prefer one Ghostty/setup command per major environment change, documented in
   `docs/development/local-setup.md`.

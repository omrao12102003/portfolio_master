# Development Principles

These rules apply to every later stage. They are more important than adding libraries.

## 1. Source of truth

Quantitative numbers come from tested Python in `backend/app`. The LLM may restate them.
It may not originate them.

## 2. Deterministic quantitative engine

Given the same inputs (prices, weights, window, risk-free rate, constraints), `quant`,
`risk`, `optimization`, and `backtest` must return the same outputs. Randomness belongs
only in explicitly seeded simulation or RL training.

## 3. No look-ahead bias

Features, expected-return estimates, covariance, optimizer inputs, RL states, and RAG
document filters for historical experiments may use only information available at that
decision date. Train / validation / test splits are chronological.

Leakage is a failing test, not a documentation footnote.

## 4. Reproducibility

- Pin application dependencies in `backend/pyproject.toml`.
- Configure via environment variables; never commit `.env`.
- Record methodology (windows, costs, constraints) with every optimization and backtest run
  once those modules exist.
- Do not cherry-pick backtest windows in documentation.

## 5. Testing first for financial logic

When a formula is implemented, a unit test must exist for a known numerical example.
API tests do not replace formula tests. Data-leakage tests live in `backend/tests/leakage/`.

## 6. Stage-by-stage development

Do not implement Stage N+1 while Stage N is incomplete unless the owner explicitly
re-scopes. Folder stubs are boundaries, not hidden work.

## 7. Notebook policy

`notebooks/` is for exploration. Production logic lives in `backend/app` and is imported
by tests and the API. Do not copy-paste conflicting versions of Sharpe, VaR, or covariance
between a notebook and the engine.

## 8. Honest research claims

Do not claim that AI predicts the market, that RL beats classical optimization, or that
backtests are live results. State limitations next to results.

## 9. Modular monolith

One API process, one database, one frontend. New infrastructure (queues, extra databases,
Kubernetes) requires a concrete failure of this model.

## 10. Security baseline

No secrets in git. Validate uploads when documents arrive. Do not log credentials.
`.env` is ignored; `.env.example` is the template.

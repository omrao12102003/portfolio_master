# Portfolio Master

A quantitative investment research and portfolio-management platform combining classical
portfolio theory, risk analytics, historical backtesting, reinforcement learning, and
AI-assisted financial-document research.

This repository is `portfolio_master`. The product display name is **Portfolio Master**.

## Project purpose

The long-term system is a professional research workbench, not a toy optimizer and not an
"AI picks stocks" demo.

It is designed for:

- Classical quantitative portfolio construction and risk analysis
- Chronological backtesting with explicit transaction assumptions
- Reinforcement-learning portfolio agents evaluated against classical benchmarks
- Retrieval-augmented research over actual financial documents
- An LLM copilot that explains engine output and retrieved evidence

Target discussion contexts include quantitative research, portfolio analytics, risk,
systematic investing, and Python/AI engineering in finance.

## Current status

**Production-ready prototype — quantitative engine, research platform, and frontend implemented.**

Portfolio Master now contains the core quantitative-finance, portfolio-management, reinforcement-learning, financial-research, and web-application layers.

Validated components include:

- Market-data ingestion and normalization
- Portfolio and return analytics
- Risk analytics and risk attribution
- Classical portfolio optimization
- Efficient frontier generation
- Historical backtesting
- Time-series and factor models
- Derivatives pricing and Greeks
- Fixed-income analytics
- Trading research and walk-forward evaluation
- Reinforcement-learning portfolio management
- SEC financial-document ingestion and chunking
- PostgreSQL + pgvector retrieval
- Semantic and hybrid RAG
- Grounded research reporting
- React/TypeScript portfolio dashboards
- FastAPI quantitative and research APIs
- Production deployment configuration for Render and Vercel

The latest pre-deployment validation passed the backend regression suite, Ruff, frontend lint/build, API health/readiness checks, deterministic quantitative checks, real market-data checks, chronological leakage checks, RL validation, and SEC/RAG historical cutoff validation.

The project is a serious quantitative-finance research prototype, not an institutional trading system. Historical backtests and model outputs are empirical results under stated assumptions and are not guarantees of future performance.

## Final architecture overview

A modular monolith:

1. React / TypeScript UI
2. FastAPI application with a `/api` namespace
3. Deterministic quantitative packages (`quant`, `portfolio`, `risk`, `optimization`, `backtest`)
4. Separate RL package for sequential decisions
5. RAG + LLM packages for retrieval and explanation
6. PostgreSQL + pgvector as the only data store

The LLM is never the source of truth for numbers. RAG never modifies portfolio weights.
Details: [docs/architecture/system-architecture.md](docs/architecture/system-architecture.md)
and [docs/architecture/module-boundaries.md](docs/architecture/module-boundaries.md).

```mermaid
flowchart TB
    ui[Web UI]
    api[FastAPI]
    quant[Quantitative engine]
    rl[RL]
    rag[RAG]
    llm[LLM]
    db[(PostgreSQL + pgvector)]
    ui --> api
    api --> quant
    api --> rl
    api --> rag
    rag --> llm
    quant --> db
    rl --> db
    rag --> db
```

## Technology stack

| Layer | Choice | Role now |
| --- | --- | --- |
| Backend | Python 3.11+, FastAPI, Pydantic, uvicorn | HTTP foundation |
| Config | pydantic-settings, `.env` | Environment-based configuration |
| Frontend | Vite, React, TypeScript | Minimal professional shell |
| Database | PostgreSQL with pgvector image | Infrastructure only; no app schema yet |
| Packaging | pyproject.toml | Backend dependency and packaging source of truth |
| Tests | pytest, pytest-cov, httpx | Health and configuration tests |
| Lint | Ruff | Backend style |

NumPy, Pandas, CVXPY, RL libraries, and LLM/embedding SDKs are intentionally **not**
installed yet.

## Repository structure

```
backend/                 FastAPI application and tests
frontend/                Vite + React + TypeScript shell
docs/                    Architecture and development documentation
data/                    Market-data and sample-data workspace
notebooks/               Exploration only
scripts/                 Reserved for later operational scripts
render.yaml              Render backend deployment configuration
.env.example             Configuration template
```

## Stage roadmap

The project is developed incrementally. See
[docs/development/development-roadmap.md](docs/development/development-roadmap.md).

| Stage | Focus |
| --- | --- |
| 1 | Architecture and environment (current) |
| 2–7 | Data, analytics, risk, optimization, backtesting |
| 8–10 | Domain APIs, dashboard, interactive recalculation |
| 11–14 | RL environment, agent, evaluation vs classical strategies |
| 15–19 | Documents, pgvector, RAG, research copilot |
| 20–27 | Reports, testing, performance, Docker, docs, presentation |

## Local development prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+ with pgvector for local development

Full commands: [docs/development/local-setup.md](docs/development/local-setup.md).

### One-shot backend setup

From the repository root (Ghostty / zsh):

```bash
python3 -m venv backend/.venv && source backend/.venv/bin/activate && python -m pip install --upgrade pip && python -m pip install -e "./backend[dev]" && (test -f .env || cp .env.example .env) && cd backend && python -m pytest
```

## Backend setup

```bash
source backend/.venv/bin/activate
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/api/health
- http://127.0.0.1:8000/docs

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Build check:

```bash
cd frontend && npm run build
```

The frontend provides portfolio, optimization, risk, backtesting, frontier, RL, and research dashboards.

## Database setup

Portfolio Master uses native PostgreSQL with pgvector for local development.

Verify PostgreSQL:

```bash
pg_isready
```

The research vector store uses PostgreSQL with the `vector` extension.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Docker is not required for local or production deployment.

## Testing

From `backend/` with the virtualenv active:

```bash
python -m pytest
python -m pytest --cov=app --cov-report=term-missing
```

From the repository root:

```bash
python -m pytest
```

## Environment configuration

Copy `.env.example` to `.env`. Required to start Postgres via Compose: `POSTGRES_*`.
Application fields have code defaults. Production secrets must be supplied through deployment environment variables.

## Current limitations

- The current SEC corpus contains a limited set of indexed filings

## Development philosophy

Correctness, financial validity, reproducibility, explainability, and tests outrank adding
frameworks. Principles:
[docs/development/development-principles.md](docs/development/development-principles.md).

This project is being developed incrementally. Stage 1 does not contain the quantitative
investment engine yet.

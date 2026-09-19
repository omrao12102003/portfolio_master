# Local Development Setup

Stage 1A is complete when the API starts, tests pass, the frontend builds, and Compose
configuration for PostgreSQL + pgvector is valid. You do not need a populated database.

## Prerequisites

- macOS
- Python 3.11 or newer
- Node.js 20 or newer and npm (for the Vite frontend; not currently assumed to be installed)
- Docker Desktop **optional** until you want PostgreSQL running. Do not install Docker automatically if it is missing.

Do not install Docker automatically if it is missing.

## One-shot backend setup (Ghostty)

This creates a virtual environment, installs the backend with development extras, and runs
tests. Run it from the repository root.

```bash
cd "/Users/ombarot/Desktop/portfolio master" && python3 -m venv backend/.venv && source backend/.venv/bin/activate && python -m pip install --upgrade pip && python -m pip install -e "./backend[dev]" && (test -f .env || cp .env.example .env) && cd backend && python -m pytest
```

## Backend run

From the repository root, with the virtualenv active:

```bash
cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: http://127.0.0.1:8000/health
- API health: http://127.0.0.1:8000/api/health
- OpenAPI: http://127.0.0.1:8000/docs

## Frontend

```bash
cd frontend && npm install && npm run dev
```

Production-style check:

```bash
cd frontend && npm run build
```

## PostgreSQL + pgvector

From the repository root:

```bash
docker compose up -d postgres
```

This starts only the database. The API service is available behind the Compose profile
`api` and is not required for Stage 1A:

```bash
docker compose --profile api up --build
```

Validate Compose syntax without starting containers:

```bash
docker compose config
```

## Tests

Preferred (from `backend/`):

```bash
python -m pytest
```

Coverage:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

From the repository root:

```bash
python -m pytest backend/tests --import-mode=importlib
```

If you use the root `pytest.ini`, run `python -m pytest` from the repository root with
`backend` on `PYTHONPATH` (the ini file sets this).

## Configuration

Copy `.env.example` to `.env` and edit local values. `.env` is gitignored.

See the comments in `.env.example` for required vs optional variables.

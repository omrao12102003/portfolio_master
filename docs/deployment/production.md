# Portfolio Master — Production Deployment

## Architecture

- Frontend: Vercel
- Backend: Render Web Service
- Database: managed PostgreSQL with pgvector
- Vector retrieval: PostgreSQL + pgvector
- Docker: not required

## Backend

Render service:

- Root directory: `backend`
- Build command: `pip install .`
- Start command initializes the schema and starts Uvicorn.

Required environment variables:

- `APP_ENV=production`
- `APP_ENVIRONMENT=production`
- `APP_DEBUG=false`
- `DATABASE_URL=<managed PostgreSQL connection string>`
- `CORS_ORIGINS=<deployed frontend origin>`

## Database

Enable pgvector:

    CREATE EXTENSION IF NOT EXISTS vector;

The application initializes the research vector table automatically.

Index the research corpus after deployment:

    python -m app.research.corpus_cli

Expected corpus:

- AAPL: 116 chunks
- MSFT: 185 chunks
- NVDA: 194 chunks
- Total: 495 chunks

## Frontend

Vercel configuration:

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`

Set:

    VITE_API_BASE_URL=https://YOUR-BACKEND.onrender.com

`frontend/vercel.json` provides the React Router SPA fallback.

## Health checks

- `/health`
- `/api/health`
- `/api/readiness`

## Security

- Never commit `.env`.
- Never expose database credentials to the frontend.
- Restrict `CORS_ORIGINS` to the deployed frontend.
- Keep `APP_DEBUG=false` in production.

from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Quantitative portfolio optimization and AI investment research platform.",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": settings.app_name, "status": "running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}

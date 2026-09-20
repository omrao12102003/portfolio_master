from __future__ import annotations

import os


def get_database_url() -> str:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://localhost/portfolio_master",
    )

    if not database_url.strip():
        raise RuntimeError("DATABASE_URL is not configured.")

    return database_url

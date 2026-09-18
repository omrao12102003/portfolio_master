from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Portfolio Master"
    app_environment: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/portfolio_platform"

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")


settings = Settings()

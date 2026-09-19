from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(examples=["healthy"])


class RootResponse(BaseModel):
    name: str
    version: str
    status: str
    environment: str

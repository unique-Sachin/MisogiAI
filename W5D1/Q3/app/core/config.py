"""Centralized application configuration.

Reads environment variables and provides them as attributes. A single
`settings` instance should be imported across the codebase.
"""
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):  # type: ignore[misc]
    # Pinecone
    pinecone_api_key: str = Field(...)
    pinecone_environment: str = Field(...)
    pinecone_index_name: str = Field("financial-intel-index")
    pinecone_dimension: int = Field(1024)

    # Redis
    redis_url: str = Field("redis://localhost:6379/0")

    # Cache TTLs (seconds)
    ttl_realtime: int = Field(3600)  # 1 hour
    ttl_historical: int = Field(86400)  # 24 hours
    ttl_popular: int = Field(21600)  # 6 hours

    # OpenAI / Chat model
    openai_api_key: Optional[str] = Field(None)
    openai_model: str = Field("gpt-4o-mini")

    # Misc
    allowed_origins: List[str] = Field(["*"])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("allowed_origins", pre=True)
    def _split_origins(cls, v):  # noqa: ANN101, D401, N805
        """Allow comma-separated origins in env variable."""
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings() 
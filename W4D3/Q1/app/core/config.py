from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralised application settings loaded from environment variables."""
    app_name: str = Field(default="MCP Server")
    environment: str = Field(default="development")

    # Database and Discord
    database_url: str = Field(default="sqlite:///./test.db")
    discord_bot_token: str = Field(default="dummy-token")

    # API & security
    api_key_header: str = Field(default="X-API-Key")

    # Rate-limiting (SlowAPI)
    rate_limit_per_minute: int = Field(default=100)
    rate_limit_per_endpoint: int = Field(default=10)

    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "ignore"}


settings = Settings() 
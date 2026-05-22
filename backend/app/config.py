from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AgentForge"
    environment: str = Field(default="development")
    debug: bool = False
    log_level: str = "INFO"

    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agentforge"
    database_echo: bool = False

    redis_url: str = "redis://localhost:6379/0"
    rate_limit_per_minute: int = 10

    jwt_private_key_path: Path = Path("keys/jwt_private.pem")
    jwt_public_key_path: Path = Path("keys/jwt_public.pem")
    jwt_algorithm: str = "RS256"
    access_token_ttl_seconds: int = 60 * 15
    refresh_token_ttl_seconds: int = 60 * 60 * 24 * 7

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-large"

    pinecone_api_key: str = ""
    pinecone_index: str = "agentforge"
    pinecone_namespace_default: str = "default"

    langsmith_api_key: str = ""
    langsmith_project: str = "agentforge"
    langsmith_tracing: bool = False

    serpapi_api_key: str = ""

    max_critic_loops: int = 2
    min_passing_score: int = 7

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

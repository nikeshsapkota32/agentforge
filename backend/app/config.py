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
    # Alternatively, supply the PEM content directly (useful on ephemeral hosts).
    jwt_private_key: str = ""
    jwt_public_key: str = ""
    jwt_algorithm: str = "RS256"
    access_token_ttl_seconds: int = 60 * 15
    refresh_token_ttl_seconds: int = 60 * 60 * 24 * 7

    # LLM provider — OpenAI-compatible.
    # Free options:
    #   openrouter  -> https://openrouter.ai/api/v1  (Llama 3.3 70B :free)
    #   groq        -> https://api.groq.com/openai/v1
    #   cerebras    -> https://api.cerebras.ai/v1
    #   gemini      -> https://generativelanguage.googleapis.com/v1beta/openai/
    # Paid: openai (default)
    llm_provider: str = "openai"
    llm_base_url: str = ""  # blank = use provider preset
    llm_api_key: str = ""  # if blank, falls back to openai_api_key
    llm_model: str = ""  # if blank, picked from provider preset
    openrouter_referer: str = "https://github.com/nikeshsapkota32/agentforge"
    openrouter_title: str = "AgentForge"

    # Legacy / fallback (kept so existing .env files keep working)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-large"

    # Embeddings provider — separate from chat. Optional.
    embeddings_provider: str = "openai"  # "openai" | "disabled"
    embeddings_api_key: str = ""  # falls back to openai_api_key
    embeddings_base_url: str = ""
    embeddings_model: str = ""  # blank = openai_embedding_model

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

    @property
    def resolved_llm_api_key(self) -> str:
        return self.llm_api_key or self.openai_api_key

    @property
    def resolved_llm_base_url(self) -> str | None:
        if self.llm_base_url:
            return self.llm_base_url
        return {
            "openrouter": "https://openrouter.ai/api/v1",
            "groq": "https://api.groq.com/openai/v1",
            "cerebras": "https://api.cerebras.ai/v1",
            "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
        }.get(self.llm_provider)

    @property
    def llm_default_headers(self) -> dict[str, str]:
        if self.llm_provider == "openrouter":
            return {
                "HTTP-Referer": self.openrouter_referer,
                "X-Title": self.openrouter_title,
            }
        return {}

    @property
    def resolved_llm_model(self) -> str:
        if self.llm_model:
            return self.llm_model
        return {
            "openrouter": "meta-llama/llama-3.3-70b-instruct:free",
            "groq": "llama-3.3-70b-versatile",
            "cerebras": "llama-3.3-70b",
            "gemini": "gemini-2.0-flash",
            "openai": self.openai_model,
        }.get(self.llm_provider, self.openai_model)

    @property
    def resolved_embeddings_api_key(self) -> str:
        return self.embeddings_api_key or self.openai_api_key

    @property
    def resolved_embeddings_model(self) -> str:
        return self.embeddings_model or self.openai_embedding_model

    @property
    def embeddings_enabled(self) -> bool:
        return (
            self.embeddings_provider != "disabled"
            and bool(self.resolved_embeddings_api_key)
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

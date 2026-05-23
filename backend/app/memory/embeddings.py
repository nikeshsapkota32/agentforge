from __future__ import annotations

from openai import AsyncOpenAI

from app.config import settings

_client: AsyncOpenAI | None = None


def _client_or_raise() -> AsyncOpenAI:
    global _client
    if not settings.embeddings_enabled:
        raise RuntimeError(
            "Embeddings are disabled. Set OPENAI_API_KEY or EMBEDDINGS_API_KEY to enable."
        )
    if _client is None:
        kwargs: dict = {"api_key": settings.resolved_embeddings_api_key}
        if settings.embeddings_base_url:
            kwargs["base_url"] = settings.embeddings_base_url
        _client = AsyncOpenAI(**kwargs)
    return _client


async def embed(text: str) -> list[float]:
    resp = await _client_or_raise().embeddings.create(
        model=settings.resolved_embeddings_model,
        input=text[:8000],
    )
    return resp.data[0].embedding


async def embed_many(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    resp = await _client_or_raise().embeddings.create(
        model=settings.resolved_embeddings_model,
        input=[t[:8000] for t in texts],
    )
    return [d.embedding for d in resp.data]

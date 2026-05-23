from __future__ import annotations

from openai import AsyncOpenAI

from app.config import settings

_client: AsyncOpenAI | None = None


def _openai() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def embed(text: str) -> list[float]:
    resp = await _openai().embeddings.create(
        model=settings.openai_embedding_model,
        input=text[:8000],
    )
    return resp.data[0].embedding


async def embed_many(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    resp = await _openai().embeddings.create(
        model=settings.openai_embedding_model,
        input=[t[:8000] for t in texts],
    )
    return [d.embedding for d in resp.data]

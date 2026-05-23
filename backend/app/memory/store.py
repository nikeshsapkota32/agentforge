from __future__ import annotations

import asyncio
import uuid
from typing import Any

from app.config import settings
from app.memory.embeddings import embed


class MemoryStore:
    """Thin wrapper around Pinecone serverless. Lazy init so the app starts without keys."""

    def __init__(self) -> None:
        self._index: Any | None = None

    def _get_index(self) -> Any:
        if self._index is not None:
            return self._index
        if not settings.pinecone_api_key:
            raise RuntimeError("PINECONE_API_KEY is not configured")
        from pinecone import Pinecone

        pc = Pinecone(api_key=settings.pinecone_api_key)
        self._index = pc.Index(settings.pinecone_index)
        return self._index

    async def upsert(
        self,
        text: str,
        *,
        metadata: dict[str, Any] | None = None,
        namespace: str | None = None,
    ) -> str:
        vector = await embed(text)
        record_id = uuid.uuid4().hex
        meta = {"text": text[:4000], **(metadata or {})}
        ns = namespace or settings.pinecone_namespace_default
        await asyncio.to_thread(
            lambda: self._get_index().upsert(
                vectors=[{"id": record_id, "values": vector, "metadata": meta}],
                namespace=ns,
            )
        )
        return record_id

    async def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        namespace: str | None = None,
    ) -> list[dict[str, Any]]:
        vector = await embed(query)
        ns = namespace or settings.pinecone_namespace_default
        result = await asyncio.to_thread(
            lambda: self._get_index().query(
                vector=vector,
                top_k=top_k,
                include_metadata=True,
                namespace=ns,
            )
        )
        matches = result.get("matches", []) if isinstance(result, dict) else result.matches
        out = []
        for m in matches:
            md = m.get("metadata") if isinstance(m, dict) else getattr(m, "metadata", {})
            score = m.get("score") if isinstance(m, dict) else getattr(m, "score", 0.0)
            mid = m.get("id") if isinstance(m, dict) else getattr(m, "id", "")
            out.append({"id": mid, "score": score, "metadata": md or {}})
        return out


memory_store = MemoryStore()

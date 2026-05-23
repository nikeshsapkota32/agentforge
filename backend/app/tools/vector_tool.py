from __future__ import annotations

from typing import Any

from app.config import settings
from app.memory.store import memory_store


def _disabled_reason() -> str | None:
    if not settings.pinecone_api_key:
        return "vector memory disabled: PINECONE_API_KEY not configured"
    if not settings.embeddings_enabled:
        return "vector memory disabled: embeddings provider not configured"
    return None


async def vector_search(payload: dict[str, Any]) -> dict[str, Any]:
    reason = _disabled_reason()
    if reason:
        return {"matches": [], "disabled": reason}
    query = str(payload.get("query") or "").strip()
    if not query:
        return {"error": "missing query"}
    top_k = int(payload.get("top_k") or 5)
    namespace = str(payload.get("namespace") or "")
    try:
        matches = await memory_store.search(query, top_k=top_k, namespace=namespace or None)
    except Exception as exc:
        return {"matches": [], "error": str(exc)}
    return {"matches": matches}


async def vector_write(payload: dict[str, Any]) -> dict[str, Any]:
    reason = _disabled_reason()
    if reason:
        return {"disabled": reason}
    text = str(payload.get("text") or "")
    if not text.strip():
        return {"error": "missing text"}
    metadata = payload.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}
    namespace = str(payload.get("namespace") or "")
    try:
        record_id = await memory_store.upsert(
            text, metadata=metadata, namespace=namespace or None
        )
    except Exception as exc:
        return {"error": str(exc)}
    return {"id": record_id}

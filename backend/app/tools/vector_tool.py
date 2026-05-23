from __future__ import annotations

from typing import Any

from app.memory.store import memory_store


async def vector_search(payload: dict[str, Any]) -> dict[str, Any]:
    query = str(payload.get("query") or "").strip()
    if not query:
        return {"error": "missing query"}
    top_k = int(payload.get("top_k") or 5)
    namespace = str(payload.get("namespace") or "")
    matches = await memory_store.search(query, top_k=top_k, namespace=namespace or None)
    return {"matches": matches}


async def vector_write(payload: dict[str, Any]) -> dict[str, Any]:
    text = str(payload.get("text") or "")
    if not text.strip():
        return {"error": "missing text"}
    metadata = payload.get("metadata") or {}
    if not isinstance(metadata, dict):
        metadata = {}
    namespace = str(payload.get("namespace") or "")
    record_id = await memory_store.upsert(text, metadata=metadata, namespace=namespace or None)
    return {"id": record_id}

from __future__ import annotations

import asyncio
from typing import Any

import wikipediaapi

_WIKI = wikipediaapi.Wikipedia(user_agent="AgentForge/0.1", language="en")


def _lookup_sync(title: str, max_chars: int) -> dict[str, Any]:
    page = _WIKI.page(title)
    if not page.exists():
        return {"found": False, "title": title}
    return {
        "found": True,
        "title": page.title,
        "url": page.fullurl,
        "summary": page.summary[:max_chars],
    }


async def wikipedia_lookup(payload: dict[str, Any]) -> dict[str, Any]:
    title = str(payload.get("title") or payload.get("query") or "").strip()
    if not title:
        return {"error": "missing title"}
    max_chars = int(payload.get("max_chars") or 4000)
    return await asyncio.to_thread(_lookup_sync, title, max_chars)

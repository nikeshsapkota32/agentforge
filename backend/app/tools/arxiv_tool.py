from __future__ import annotations

import asyncio
from typing import Any

import arxiv


def _search_sync(query: str, max_results: int) -> dict[str, Any]:
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    out = []
    for paper in arxiv.Client().results(search):
        out.append(
            {
                "title": paper.title,
                "authors": [a.name for a in paper.authors],
                "published": paper.published.isoformat() if paper.published else None,
                "url": paper.entry_id,
                "summary": paper.summary[:1200],
            }
        )
    return {"results": out}


async def arxiv_search(payload: dict[str, Any]) -> dict[str, Any]:
    query = str(payload.get("query") or "").strip()
    if not query:
        return {"error": "missing query"}
    max_results = int(payload.get("max_results") or 5)
    return await asyncio.to_thread(_search_sync, query, max_results)

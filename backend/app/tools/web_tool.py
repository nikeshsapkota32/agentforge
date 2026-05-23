from __future__ import annotations

from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.config import settings

_USER_AGENT = "AgentForge/0.1 (+https://github.com/nikeshsapkota32/agentforge)"
_TIMEOUT = httpx.Timeout(15.0)


async def web_search(payload: dict[str, Any]) -> dict[str, Any]:
    query = str(payload.get("query") or "").strip()
    if not query:
        return {"results": [], "error": "missing query"}
    top_k = int(payload.get("top_k") or 5)

    if settings.serpapi_api_key:
        return await _serpapi(query, top_k)
    return await _duckduckgo(query, top_k)


async def _serpapi(query: str, top_k: int) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=_TIMEOUT, headers={"User-Agent": _USER_AGENT}) as c:
        r = await c.get(
            "https://serpapi.com/search.json",
            params={"q": query, "api_key": settings.serpapi_api_key, "num": top_k},
        )
        r.raise_for_status()
        data = r.json()
    out = []
    for item in (data.get("organic_results") or [])[:top_k]:
        out.append(
            {
                "title": item.get("title"),
                "url": item.get("link"),
                "snippet": item.get("snippet"),
            }
        )
    return {"results": out}


async def _duckduckgo(query: str, top_k: int) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=_TIMEOUT, headers={"User-Agent": _USER_AGENT}) as c:
        r = await c.get("https://duckduckgo.com/html/", params={"q": query})
        r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for a in soup.select("a.result__a")[:top_k]:
        url = a.get("href")
        snippet_el = a.find_parent("div", class_="result__body")
        snippet = ""
        if snippet_el is not None:
            sn = snippet_el.select_one(".result__snippet")
            snippet = sn.get_text(strip=True) if sn else ""
        out.append({"title": a.get_text(strip=True), "url": url, "snippet": snippet})
    return {"results": out}


async def web_fetch(payload: dict[str, Any]) -> dict[str, Any]:
    url = str(payload.get("url") or "").strip()
    if not url.startswith(("http://", "https://")):
        return {"error": "url must be http(s)"}
    max_chars = int(payload.get("max_chars") or 8000)

    async with httpx.AsyncClient(timeout=_TIMEOUT, headers={"User-Agent": _USER_AGENT}) as c:
        r = await c.get(url, follow_redirects=True)
        r.raise_for_status()
        content_type = r.headers.get("content-type", "")
        text = r.text

    if "html" in content_type.lower():
        soup = BeautifulSoup(text, "html.parser")
        for el in soup(["script", "style", "noscript"]):
            el.decompose()
        text = soup.get_text(separator="\n", strip=True)

    return {
        "url": url,
        "content_type": content_type,
        "text": text[:max_chars],
        "truncated": len(text) > max_chars,
    }

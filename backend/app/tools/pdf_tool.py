from __future__ import annotations

import asyncio
from io import BytesIO
from typing import Any

import httpx
from pypdf import PdfReader


async def _fetch(url: str) -> bytes:
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.get(url, follow_redirects=True)
        r.raise_for_status()
        return r.content


def _extract(data: bytes, max_pages: int, max_chars: int) -> dict[str, Any]:
    reader = PdfReader(BytesIO(data))
    chunks: list[str] = []
    pages = min(len(reader.pages), max_pages)
    for i in range(pages):
        chunks.append(reader.pages[i].extract_text() or "")
    text = "\n\n".join(chunks)
    return {
        "pages_total": len(reader.pages),
        "pages_read": pages,
        "text": text[:max_chars],
        "truncated": len(text) > max_chars,
    }


async def pdf_read(payload: dict[str, Any]) -> dict[str, Any]:
    url = str(payload.get("url") or "").strip()
    if not url.startswith(("http://", "https://")):
        return {"error": "url must be http(s)"}
    max_pages = int(payload.get("max_pages") or 20)
    max_chars = int(payload.get("max_chars") or 12000)
    data = await _fetch(url)
    return await asyncio.to_thread(_extract, data, max_pages, max_chars)

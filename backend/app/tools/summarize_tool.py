from __future__ import annotations

from typing import Any

from app.agents.llm import call_json


async def summarize(payload: dict[str, Any]) -> dict[str, Any]:
    text = str(payload.get("text") or "")
    if not text.strip():
        return {"error": "missing text"}
    style = str(payload.get("style") or "bullet points")

    system = (
        "You are a precise summarizer. Compress the user's text without losing factual content. "
        "Return JSON: {\"summary\": \"...\"}"
    )
    user = f"Style: {style}\n\nText to summarize:\n{text[:16000]}"
    parsed, _, _ = await call_json(system, user, temperature=0.1)
    return {"summary": parsed.get("summary") or ""}

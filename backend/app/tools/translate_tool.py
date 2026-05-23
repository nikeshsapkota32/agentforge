from __future__ import annotations

from typing import Any

from app.agents.llm import call_json


async def translate(payload: dict[str, Any]) -> dict[str, Any]:
    text = str(payload.get("text") or "")
    target = str(payload.get("target_lang") or "English")
    if not text.strip():
        return {"error": "missing text"}

    system = (
        "You are a translator. Translate the user's text to the target language without adding "
        "commentary. Return JSON: {\"translation\": \"...\"}"
    )
    user = f"Target language: {target}\n\nText:\n{text[:8000]}"
    parsed, _, _ = await call_json(system, user, temperature=0.0)
    return {"target_lang": target, "translation": parsed.get("translation") or ""}

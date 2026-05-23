from __future__ import annotations

import json
from typing import Any

from langchain_openai import ChatOpenAI

from app.config import settings


def chat_model(temperature: float = 0.2) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.openai_model,
        temperature=temperature,
        api_key=settings.openai_api_key,
        timeout=60,
        max_retries=2,
    )


async def call_json(
    system: str,
    user: str,
    *,
    temperature: float = 0.2,
) -> tuple[dict[str, Any], int, int]:
    """Call the LLM with response_format=json_object and return (parsed, tokens_in, tokens_out)."""
    llm = chat_model(temperature=temperature).bind(response_format={"type": "json_object"})
    msg = await llm.ainvoke(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
    )
    usage = getattr(msg, "usage_metadata", None) or {}
    tokens_in = int(usage.get("input_tokens", 0))
    tokens_out = int(usage.get("output_tokens", 0))
    try:
        parsed = json.loads(msg.content or "{}")
    except json.JSONDecodeError:
        parsed = {"_raw": msg.content}
    return parsed, tokens_in, tokens_out

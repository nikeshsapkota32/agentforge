from __future__ import annotations

import json
from typing import Any

from langchain_openai import ChatOpenAI

from app.config import settings


def chat_model(temperature: float = 0.2) -> ChatOpenAI:
    """Build a chat model client.

    Provider is whatever exposes an OpenAI-compatible /v1/chat/completions:
    - openai (default)
    - groq    -> https://api.groq.com/openai/v1, free Llama 3.3 70B
    - custom  -> set LLM_BASE_URL yourself

    Falls back to OpenAI defaults if specific LLM_* vars aren't set.
    """
    kwargs: dict[str, Any] = {
        "model": settings.resolved_llm_model,
        "temperature": temperature,
        "api_key": settings.resolved_llm_api_key,
        "timeout": 60,
        "max_retries": 2,
    }
    base_url = settings.resolved_llm_base_url
    if base_url:
        kwargs["base_url"] = base_url
    return ChatOpenAI(**kwargs)


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

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from langchain_openai import ChatOpenAI

from app.config import settings

log = logging.getLogger(__name__)


def chat_model(temperature: float = 0.2, model: str | None = None) -> ChatOpenAI:
    """Build a chat model client.

    Provider is whatever exposes an OpenAI-compatible /v1/chat/completions:
    - openrouter (default free)
    - openai, groq, cerebras, gemini, custom
    """
    kwargs: dict[str, Any] = {
        "model": model or settings.resolved_llm_model,
        "temperature": temperature,
        "api_key": settings.resolved_llm_api_key,
        "timeout": 60,
        "max_retries": 2,
    }
    base_url = settings.resolved_llm_base_url
    if base_url:
        kwargs["base_url"] = base_url
    headers = settings.llm_default_headers
    if headers:
        kwargs["default_headers"] = headers
    return ChatOpenAI(**kwargs)


def _is_retryable(err: BaseException) -> bool:
    """Worth trying the next fallback model for: rate-limits, model-missing, gateway errors."""
    msg = str(err).lower()
    needles = (
        "429",
        "rate",
        "rate_limit",
        "rate-limit",
        "404",
        "no endpoints found",
        "not found",
        "model_not_found",
        "502",
        "503",
        "504",
        "timed out",
    )
    return any(n in msg for n in needles)


async def _invoke_once(
    model: str,
    system: str,
    user: str,
    temperature: float,
) -> Any:
    llm = chat_model(temperature=temperature, model=model).bind(
        response_format={"type": "json_object"}
    )
    return await llm.ainvoke(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
    )


async def call_json(
    system: str,
    user: str,
    *,
    temperature: float = 0.2,
) -> tuple[dict[str, Any], int, int]:
    """
    Call the LLM with response_format=json_object.

    Strategy:
      1. Try the configured primary model.
      2. On rate-limit (429), fall back to each model in LLM_FALLBACK_MODELS
         in order, with a small backoff between attempts.

    Returns (parsed_json, tokens_in, tokens_out).
    """
    primary = settings.resolved_llm_model
    fallbacks = [m for m in settings.llm_fallback_list if m != primary]
    candidates = [primary, *fallbacks]

    last_err: BaseException | None = None
    for i, model in enumerate(candidates):
        try:
            msg = await _invoke_once(model, system, user, temperature)
            usage = getattr(msg, "usage_metadata", None) or {}
            tokens_in = int(usage.get("input_tokens", 0))
            tokens_out = int(usage.get("output_tokens", 0))
            try:
                parsed = json.loads(msg.content or "{}")
            except json.JSONDecodeError:
                parsed = {"_raw": msg.content}
            if i > 0:
                log.info("llm fallback hit: served by %s after %d retries", model, i)
            return parsed, tokens_in, tokens_out
        except BaseException as err:
            last_err = err
            if not _is_retryable(err):
                raise
            log.warning("llm error on %s (%s); trying next fallback", model, type(err).__name__)
            await asyncio.sleep(min(2 + i, 6))

    raise RuntimeError(
        f"All LLM candidates failed. Tried: {candidates}. Last error: {last_err}"
    )

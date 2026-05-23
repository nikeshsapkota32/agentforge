from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from app.tools import (
    arxiv_tool,
    calculator_tool,
    datetime_tool,
    pdf_tool,
    python_tool,
    summarize_tool,
    translate_tool,
    vector_tool,
    web_tool,
    wikipedia_tool,
)

ToolFn = Callable[[dict[str, Any]], Awaitable[Any]]

_REGISTRY: dict[str, ToolFn] = {
    "web_search": web_tool.web_search,
    "web_fetch": web_tool.web_fetch,
    "wikipedia": wikipedia_tool.wikipedia_lookup,
    "arxiv": arxiv_tool.arxiv_search,
    "pdf_read": pdf_tool.pdf_read,
    "python_exec": python_tool.python_exec,
    "calculator": calculator_tool.calculate,
    "vector_search": vector_tool.vector_search,
    "vector_write": vector_tool.vector_write,
    "summarize": summarize_tool.summarize,
    "translate": translate_tool.translate,
    "datetime": datetime_tool.now,
}


def list_tools() -> list[str]:
    return list(_REGISTRY.keys())


async def call_tool(name: str, payload: dict[str, Any]) -> Any:
    fn = _REGISTRY.get(name)
    if fn is None:
        raise ValueError(f"unknown tool: {name}")
    if not isinstance(payload, dict):
        raise TypeError(f"tool input must be a dict, got {type(payload).__name__}")
    return await fn(payload)

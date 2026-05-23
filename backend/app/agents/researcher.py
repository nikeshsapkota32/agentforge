from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from app.agents.llm import call_json
from app.agents.prompts import RESEARCHER_SYSTEM
from app.agents.state import ResearchState, ToolCall, finish_step, new_step
from app.tools.registry import call_tool, list_tools


def _user_prompt(query: str, plan: list[str]) -> str:
    lines = [f"Original query: {query}", "", "Sub-questions to research:"]
    lines += [f"{i + 1}. {p}" for i, p in enumerate(plan)]
    lines += [
        "",
        f"Available tools: {', '.join(list_tools())}",
        "",
        "Return JSON: {\"tool_calls\": [{\"tool\": \"...\", \"input\": {...}}], "
        "\"findings\": [{\"claim\":\"...\",\"source\":\"...\",\"snippet\":\"...\"}]}",
    ]
    return "\n".join(lines)


async def _run_tool(tool: str, payload: dict[str, Any]) -> ToolCall:
    call_id = uuid.uuid4().hex
    started = time.monotonic()
    try:
        output = await call_tool(tool, payload)
        return ToolCall(
            id=call_id,
            tool=tool,
            input=payload,
            output=output,
            duration_ms=int((time.monotonic() - started) * 1000),
        )
    except Exception as exc:
        return ToolCall(
            id=call_id,
            tool=tool,
            input=payload,
            duration_ms=int((time.monotonic() - started) * 1000),
            error=str(exc),
        )


async def researcher_node(state: ResearchState) -> ResearchState:
    step = new_step("researcher")

    parsed, tin, tout = await call_json(
        RESEARCHER_SYSTEM,
        _user_prompt(state["query"], state.get("plan") or []),
    )

    raw_calls = parsed.get("tool_calls") or []
    calls = [c for c in raw_calls if isinstance(c, dict) and "tool" in c][:8]

    tool_results: list[ToolCall] = []
    if calls:
        tool_results = await asyncio.gather(
            *(_run_tool(c["tool"], c.get("input") or {}) for c in calls)
        )

    findings = parsed.get("findings") or []
    if not isinstance(findings, list):
        findings = []

    step["thought"] = parsed.get("rationale") or f"Ran {len(tool_results)} tool call(s)."
    step["tool_calls"] = tool_results
    step["tokens_in"] = tin
    step["tokens_out"] = tout
    finish_step(step)

    steps = list(state.get("steps") or [])
    steps.append(step)
    prior_findings = list(state.get("findings") or [])
    return {"findings": prior_findings + findings, "steps": steps}

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Any

from app.agents.graph import build_graph
from app.agents.state import AgentStep as StateAgentStep
from app.agents.state import ResearchState
from app.db import db_session
from app.models import AgentStepRow, ResearchSessionRow, ToolCallRow


def _step_to_event(step: StateAgentStep) -> dict[str, Any]:
    return {
        "id": step.get("id"),
        "role": step.get("role"),
        "thought": step.get("thought") or "",
        "toolCalls": [
            {
                "id": tc.get("id"),
                "tool": tc.get("tool"),
                "input": tc.get("input") or {},
                "output": tc.get("output"),
                "durationMs": tc.get("duration_ms"),
                "error": tc.get("error"),
            }
            for tc in (step.get("tool_calls") or [])
        ],
        "startedAt": step.get("started_at"),
        "endedAt": step.get("ended_at"),
        "tokensIn": step.get("tokens_in"),
        "tokensOut": step.get("tokens_out"),
    }


async def _persist_session(
    user_id: uuid.UUID,
    query: str,
    answer: str,
    score: int | None,
    steps: list[StateAgentStep],
) -> uuid.UUID:
    async with db_session() as db:
        row = ResearchSessionRow(
            user_id=user_id,
            query=query,
            answer=answer or None,
            score=score,
        )
        db.add(row)
        await db.flush()

        for step in steps:
            step_row = AgentStepRow(
                session_id=row.id,
                role=step.get("role") or "planner",
                thought=step.get("thought") or "",
                tokens_in=int(step.get("tokens_in") or 0),
                tokens_out=int(step.get("tokens_out") or 0),
            )
            db.add(step_row)
            await db.flush()
            for tc in step.get("tool_calls") or []:
                output = tc.get("output")
                db.add(
                    ToolCallRow(
                        step_id=step_row.id,
                        tool=tc.get("tool") or "unknown",
                        input=tc.get("input") or {},
                        output=output if isinstance(output, dict) else {"value": output},
                        duration_ms=tc.get("duration_ms"),
                        error=tc.get("error"),
                    )
                )
        await db.commit()
        return row.id


async def run_research(
    *,
    user_id: uuid.UUID,
    query: str,
) -> AsyncIterator[dict[str, Any]]:
    """Drive the LangGraph workflow, yielding SSE-shaped events as it runs."""
    graph = build_graph()
    initial: ResearchState = {
        "user_id": str(user_id),
        "query": query,
        "steps": [],
        "loop_count": 0,
    }

    emitted_step_ids: set[str] = set()
    final_state: ResearchState | None = None

    try:
        async for snapshot in graph.astream(initial, stream_mode="values"):
            final_state = snapshot
            for step in snapshot.get("steps") or []:
                sid = step.get("id")
                if not sid or sid in emitted_step_ids:
                    continue
                if not step.get("ended_at"):
                    continue
                emitted_step_ids.add(sid)
                yield {"type": "agent_step", "step": _step_to_event(step)}
                for tc in step.get("tool_calls") or []:
                    yield {
                        "type": "tool_call",
                        "stepId": sid,
                        "call": {
                            "id": tc.get("id"),
                            "tool": tc.get("tool"),
                            "input": tc.get("input") or {},
                            "output": tc.get("output"),
                            "durationMs": tc.get("duration_ms"),
                            "error": tc.get("error"),
                        },
                    }
    except Exception as exc:
        yield {"type": "error", "message": str(exc)}
        return

    if final_state is None:
        yield {"type": "error", "message": "graph produced no output"}
        return

    answer = final_state.get("answer") or ""
    score = final_state.get("score")
    steps = final_state.get("steps") or []

    session_id = await _persist_session(user_id, query, answer, score, steps)

    yield {
        "type": "done",
        "sessionId": str(session_id),
        "answer": answer,
        "score": int(score or 0),
    }

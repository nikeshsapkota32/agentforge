from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Literal, TypedDict

AgentRole = Literal["planner", "researcher", "synthesizer", "critic"]


class ToolCall(TypedDict, total=False):
    id: str
    tool: str
    input: dict[str, Any]
    output: Any
    duration_ms: int
    error: str


class AgentStep(TypedDict, total=False):
    id: str
    role: AgentRole
    thought: str
    tool_calls: list[ToolCall]
    started_at: str
    ended_at: str
    tokens_in: int
    tokens_out: int


class ResearchState(TypedDict, total=False):
    user_id: str
    session_id: str
    query: str
    plan: list[str]
    findings: list[dict[str, Any]]
    draft_answer: str
    answer: str
    citations: list[str]
    score: int
    critique: str
    loop_count: int
    steps: list[AgentStep]


def new_step(role: AgentRole) -> AgentStep:
    return AgentStep(
        id=uuid.uuid4().hex,
        role=role,
        thought="",
        tool_calls=[],
        started_at=datetime.now(UTC).isoformat(),
        tokens_in=0,
        tokens_out=0,
    )


def finish_step(step: AgentStep) -> AgentStep:
    step["ended_at"] = datetime.now(UTC).isoformat()
    return step

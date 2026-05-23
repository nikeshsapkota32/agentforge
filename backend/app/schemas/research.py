from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ResearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    session_id: UUID | None = None


class ToolCallOut(BaseModel):
    id: str
    tool: str
    input: dict[str, Any]
    output: Any | None = None
    durationMs: int | None = None
    error: str | None = None


class AgentStepOut(BaseModel):
    id: str
    role: str
    thought: str
    toolCalls: list[ToolCallOut] = Field(default_factory=list)
    startedAt: str
    endedAt: str | None = None
    tokensIn: int | None = None
    tokensOut: int | None = None


class SessionSummaryOut(BaseModel):
    id: UUID
    query: str
    score: int | None
    createdAt: datetime


class SessionDetailOut(ORMModel):
    id: UUID
    userId: UUID
    query: str
    answer: str | None
    score: int | None
    steps: list[AgentStepOut]
    createdAt: datetime
    updatedAt: datetime

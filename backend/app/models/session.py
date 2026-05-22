from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ResearchSessionRow(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "research_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    steps: Mapped[list[AgentStepRow]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="AgentStepRow.created_at"
    )


class AgentStepRow(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "agent_steps"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_sessions.id", ondelete="CASCADE"),
        index=True,
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    thought: Mapped[str] = mapped_column(Text, default="", nullable=False)
    tokens_in: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    session: Mapped[ResearchSessionRow] = relationship(back_populates="steps")
    tool_calls: Mapped[list[ToolCallRow]] = relationship(
        back_populates="step", cascade="all, delete-orphan", order_by="ToolCallRow.created_at"
    )


class ToolCallRow(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "tool_calls"

    step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("agent_steps.id", ondelete="CASCADE"), index=True
    )
    tool: Mapped[str] = mapped_column(String(64), nullable=False)
    input: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    step: Mapped[AgentStepRow] = relationship(back_populates="tool_calls")

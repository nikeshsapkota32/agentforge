from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models import AgentStepRow, ResearchSessionRow
from app.schemas.research import AgentStepOut, SessionDetailOut, SessionSummaryOut, ToolCallOut

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionSummaryOut])
async def list_sessions(user: CurrentUser, db: DbSession) -> list[SessionSummaryOut]:
    result = await db.execute(
        select(ResearchSessionRow)
        .where(ResearchSessionRow.user_id == user.id)
        .order_by(ResearchSessionRow.created_at.desc())
        .limit(100)
    )
    rows = result.scalars().all()
    return [
        SessionSummaryOut(
            id=row.id,
            query=row.query,
            score=row.score,
            createdAt=row.created_at,
        )
        for row in rows
    ]


def _step_to_out(step: AgentStepRow) -> AgentStepOut:
    return AgentStepOut(
        id=step.id.hex,
        role=step.role,
        thought=step.thought,
        startedAt=step.created_at.isoformat(),
        endedAt=step.updated_at.isoformat(),
        tokensIn=step.tokens_in,
        tokensOut=step.tokens_out,
        toolCalls=[
            ToolCallOut(
                id=tc.id.hex,
                tool=tc.tool,
                input=tc.input,
                output=tc.output,
                durationMs=tc.duration_ms,
                error=tc.error,
            )
            for tc in step.tool_calls
        ],
    )


@router.get("/{session_id}", response_model=SessionDetailOut)
async def get_session(session_id: UUID, user: CurrentUser, db: DbSession) -> SessionDetailOut:
    result = await db.execute(
        select(ResearchSessionRow)
        .where(
            ResearchSessionRow.id == session_id,
            ResearchSessionRow.user_id == user.id,
        )
        .options(selectinload(ResearchSessionRow.steps).selectinload(AgentStepRow.tool_calls))
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return SessionDetailOut(
        id=row.id,
        userId=row.user_id,
        query=row.query,
        answer=row.answer,
        score=row.score,
        steps=[_step_to_out(s) for s in row.steps],
        createdAt=row.created_at,
        updatedAt=row.updated_at,
    )

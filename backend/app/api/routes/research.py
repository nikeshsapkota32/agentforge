from __future__ import annotations

import json
from collections.abc import AsyncIterator

import orjson
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from app.api.deps import CurrentUser, rate_limit_user
from app.schemas.research import ResearchRequest
from app.services.research_runner import run_research

router = APIRouter(tags=["research"])


async def _sse_stream(user_id, query: str) -> AsyncIterator[dict[str, str]]:
    async for event in run_research(user_id=user_id, query=query):
        yield {"data": orjson.dumps(event).decode("utf-8")}


@router.post("/research", dependencies=[Depends(rate_limit_user)])
async def research(payload: ResearchRequest, user: CurrentUser) -> EventSourceResponse:
    return EventSourceResponse(
        _sse_stream(user.id, payload.query),
        ping=15,
        media_type="text/event-stream",
    )


# unused import retained to keep mypy happy when json fallback is needed
_ = json

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import enforce_rate_limit
from app.core.security import decode_token
from app.db import get_db
from app.models import UserRow

bearer = HTTPBearer(auto_error=False)


async def db_dep() -> AsyncIterator[AsyncSession]:
    async for s in get_db():
        yield s


DbSession = Annotated[AsyncSession, Depends(db_dep)]


async def current_user(
    db: DbSession,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> UserRow:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = decode_token(creds.credentials, expected_type="access")
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject"
        ) from exc

    user = await db.get(UserRow, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


CurrentUser = Annotated[UserRow, Depends(current_user)]


async def rate_limit_user(user: CurrentUser) -> None:
    await enforce_rate_limit(f"user:{user.id}", cost=1)


async def rate_limit_ip(request: Request) -> None:
    ip = request.client.host if request.client else "anon"
    await enforce_rate_limit(f"ip:{ip}", cost=1)


async def _unused_email_lookup(db: DbSession, email: str) -> UserRow | None:
    result = await db.execute(select(UserRow).where(UserRow.email == email))
    return result.scalar_one_or_none()

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession, rate_limit_ip
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models import RefreshTokenRow, UserRow
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    SignupRequest,
    TokenPair,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


async def _issue_token_pair(db: DbSession, user: UserRow) -> TokenPair:
    access = create_access_token(user.id, user.email)
    refresh_raw, refresh_hash, expires_at = create_refresh_token(user.id, user.email)
    db.add(
        RefreshTokenRow(
            user_id=user.id,
            token_hash=refresh_hash,
            expires_at=expires_at,
        )
    )
    await db.commit()
    return TokenPair(access_token=access, refresh_token=refresh_raw)


@router.post(
    "/signup",
    response_model=TokenPair,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_ip)],
)
async def signup(payload: SignupRequest, db: DbSession) -> TokenPair:
    existing = await db.execute(select(UserRow).where(UserRow.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    user = UserRow(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    await db.flush()
    return await _issue_token_pair(db, user)


@router.post("/login", response_model=TokenPair, dependencies=[Depends(rate_limit_ip)])
async def login(payload: LoginRequest, db: DbSession) -> TokenPair:
    result = await db.execute(select(UserRow).where(UserRow.email == payload.email))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    return await _issue_token_pair(db, user)


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(payload: RefreshRequest, db: DbSession) -> AccessTokenResponse:
    try:
        claims = decode_token(payload.refresh_token, expected_type="refresh")
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        ) from exc

    token_hash = hash_token(payload.refresh_token)
    result = await db.execute(
        select(RefreshTokenRow).where(RefreshTokenRow.token_hash == token_hash)
    )
    row = result.scalar_one_or_none()
    now = datetime.now(UTC)
    if row is None or row.revoked_at is not None or row.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked"
        )

    user = await db.get(UserRow, row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if claims.get("sub") != str(user.id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token subject mismatch"
        )
    return AccessTokenResponse(access_token=create_access_token(user.id, user.email))


@router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(user: CurrentUser, db: DbSession) -> None:
    now = datetime.now(UTC)
    result = await db.execute(
        select(RefreshTokenRow).where(
            RefreshTokenRow.user_id == user.id,
            RefreshTokenRow.revoked_at.is_(None),
        )
    )
    for row in result.scalars():
        row.revoked_at = now
    await db.commit()


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)

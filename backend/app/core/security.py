from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# bcrypt only consumes the first 72 bytes of input. Newer libs raise on
# anything longer instead of silently truncating; we clip ourselves to stay
# compatible with both behaviors and to make hashing deterministic.
_BCRYPT_MAX_BYTES = 72


def _clip_password(password: str) -> str:
    encoded = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return encoded.decode("utf-8", errors="ignore")


def hash_password(password: str) -> str:
    return _pwd.hash(_clip_password(password))


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd.verify(_clip_password(password), password_hash)


def _materialize(env_value: str, path) -> str:
    """Prefer the env-supplied PEM; fall back to disk."""
    if env_value:
        # Allow newlines passed as literal '\n' (common in PaaS env editors).
        return env_value.replace("\\n", "\n")
    return path.read_text()


def _private_key() -> str:
    return _materialize(settings.jwt_private_key, settings.jwt_private_key_path)


def _public_key() -> str:
    return _materialize(settings.jwt_public_key, settings.jwt_public_key_path)


TokenType = Literal["access", "refresh"]


def create_token(*, sub: str, email: str, token_type: TokenType, ttl_seconds: int) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": sub,
        "email": email,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, _private_key(), algorithm=settings.jwt_algorithm)


def create_access_token(user_id: uuid.UUID, email: str) -> str:
    return create_token(
        sub=str(user_id),
        email=email,
        token_type="access",
        ttl_seconds=settings.access_token_ttl_seconds,
    )


def create_refresh_token(user_id: uuid.UUID, email: str) -> tuple[str, str, datetime]:
    token = create_token(
        sub=str(user_id),
        email=email,
        token_type="refresh",
        ttl_seconds=settings.refresh_token_ttl_seconds,
    )
    token_hash = hash_token(token)
    expires_at = datetime.now(UTC) + timedelta(seconds=settings.refresh_token_ttl_seconds)
    return token, token_hash, expires_at


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    payload = jwt.decode(token, _public_key(), algorithms=[settings.jwt_algorithm])
    if payload.get("type") != expected_type:
        raise JWTError(f"expected token type {expected_type}, got {payload.get('type')}")
    return payload


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def random_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)

from __future__ import annotations

import logging
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

log = logging.getLogger(__name__)


def _mask(url: str) -> str:
    """Return a copy of the URL with the password redacted."""
    return re.sub(r"(://[^:/?#]+:)[^@]*(@)", r"\1***\2", url or "")


def _normalize_db_url(raw: str) -> tuple[str, dict]:
    """
    Make the DATABASE_URL safe for asyncpg.

    Accepts whatever shape the env var arrives in:
    - postgresql://...        -> rewrite to postgresql+asyncpg://...
    - ?sslmode=require        -> drop (libpq-only, asyncpg rejects)
    - ?ssl=require|true       -> drop from URL, pass via connect_args
    - missing /dbname         -> default to /postgres
    - any other query params  -> preserved

    Returns (clean_url, connect_args).
    """
    if not raw:
        return raw, {}

    raw = raw.strip().strip('"').strip("'")

    # Collapse accidental double-?, which would otherwise leak '?' into a
    # query-string key name and trigger configparser interpolation later.
    while "??" in raw:
        raw = raw.replace("??", "?")

    parts = urlsplit(raw)
    scheme = parts.scheme or "postgresql"
    if scheme == "postgresql" or scheme == "postgres":
        scheme = "postgresql+asyncpg"

    if not parts.netloc:
        raise ValueError(
            f"DATABASE_URL is missing the host part. Got: {_mask(raw)!r}"
        )

    # Some PaaS env editors lose the path. asyncpg needs at least /<db>.
    path = parts.path or "/postgres"

    connect_args: dict = {}
    new_qs: list[tuple[str, str]] = []
    for k, v in parse_qsl(parts.query, keep_blank_values=False):
        # Tolerate accidentally-included leading punctuation like "?ssl".
        key = k.strip().lstrip("?&").lower()
        if key == "sslmode":
            if v.lower() in ("require", "verify-ca", "verify-full"):
                connect_args["ssl"] = True
            continue
        if key == "ssl":
            if v.lower() in ("true", "require", "verify-ca", "verify-full"):
                connect_args["ssl"] = True
            elif v.lower() in ("false", "disable"):
                connect_args["ssl"] = False
            continue
        new_qs.append((k, v))

    cleaned = urlunsplit(
        (scheme, parts.netloc, path, urlencode(new_qs), parts.fragment)
    )
    return cleaned, connect_args


_clean_url, _connect_args = _normalize_db_url(settings.database_url)

if not _clean_url:
    raise RuntimeError(
        "DATABASE_URL is empty. Set it in your environment to a Postgres "
        "connection string, e.g. "
        "postgresql+asyncpg://user:pass@host/dbname?ssl=require"
    )

log.info(
    "Connecting to database %s (ssl=%s)",
    _mask(_clean_url),
    _connect_args.get("ssl", "default"),
)

engine = create_async_engine(
    _clean_url,
    echo=settings.database_echo,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=_connect_args,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


async def init_db() -> None:
    """Create any missing tables. Safe to call on every boot — create_all is idempotent."""
    from app.models import Base  # imported here to avoid circular import at module load

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("init_db: schema verified")


async def get_db() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def db_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

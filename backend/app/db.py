from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


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

    # Collapse accidental double-?, which would otherwise leak '?' into a
    # query-string key name and trigger configparser interpolation later.
    while "??" in raw:
        raw = raw.replace("??", "?")

    parts = urlsplit(raw)
    scheme = parts.scheme or "postgresql"
    if scheme == "postgresql" or scheme == "postgres":
        scheme = "postgresql+asyncpg"

    # Some PaaS env editors lose the path. asyncpg needs at least /<db>.
    path = parts.path or "/postgres"

    connect_args: dict = {}
    new_qs: list[tuple[str, str]] = []
    for k, v in parse_qsl(parts.query, keep_blank_values=False):
        # Tolerate accidentally-included leading punctuation like "?ssl".
        key = k.strip().lstrip("?&").lower()
        if key == "sslmode":
            # libpq style; asyncpg uses `ssl` kwarg instead.
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

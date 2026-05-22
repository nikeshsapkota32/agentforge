from __future__ import annotations

from fastapi import HTTPException, status

from app.config import settings
from app.core.redis import get_redis

_LUA_TOKEN_BUCKET = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_per_sec = tonumber(ARGV[2])
local now_ms = tonumber(ARGV[3])
local cost = tonumber(ARGV[4])
local ttl_ms = tonumber(ARGV[5])

local bucket = redis.call("HMGET", key, "tokens", "ts")
local tokens = tonumber(bucket[1])
local ts = tonumber(bucket[2])

if tokens == nil then
  tokens = capacity
  ts = now_ms
end

local elapsed = math.max(0, now_ms - ts) / 1000.0
tokens = math.min(capacity, tokens + elapsed * refill_per_sec)

local allowed = 0
if tokens >= cost then
  tokens = tokens - cost
  allowed = 1
end

redis.call("HMSET", key, "tokens", tokens, "ts", now_ms)
redis.call("PEXPIRE", key, ttl_ms)

return {allowed, tokens}
"""


async def enforce_rate_limit(identity: str, *, cost: int = 1) -> None:
    capacity = settings.rate_limit_per_minute
    refill_per_sec = capacity / 60.0
    redis = get_redis()
    now_ms = int(__import__("time").time() * 1000)
    key = f"rl:{identity}"
    ttl_ms = 5 * 60 * 1000

    result = await redis.eval(
        _LUA_TOKEN_BUCKET,
        1,
        key,
        capacity,
        refill_per_sec,
        now_ms,
        cost,
        ttl_ms,
    )
    allowed = int(result[0])
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again shortly.",
            headers={"Retry-After": "10"},
        )

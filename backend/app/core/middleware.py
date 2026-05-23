from __future__ import annotations

import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

log = logging.getLogger("agentforge.access")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
        )
        if request.url.scheme == "https":
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex
        start = time.monotonic()
        try:
            response = await call_next(request)
        except Exception:
            elapsed = int((time.monotonic() - start) * 1000)
            log.exception("request %s %s failed after %dms (rid=%s)", request.method, request.url.path, elapsed, rid)
            return JSONResponse(
                status_code=500,
                content={"detail": "internal server error"},
                headers={"X-Request-ID": rid},
            )
        elapsed = int((time.monotonic() - start) * 1000)
        log.info(
            "%s %s -> %d (%dms, rid=%s)",
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
            rid,
        )
        response.headers["X-Request-ID"] = rid
        return response

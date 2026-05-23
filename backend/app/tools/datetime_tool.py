from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


async def now(payload: dict[str, Any]) -> dict[str, Any]:
    tz = (payload.get("tz") or "UTC").upper()
    dt = datetime.now(UTC)
    return {
        "utc_iso": dt.isoformat(),
        "epoch_seconds": int(dt.timestamp()),
        "weekday": dt.strftime("%A"),
        "requested_tz": tz,
    }

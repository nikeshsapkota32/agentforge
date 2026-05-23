from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path
from typing import Any

_TIMEOUT_SECONDS = 8
_MAX_OUTPUT_BYTES = 16 * 1024


async def python_exec(payload: dict[str, Any]) -> dict[str, Any]:
    code = str(payload.get("code") or "")
    if not code.strip():
        return {"error": "empty code"}
    if len(code) > 16_000:
        return {"error": "code too long"}

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "snippet.py"
        path.write_text(code, encoding="utf-8")

        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-I",
            "-S",
            str(path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tmp,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=_TIMEOUT_SECONDS)
        except TimeoutError:
            proc.kill()
            await proc.wait()
            return {"error": f"timed out after {_TIMEOUT_SECONDS}s"}

    return {
        "exit_code": proc.returncode,
        "stdout": stdout[:_MAX_OUTPUT_BYTES].decode("utf-8", errors="replace"),
        "stderr": stderr[:_MAX_OUTPUT_BYTES].decode("utf-8", errors="replace"),
        "stdout_truncated": len(stdout) > _MAX_OUTPUT_BYTES,
        "stderr_truncated": len(stderr) > _MAX_OUTPUT_BYTES,
    }

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

_TIMEOUT_SECONDS = 8
_MAX_OUTPUT_BYTES = 16 * 1024
_MEM_LIMIT_BYTES = 256 * 1024 * 1024
_CPU_SECONDS = 6


def _posix_preexec() -> None:  # pragma: no cover - POSIX only
    import resource

    resource.setrlimit(resource.RLIMIT_CPU, (_CPU_SECONDS, _CPU_SECONDS))
    resource.setrlimit(resource.RLIMIT_AS, (_MEM_LIMIT_BYTES, _MEM_LIMIT_BYTES))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))


async def python_exec(payload: dict[str, Any]) -> dict[str, Any]:
    code = str(payload.get("code") or "")
    if not code.strip():
        return {"error": "empty code"}
    if len(code) > 16_000:
        return {"error": "code too long"}

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "snippet.py"
        path.write_text(code, encoding="utf-8")

        kwargs: dict[str, Any] = {
            "stdout": asyncio.subprocess.PIPE,
            "stderr": asyncio.subprocess.PIPE,
            "cwd": tmp,
            "env": {"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0"},
        }
        if os.name == "posix":
            kwargs["preexec_fn"] = _posix_preexec
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-I", "-S", "-B", str(path), **kwargs
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

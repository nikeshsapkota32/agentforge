from __future__ import annotations

import logging
import os

from app.config import settings

log = logging.getLogger(__name__)


def configure_observability() -> None:
    """Configure LangSmith tracing via env vars LangChain reads at import time."""
    if not settings.langsmith_tracing:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")
        return

    if not settings.langsmith_api_key:
        log.warning("LANGSMITH_TRACING enabled but no LANGSMITH_API_KEY; disabling.")
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        return

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
    log.info("LangSmith tracing enabled (project=%s)", settings.langsmith_project)

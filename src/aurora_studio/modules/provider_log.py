"""Provider request/response log for Aurora Studio v0.3.

Sanitized in-memory log. No secrets. No network calls. No provider SDK.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.provider import (
    LOG_EVENT_TYPES,
    ProviderLogEntry,
    ProviderRequest,
    ProviderResponse,
)

_PREVIEW_MAX = 80
_SECRET_PATTERNS = frozenset({
    "api_key", "apikey", "api-key",
    "token", "bearer", "secret",
    "password", "credential", "key",
    "authorization", "auth",
})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize_preview(text: str, max_len: int = _PREVIEW_MAX) -> str:
    """Truncate text and mask any line that looks like a secret."""
    lines = text.splitlines()
    safe: list[str] = []
    for line in lines:
        lower = line.lower()
        if any(pat in lower for pat in _SECRET_PATTERNS):
            safe.append("[REDACTED]")
        else:
            safe.append(line)
    result = " ".join(safe)
    if len(result) > max_len:
        result = result[:max_len] + "..."
    return result


class ProviderLog:
    """In-memory sanitized provider log.

    Stores ProviderLogEntry records only.
    No secrets are written.
    """

    def __init__(self) -> None:
        self._entries: list[ProviderLogEntry] = []

    def record(
        self,
        request: ProviderRequest,
        response: ProviderResponse,
        event_type: str = "dry_run_completed",
    ) -> ProviderLogEntry:
        if event_type not in LOG_EVENT_TYPES:
            event_type = "dry_run_completed"

        entry = ProviderLogEntry(
            log_id=f"log-{uuid.uuid4().hex[:12]}",
            request_id=request.request_id,
            response_id=response.response_id,
            provider_id=request.provider_id,
            event_type=event_type,
            status=response.status,
            source_type=request.source_type,
            source_id=request.source_id,
            prompt_preview=_sanitize_preview(request.prompt_text),
            output_preview=_sanitize_preview(response.output_text),
            error_message=_sanitize_preview(response.error_message),
            created_at=_utc_now(),
        )
        self._entries.append(entry)
        return entry

    def list_entries(
        self,
        provider_id: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[ProviderLogEntry]:
        results = list(self._entries)
        if provider_id is not None:
            results = [e for e in results if e.provider_id == provider_id]
        if status is not None:
            results = [e for e in results if e.status == status]
        # Most recent first
        results.reverse()
        return results[:limit]

    def clear(self) -> int:
        count = len(self._entries)
        self._entries.clear()
        return count

    def count(self) -> int:
        return len(self._entries)

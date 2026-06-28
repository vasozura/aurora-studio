"""Provider error handling for Aurora Studio v0.3.

Normalizes errors from provider workflow into compact, safe user messages.
No traceback leakage. No secret exposure.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.provider import (
    PROVIDER_ERROR_TYPES,
    RETRYABLE_ERROR_TYPES,
    ProviderError,
)

_SECRET_PATTERNS = frozenset({
    "api_key", "apikey", "token", "bearer", "secret",
    "password", "credential", "authorization",
})

_MAX_MSG_LEN = 200


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize_message(text: str) -> str:
    """Remove secret-like content and truncate."""
    if not text:
        return ""
    lines = str(text).splitlines()
    safe: list[str] = []
    for line in lines:
        if any(p in line.lower() for p in _SECRET_PATTERNS):
            safe.append("[REDACTED]")
        else:
            safe.append(line)
    result = " ".join(safe)
    result = "".join(c if c.isprintable() else " " for c in result)
    if len(result) > _MAX_MSG_LEN:
        result = result[:_MAX_MSG_LEN] + "..."
    return result.strip()


def normalize_error(
    error: Exception | str,
    provider_id: str = "",
    source_type: str = "",
    source_id: str = "",
    request_id: str = "",
    error_type: str = "unknown",
) -> ProviderError:
    """Convert an exception or string into a ProviderError."""
    raw_msg = str(error) if not isinstance(error, str) else error

    # Infer error type from known patterns
    lower = raw_msg.lower()
    if error_type == "unknown":
        if "disabled" in lower:
            error_type = "provider_disabled"
        elif "not configured" in lower or "not found" in lower:
            error_type = "provider_not_configured"
        elif "validation" in lower or "must not be empty" in lower or "invalid" in lower:
            error_type = "validation_error"
        elif "blocked" in lower:
            error_type = "blocked"
        elif "network" in lower or "connection" in lower:
            error_type = "network_error"
        elif "timeout" in lower:
            error_type = "timeout"
        elif "rate" in lower or "limit" in lower:
            error_type = "rate_limited"

    if error_type not in PROVIDER_ERROR_TYPES:
        error_type = "unknown"

    return ProviderError(
        error_id=f"err-{uuid.uuid4().hex[:12]}",
        provider_id=provider_id,
        error_type=error_type,
        message=_sanitize_message(raw_msg),
        is_retryable=is_retryable(error_type),
        source_type=source_type,
        source_id=source_id,
        request_id=request_id,
        created_at=_utc_now(),
    )


def is_retryable(error_type: str) -> bool:
    """Return True if this error type is considered retryable."""
    return error_type in RETRYABLE_ERROR_TYPES


def to_user_message(provider_error: ProviderError) -> str:
    """Return a compact, traceback-free message for UI display."""
    prefix = {
        "validation_error": "Invalid input",
        "provider_not_configured": "Provider not configured",
        "provider_disabled": "Provider is disabled",
        "provider_unavailable": "Provider unavailable",
        "rate_limited": "Rate limit reached",
        "network_error": "Network error",
        "timeout": "Request timed out",
        "blocked": "Request blocked",
        "unknown": "Unexpected error",
    }.get(provider_error.error_type, "Error")

    msg = provider_error.message
    if not msg:
        return prefix + "."
    if len(msg) > 120:
        msg = msg[:120] + "..."
    return f"{prefix}: {msg}"


def to_log_payload(provider_error: ProviderError) -> dict[str, Any]:
    """Return a JSON-safe log payload without tracebacks."""
    return {
        "error_id": provider_error.error_id,
        "provider_id": provider_error.provider_id,
        "error_type": provider_error.error_type,
        "message": provider_error.message,
        "is_retryable": provider_error.is_retryable,
        "source_type": provider_error.source_type,
        "source_id": provider_error.source_id,
        "request_id": provider_error.request_id,
        "created_at": provider_error.created_at,
    }

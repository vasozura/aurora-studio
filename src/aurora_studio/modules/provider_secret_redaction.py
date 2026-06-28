"""Provider secret redaction utilities for Aurora Studio v0.4.

Redacts API keys and other secrets from values, payloads, and log text.
No provider SDK. No network. No subprocess.
Standard library only.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_KEY_LIKE_FIELD_NAMES: frozenset[str] = frozenset({
    "api_key",
    "apikey",
    "token",
    "secret",
    "password",
    "authorization",
    "auth_header",
    "bearer",
    "private_key",
    "access_token",
    "refresh_token",
    "client_secret",
})

# Patterns that look like secrets (long alphanumeric strings, key prefixes, etc.)
_SECRET_PATTERNS: list[re.Pattern] = [
    re.compile(r'sk-[A-Za-z0-9]{20,}'),          # OpenAI-style keys
    re.compile(r'Bearer\s+[A-Za-z0-9\-_.]{10,}'),  # Bearer tokens
    re.compile(r'[A-Za-z0-9]{32,}'),               # Long base key strings
]

_REDACTED = "<redacted>"
_EMPTY = "<empty>"
_MIN_SECRET_LENGTH = 4
_PREFIX_SUFFIX_LEN = 3


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def redact_secret(value: str) -> str:
    """Return a redacted representation of a secret value.

    - Empty -> '<empty>'
    - Short (< MIN_SECRET_LENGTH) -> masked entirely
    - Long -> '<redacted>'
    """
    if not isinstance(value, str):
        value = str(value)
    stripped = value.strip()
    if not stripped:
        return _EMPTY
    if len(stripped) < _MIN_SECRET_LENGTH:
        return "*" * len(stripped)
    return _REDACTED


def looks_like_secret(value: str) -> bool:
    """Return True if the value looks like it could be a secret.

    Heuristics: long alphanumeric string, known key prefixes, etc.
    """
    if not isinstance(value, str):
        return False
    stripped = value.strip()
    if len(stripped) >= 20 and stripped.isalnum():
        return True
    for pattern in _SECRET_PATTERNS:
        if pattern.search(stripped):
            return True
    return False


def sanitize_provider_config_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove or redact all key-like fields from a provider config payload.

    Returns a new dict — does not mutate the input.
    Known key-like field names are replaced with '<redacted>'.
    """
    if not isinstance(payload, dict):
        return {}
    result = {}
    for k, v in payload.items():
        k_lower = k.lower().replace("-", "_")
        if k_lower in _KEY_LIKE_FIELD_NAMES:
            result[k] = _REDACTED
        elif isinstance(v, dict):
            result[k] = sanitize_provider_config_payload(v)
        else:
            result[k] = v
    return result


def sanitize_text_for_secrets(text: str) -> str:
    """Replace secret-like patterns in free text with '<redacted>'.

    Used for sanitizing log strings before persistence.
    """
    if not isinstance(text, str):
        return str(text)
    result = text
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub(_REDACTED, result)
    return result

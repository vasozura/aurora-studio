"""Provider config contracts for Aurora Studio v0.4.

No provider SDK. No network. No real API key storage.
Standard library only.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KEY_ENTRY_STATUSES: frozenset[str] = frozenset({
    "empty",
    "entered_not_saved",
    "redacted",
    "cleared",
    "invalid_format",
    "storage_not_configured",
})

CONFIG_STATUSES: frozenset[str] = frozenset({
    "not_configured",
    "configured_without_secret",
    "secret_required",
    "secret_entry_not_saved",
    "storage_not_configured",
    "disabled",
    "blocked",
    "invalid",
})

SECRET_STORAGE_STATUSES: frozenset[str] = frozenset({
    "not_supported",
    "not_configured",
    "planned",
    "external_required",
    "blocked",
})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# ProviderSecretPlaceholder
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderSecretPlaceholder:
    """Placeholder record for a provider secret entry.

    Never stores the real secret value.
    redacted_value is the only representation of any user input.
    """

    provider_id: str
    redacted_value: str = ""
    status: str = "empty"
    message: str = ""
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict — never includes real key value."""
        return {
            "provider_id": self.provider_id,
            "redacted_value": self.redacted_value,
            "status": self.status,
            "message": self.message,
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Any) -> "ProviderSecretPlaceholder":
        return cls(
            provider_id=str(data["provider_id"]),
            redacted_value=str(data.get("redacted_value", "")),
            status=str(data.get("status", "empty")),
            message=str(data.get("message", "")),
            created_at=str(data.get("created_at", _utc_now())),
        )


# ---------------------------------------------------------------------------
# ProviderKeyEntryState
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderKeyEntryState:
    """State record for the user API key entry boundary.

    Tracks whether a user has entered a key and what its redacted form looks like.
    The real key is NEVER stored in this dataclass.
    """

    provider_id: str
    has_user_input: bool = False
    redacted_value: str = ""
    status: str = "empty"
    message: str = "Not saved. Storage not configured. Real provider calls disabled."
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict — never includes real key value."""
        return {
            "provider_id": self.provider_id,
            "has_user_input": self.has_user_input,
            "redacted_value": self.redacted_value,
            "status": self.status,
            "message": self.message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Any) -> "ProviderKeyEntryState":
        return cls(
            provider_id=str(data["provider_id"]),
            has_user_input=bool(data.get("has_user_input", False)),
            redacted_value=str(data.get("redacted_value", "")),
            status=str(data.get("status", "empty")),
            message=str(data.get("message", "")),
            created_at=str(data.get("created_at", _utc_now())),
            updated_at=str(data.get("updated_at", _utc_now())),
        )

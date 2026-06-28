"""Provider security contracts for Aurora Studio v0.4.

No provider SDK imports.
No network calls.
No real API key storage.
Standard library only.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SECRET_FIELD_NAMES: frozenset[str] = frozenset({
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

SECRET_STORAGE_PROHIBITED_LOCATIONS: frozenset[str] = frozenset({
    "project_json",
    "autosave_file",
    "backup_file",
    "export_artifact",
    "provider_log",
    "run_history",
    "portable_zip",
    "release_notes",
    "screenshot",
    "console_output",
})

GATE_DECISION_REASONS: frozenset[str] = frozenset({
    "blocked_v0_4",
    "missing_prerequisites",
    "no_adapter",
    "no_keyring",
    "no_user_consent",
    "execution_allowed",
    "dry_run_allowed",
    "mock_allowed",
    "real_text_blocked",
    "real_text_allowed",
})

EXECUTION_GATE_STATUSES: frozenset[str] = frozenset({
    "blocked",
    "allowed",
    "prerequisites_not_met",
    "adapter_not_implemented",
})

# Execution modes for the gate (TASK-000106)
PROVIDER_EXECUTION_MODES: frozenset[str] = frozenset({
    "dry_run",
    "mock",
    "real_text",
    "blocked_real",
})

# All prerequisites required before real_text execution may proceed (TASK-000106)
REAL_TEXT_PREREQUISITES: tuple[str, ...] = (
    "provider_registered",
    "provider_enabled",
    "real_execution_requested",
    "real_execution_allowed",
    "secret_reference_available",
    "secret_storage_approved",
    "text_only_request",
    "redaction_enabled",
    "logging_sanitized",
    "network_allowed_for_provider",
    "user_confirmed",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# ProviderExecutionPrerequisite
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderExecutionPrerequisite:
    """A single prerequisite for provider execution."""

    name: str
    description: str = ""
    satisfied: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "satisfied": self.satisfied,
        }


# ---------------------------------------------------------------------------
# ProviderExecutionMode
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderExecutionMode:
    """Describes an execution mode for a provider request."""

    mode: str
    description: str = ""
    requires_secret: bool = False
    requires_network: bool = False
    allowed_by_default: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "description": self.description,
            "requires_secret": self.requires_secret,
            "requires_network": self.requires_network,
            "allowed_by_default": self.allowed_by_default,
        }


# ---------------------------------------------------------------------------
# ProviderExecutionGateDecision
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderExecutionGateDecision:
    """Decision record returned by the provider execution gate.

    Extended in TASK-000106 to include mode and missing_conditions.
    Backward-compatible: mode and missing_conditions have defaults.
    """

    provider_id: str
    requested_action: str
    allowed: bool
    reason: str
    required_conditions: tuple[str, ...] = ()
    missing_conditions: tuple[str, ...] = ()
    mode: str = "dry_run"
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "requested_action": self.requested_action,
            "allowed": self.allowed,
            "reason": self.reason,
            "mode": self.mode,
            "required_conditions": list(self.required_conditions),
            "missing_conditions": list(self.missing_conditions),
            "created_at": self.created_at,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Any) -> "ProviderExecutionGateDecision":
        return cls(
            provider_id=str(data["provider_id"]),
            requested_action=str(data.get("requested_action", "")),
            allowed=bool(data.get("allowed", False)),
            reason=str(data.get("reason", "")),
            required_conditions=tuple(data.get("required_conditions", [])),
            missing_conditions=tuple(data.get("missing_conditions", [])),
            mode=str(data.get("mode", "dry_run")),
            created_at=str(data.get("created_at", _utc_now())),
        )

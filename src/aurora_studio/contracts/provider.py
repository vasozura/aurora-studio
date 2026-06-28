"""Provider contracts for Aurora Studio v0.3.

No provider SDK imports.
No network calls.
No real API key storage.
All types are standard-library dataclasses only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROVIDER_TYPES = frozenset({
    "text", "image", "video", "audio", "multimodal", "local", "dry_run", "other",
})

PROVIDER_STATES = frozenset({
    "available", "disabled", "not_configured", "error",
})

RESPONSE_STATUSES = frozenset({
    "dry_run", "success", "failed", "blocked",
})

LOG_EVENT_TYPES = frozenset({
    "request_created", "dry_run_completed", "provider_failed", "blocked",
})

DRY_RUN_PROVIDER_ID = "dry-run-local"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Provider capability
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderCapability:
    """A single capability that a provider declares."""

    name: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> "ProviderCapability":
        return cls(
            name=str(data["name"]),
            description=str(data.get("description", "")),
        )


# ---------------------------------------------------------------------------
# Provider definition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderDefinition:
    """Metadata record for a registered provider."""

    provider_id: str
    name: str
    version: str
    provider_type: str
    state: str = "not_configured"
    capabilities: tuple[ProviderCapability, ...] = ()
    requires_api_key: bool = False
    supports_dry_run: bool = True
    description: str = ""
    error_message: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "name": self.name,
            "version": self.version,
            "provider_type": self.provider_type,
            "state": self.state,
            "capabilities": [c.to_dict() for c in self.capabilities],
            "requires_api_key": self.requires_api_key,
            "supports_dry_run": self.supports_dry_run,
            "description": self.description,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def with_updates(self, **changes: Any) -> "ProviderDefinition":
        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: Any) -> "ProviderDefinition":
        caps = tuple(
            ProviderCapability.from_dict(c) for c in data.get("capabilities", [])
        )
        return cls(
            provider_id=str(data["provider_id"]),
            name=str(data["name"]),
            version=str(data.get("version", "0.0.0")),
            provider_type=str(data.get("provider_type", "other")),
            state=str(data.get("state", "not_configured")),
            capabilities=caps,
            requires_api_key=bool(data.get("requires_api_key", False)),
            supports_dry_run=bool(data.get("supports_dry_run", True)),
            description=str(data.get("description", "")),
            error_message=str(data.get("error_message", "")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )


# ---------------------------------------------------------------------------
# Provider status (summary view)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderStatus:
    """Thin status summary for a provider."""

    provider_id: str
    name: str
    provider_type: str
    state: str
    supports_dry_run: bool
    requires_api_key: bool
    error_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_definition(cls, defn: ProviderDefinition) -> "ProviderStatus":
        return cls(
            provider_id=defn.provider_id,
            name=defn.name,
            provider_type=defn.provider_type,
            state=defn.state,
            supports_dry_run=defn.supports_dry_run,
            requires_api_key=defn.requires_api_key,
            error_message=defn.error_message,
        )


# ---------------------------------------------------------------------------
# Provider request / response (added in TASK-000079)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderRequest:
    """A prompt request dispatched to a provider."""

    request_id: str
    provider_id: str
    source_type: str
    source_id: str
    prompt_text: str
    profile_id: str = ""
    template_id: str = ""
    parameters: dict = field(default_factory=dict)
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "provider_id": self.provider_id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "prompt_text": self.prompt_text,
            "profile_id": self.profile_id,
            "template_id": self.template_id,
            "parameters": dict(self.parameters),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Any) -> "ProviderRequest":
        return cls(
            request_id=str(data["request_id"]),
            provider_id=str(data["provider_id"]),
            source_type=str(data.get("source_type", "")),
            source_id=str(data.get("source_id", "")),
            prompt_text=str(data["prompt_text"]),
            profile_id=str(data.get("profile_id", "")),
            template_id=str(data.get("template_id", "")),
            parameters=dict(data.get("parameters") or {}),
            created_at=str(data.get("created_at", "")),
        )


@dataclass(frozen=True)
class ProviderResponse:
    """A response from a provider (or dry-run adapter)."""

    response_id: str
    request_id: str
    provider_id: str
    status: str
    output_text: str = ""
    output_artifact_id: str = ""
    error_message: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> "ProviderResponse":
        return cls(
            response_id=str(data["response_id"]),
            request_id=str(data["request_id"]),
            provider_id=str(data["provider_id"]),
            status=str(data["status"]),
            output_text=str(data.get("output_text", "")),
            output_artifact_id=str(data.get("output_artifact_id", "")),
            error_message=str(data.get("error_message", "")),
            created_at=str(data.get("created_at", "")),
        )


# ---------------------------------------------------------------------------
# Provider log entry (added in TASK-000080)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ProviderLogEntry:
    """A sanitized log entry for a provider request/response event."""

    log_id: str
    request_id: str
    response_id: str
    provider_id: str
    event_type: str
    status: str
    source_type: str
    source_id: str
    prompt_preview: str = ""
    output_preview: str = ""
    error_message: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> "ProviderLogEntry":
        return cls(
            log_id=str(data["log_id"]),
            request_id=str(data["request_id"]),
            response_id=str(data.get("response_id", "")),
            provider_id=str(data["provider_id"]),
            event_type=str(data["event_type"]),
            status=str(data["status"]),
            source_type=str(data.get("source_type", "")),
            source_id=str(data.get("source_id", "")),
            prompt_preview=str(data.get("prompt_preview", "")),
            output_preview=str(data.get("output_preview", "")),
            error_message=str(data.get("error_message", "")),
            created_at=str(data.get("created_at", "")),
        )

# ---------------------------------------------------------------------------
# Provider error types
# ---------------------------------------------------------------------------

PROVIDER_ERROR_TYPES = frozenset({
    "validation_error", "provider_not_configured", "provider_disabled",
    "provider_unavailable", "rate_limited", "network_error",
    "timeout", "blocked", "unknown",
})

RETRYABLE_ERROR_TYPES = frozenset({
    "provider_unavailable", "rate_limited", "network_error", "timeout",
})

NON_RETRYABLE_ERROR_TYPES = frozenset({
    "validation_error", "provider_not_configured",
    "provider_disabled", "blocked", "unknown",
})


@dataclass(frozen=True)
class ProviderError:
    """Normalized error record for provider workflow failures."""

    error_id: str
    provider_id: str
    error_type: str
    message: str
    is_retryable: bool = False
    source_type: str = ""
    source_id: str = ""
    request_id: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> "ProviderError":
        return cls(
            error_id=str(data["error_id"]),
            provider_id=str(data.get("provider_id", "")),
            error_type=str(data.get("error_type", "unknown")),
            message=str(data.get("message", "")),
            is_retryable=bool(data.get("is_retryable", False)),
            source_type=str(data.get("source_type", "")),
            source_id=str(data.get("source_id", "")),
            request_id=str(data.get("request_id", "")),
            created_at=str(data.get("created_at", "")),
        )


# ---------------------------------------------------------------------------
# Provider test connection (added in TASK-000105)
# ---------------------------------------------------------------------------

TEST_CONNECTION_MODES: frozenset[str] = frozenset({
    "dry_run",
    "mock",
    "blocked_real",
})

TEST_CONNECTION_STATUSES: frozenset[str] = frozenset({
    "pass",
    "fail",
    "blocked",
    "not_configured",
})


@dataclass(frozen=True)
class ProviderTestConnectionRequest:
    """A test connection request for a provider (dry/mock only in v0.4)."""

    request_id: str
    provider_id: str
    mode: str = "dry_run"
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "provider_id": self.provider_id,
            "mode": self.mode,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Any) -> "ProviderTestConnectionRequest":
        return cls(
            request_id=str(data["request_id"]),
            provider_id=str(data["provider_id"]),
            mode=str(data.get("mode", "dry_run")),
            created_at=str(data.get("created_at", "")),
        )


@dataclass(frozen=True)
class ProviderTestConnectionResult:
    """Result of a provider test connection (dry/mock only in v0.4)."""

    result_id: str
    request_id: str
    provider_id: str
    mode: str
    status: str
    message: str
    details: dict = field(default_factory=dict)
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "request_id": self.request_id,
            "provider_id": self.provider_id,
            "mode": self.mode,
            "status": self.status,
            "message": self.message,
            "details": dict(self.details),
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Any) -> "ProviderTestConnectionResult":
        return cls(
            result_id=str(data["result_id"]),
            request_id=str(data["request_id"]),
            provider_id=str(data["provider_id"]),
            mode=str(data.get("mode", "dry_run")),
            status=str(data["status"]),
            message=str(data.get("message", "")),
            details=dict(data.get("details") or {}),
            created_at=str(data.get("created_at", "")),
        )

"""Plugin permission contracts for Aurora Studio v0.3.

Defines permission metadata only. No real runtime access is granted.
Standard library dataclasses only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

RISK_LEVELS = frozenset({"low", "medium", "high", "critical"})

PERMISSION_DECISIONS = frozenset({
    "allowed", "denied", "requires_approval", "not_supported",
})

# Permissions that are critical — always denied or require approval
CRITICAL_PERMISSIONS = frozenset({
    "secret_access", "execute_code",
})

HIGH_RISK_PERMISSIONS = frozenset({
    "network_access", "file_system_write", "provider_access",
})


@dataclass(frozen=True)
class PluginPermission:
    """Metadata describing a single plugin permission."""

    permission_id: str
    name: str
    description: str
    risk_level: str
    default_decision: str
    requires_user_approval: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> "PluginPermission":
        return cls(
            permission_id=str(data["permission_id"]),
            name=str(data["name"]),
            description=str(data.get("description", "")),
            risk_level=str(data.get("risk_level", "low")),
            default_decision=str(data.get("default_decision", "denied")),
            requires_user_approval=bool(data.get("requires_user_approval", False)),
        )


@dataclass(frozen=True)
class PluginPermissionDecision:
    """The evaluated decision for a single permission request."""

    permission: str
    decision: str
    risk_level: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PluginCapability:
    """Metadata for a plugin capability."""

    capability_id: str
    name: str
    description: str
    required_permissions: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "description": self.description,
            "required_permissions": list(self.required_permissions),
        }

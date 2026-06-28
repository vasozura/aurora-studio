"""Plugin permission model for Aurora Studio v0.3.

Defines known permissions and evaluates requests.
No real access is granted. This is metadata only.
"""

from __future__ import annotations

from typing import Any

from aurora_studio.contracts.plugin_permission import (
    CRITICAL_PERMISSIONS,
    HIGH_RISK_PERMISSIONS,
    PluginCapability,
    PluginPermission,
    PluginPermissionDecision,
)

# ---------------------------------------------------------------------------
# Registry of known permissions
# ---------------------------------------------------------------------------

_KNOWN_PERMISSIONS: list[PluginPermission] = [
    PluginPermission("read_project_metadata", "read_project_metadata", "Read project name, description and settings.", "low", "allowed", False),
    PluginPermission("read_scenes", "read_scenes", "Read scene list and details.", "low", "allowed", False),
    PluginPermission("read_shots", "read_shots", "Read shot list and details.", "low", "allowed", False),
    PluginPermission("read_assets", "read_assets", "Read asset metadata.", "low", "allowed", False),
    PluginPermission("read_characters", "read_characters", "Read character list and details.", "low", "allowed", False),
    PluginPermission("write_export_artifact", "write_export_artifact", "Write an export artifact to the project.", "medium", "requires_approval", True),
    PluginPermission("read_prompt_templates", "read_prompt_templates", "Read prompt templates.", "low", "allowed", False),
    PluginPermission("network_access", "network_access", "Make network requests to external services.", "high", "denied", True),
    PluginPermission("file_system_read", "file_system_read", "Read local filesystem paths.", "medium", "requires_approval", True),
    PluginPermission("file_system_write", "file_system_write", "Write to local filesystem paths.", "high", "denied", True),
    PluginPermission("provider_access", "provider_access", "Access provider adapters and execute prompts.", "high", "denied", True),
    PluginPermission("secret_access", "secret_access", "Access stored API keys or secrets.", "critical", "denied", True),
    PluginPermission("execute_code", "execute_code", "Execute arbitrary code.", "critical", "denied", True),
]

_PERMISSION_MAP: dict[str, PluginPermission] = {p.name: p for p in _KNOWN_PERMISSIONS}


class PluginPermissionModel:
    """In-memory plugin permission model.

    No real runtime enforcement. Metadata and policy only.
    """

    def list_known_permissions(self) -> list[PluginPermission]:
        return list(_KNOWN_PERMISSIONS)

    def get_permission(self, name: str) -> PluginPermission | None:
        return _PERMISSION_MAP.get(name)

    def is_permission_supported(self, name: str) -> bool:
        return name in _PERMISSION_MAP

    def is_permission_allowed_by_default(self, name: str) -> bool:
        perm = _PERMISSION_MAP.get(name)
        if perm is None:
            return False
        return perm.default_decision == "allowed"

    def evaluate_requested_permissions(
        self, permission_names: list[str]
    ) -> list[PluginPermissionDecision]:
        """Evaluate a list of permission requests. Returns decisions."""
        decisions: list[PluginPermissionDecision] = []
        for name in permission_names:
            perm = _PERMISSION_MAP.get(name)
            if perm is None:
                decisions.append(PluginPermissionDecision(
                    permission=name,
                    decision="not_supported",
                    risk_level="unknown",
                    message=f"Permission {name!r} is not a known permission.",
                ))
            else:
                decisions.append(PluginPermissionDecision(
                    permission=name,
                    decision=perm.default_decision,
                    risk_level=perm.risk_level,
                    message=self._decision_message(perm),
                ))
        return decisions

    def _decision_message(self, perm: PluginPermission) -> str:
        if perm.default_decision == "allowed":
            return f"{perm.name!r} is allowed by default (risk: {perm.risk_level})."
        if perm.default_decision == "requires_approval":
            return f"{perm.name!r} requires explicit user approval (risk: {perm.risk_level})."
        return f"{perm.name!r} is denied by default (risk: {perm.risk_level})."

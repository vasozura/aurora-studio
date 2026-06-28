"""Plugin manifest validator for Aurora Studio v0.3.

Validates plugin manifest metadata only.
Never imports, executes, or loads plugin code.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.plugin import (
    PluginManifest,
    PluginManifestValidationIssue,
    PluginManifestValidationReport,
)

_SAFE_ID_RE = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
_REQUIRED_FIELDS = ("plugin_id", "name", "version", "manifest_version")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _issue(level: str, code: str, message: str, field: str = "") -> PluginManifestValidationIssue:
    return PluginManifestValidationIssue(level=level, code=code, message=message, field=field)


class PluginManifestValidator:
    """Validates plugin manifests without executing any code."""

    def list_required_fields(self) -> list[str]:
        return list(_REQUIRED_FIELDS)

    def normalize_manifest(self, data: Any) -> PluginManifest:
        """Convert a raw dict into a PluginManifest, normalizing types."""
        if not isinstance(data, dict):
            data = {}
        now = _utc_now()
        return PluginManifest(
            plugin_id=str(data.get("plugin_id", "")).strip(),
            name=str(data.get("name", "")).strip(),
            version=str(data.get("version", "")).strip(),
            description=str(data.get("description", "")),
            entry_point=str(data.get("entry_point", "")),
            author=str(data.get("author", "")),
            capabilities=tuple(str(c) for c in (data.get("capabilities") or [])),
            permissions=tuple(str(p) for p in (data.get("permissions") or [])),
            state=str(data.get("state", "registered")),
            manifest_version=str(data.get("manifest_version", "")).strip(),
            created_at=str(data.get("created_at", now)),
            updated_at=str(data.get("updated_at", now)),
        )

    def validate_manifest_dict(self, data: Any) -> PluginManifestValidationReport:
        """Validate a raw dict. Returns a PluginManifestValidationReport."""
        issues: list[PluginManifestValidationIssue] = []

        if not isinstance(data, dict):
            issues.append(_issue("ERROR", "INVALID_FORMAT", "Manifest must be a JSON object."))
            return PluginManifestValidationReport(
                status="fail", issue_count=len(issues), issues=tuple(issues)
            )

        # Required fields
        for field in _REQUIRED_FIELDS:
            val = data.get(field, "")
            if not str(val).strip():
                issues.append(_issue("ERROR", f"MISSING_{field.upper()}", f"{field!r} is required and must not be empty.", field=field))

        # Safe characters in plugin_id
        pid = str(data.get("plugin_id", "")).strip()
        if pid and not _SAFE_ID_RE.match(pid):
            issues.append(_issue("ERROR", "UNSAFE_PLUGIN_ID", f"plugin_id {pid!r} contains unsafe characters. Use only [a-zA-Z0-9_\\-.].", field="plugin_id"))

        # List-like fields
        for list_field in ("capabilities", "permissions"):
            val = data.get(list_field)
            if val is not None and not isinstance(val, (list, tuple)):
                issues.append(_issue("ERROR", f"INVALID_{list_field.upper()}_TYPE", f"{list_field!r} must be a list.", field=list_field))

        # Entry point is metadata only — warn if present but never execute
        ep = str(data.get("entry_point", "")).strip()
        if ep:
            issues.append(_issue("INFO", "ENTRY_POINT_METADATA_ONLY", "entry_point is stored as metadata. It is never imported or executed.", field="entry_point"))

        normalized = self.normalize_manifest(data)

        # Determine status
        levels = {i.level for i in issues}
        if "ERROR" in levels:
            status = "fail"
        elif "WARN" in levels:
            status = "warn"
        else:
            status = "pass"

        return PluginManifestValidationReport(
            status=status,
            issue_count=len(issues),
            issues=tuple(issues),
            normalized_manifest=normalized if status != "fail" else None,
        )

    def validate_manifest(self, manifest: PluginManifest) -> PluginManifestValidationReport:
        """Validate an existing PluginManifest object."""
        return self.validate_manifest_dict(manifest.to_dict())

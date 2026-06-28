"""Plugin contract placeholders and first minimal plugin metadata contract."""

from dataclasses import asdict, dataclass, replace
from typing import Any

PLUGIN_STATE_DISCOVERED = "discovered"
PLUGIN_STATE_ENABLED = "enabled"
PLUGIN_STATE_DISABLED = "disabled"
PLUGIN_STATE_INVALID = "invalid"


@dataclass(frozen=True)
class PluginMetadata:
    """Minimal plugin metadata contract.

    This tracks plugin registration only.
    It does not implement plugin loading, execution or permission enforcement.
    """

    plugin_id: str
    name: str
    version: str
    capabilities: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    state: str = PLUGIN_STATE_DISCOVERED

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable plugin metadata."""

        return asdict(self)

    def with_updates(self, **changes: Any) -> "PluginMetadata":
        """Return a new metadata record with selected fields changed."""

        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PluginMetadata":
        """Create plugin metadata from JSON-like data."""

        required = ("plugin_id", "name", "version")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"PluginMetadata missing required keys: {', '.join(missing)}")

        return cls(
            plugin_id=str(data["plugin_id"]),
            name=str(data["name"]),
            version=str(data["version"]),
            capabilities=tuple(str(c) for c in data.get("capabilities", [])),
            permissions=tuple(str(p) for p in data.get("permissions", [])),
            state=str(data.get("state", PLUGIN_STATE_DISCOVERED)),
        )

# ---------------------------------------------------------------------------
# Plugin manifest (TASK-000086)
# ---------------------------------------------------------------------------

PLUGIN_STATES = frozenset({
    "registered", "disabled", "enabled_metadata_only", "invalid", "blocked",
})

MANIFEST_ISSUE_LEVELS = frozenset({"INFO", "WARN", "ERROR"})

MANIFEST_STATUSES = frozenset({"pass", "warn", "fail"})


@dataclass(frozen=True)
class PluginManifest:
    """Full plugin manifest — metadata only, never executed."""

    plugin_id: str
    name: str
    version: str
    description: str = ""
    entry_point: str = ""
    author: str = ""
    capabilities: tuple = ()
    permissions: tuple = ()
    state: str = "registered"
    manifest_version: str = "1.0"
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "plugin_id": self.plugin_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "entry_point": self.entry_point,
            "author": self.author,
            "capabilities": list(self.capabilities),
            "permissions": list(self.permissions),
            "state": self.state,
            "manifest_version": self.manifest_version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def with_updates(self, **changes: Any) -> "PluginManifest":
        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: Any) -> "PluginManifest":
        return cls(
            plugin_id=str(data.get("plugin_id", "")),
            name=str(data.get("name", "")),
            version=str(data.get("version", "")),
            description=str(data.get("description", "")),
            entry_point=str(data.get("entry_point", "")),
            author=str(data.get("author", "")),
            capabilities=tuple(str(c) for c in data.get("capabilities", [])),
            permissions=tuple(str(p) for p in data.get("permissions", [])),
            state=str(data.get("state", "registered")),
            manifest_version=str(data.get("manifest_version", "1.0")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )


@dataclass(frozen=True)
class PluginManifestValidationIssue:
    """A single validation issue found in a plugin manifest."""

    level: str
    code: str
    message: str
    field: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PluginManifestValidationReport:
    """Result of validating a plugin manifest."""

    status: str
    issue_count: int
    issues: tuple[PluginManifestValidationIssue, ...]
    normalized_manifest: PluginManifest | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "issue_count": self.issue_count,
            "issues": [i.to_dict() for i in self.issues],
            "normalized_manifest": self.normalized_manifest.to_dict() if self.normalized_manifest else None,
        }


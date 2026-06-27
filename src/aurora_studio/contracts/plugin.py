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

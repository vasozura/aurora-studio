"""Plugin contract placeholders."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PluginMetadata:
    """Placeholder plugin metadata contract."""

    plugin_id: str
    name: str
    version: str
    enabled: bool = False

"""Plugin Manager first minimal implementation."""

from __future__ import annotations

from aurora_studio.contracts.plugin import (
    PLUGIN_STATE_DISABLED,
    PLUGIN_STATE_DISCOVERED,
    PLUGIN_STATE_ENABLED,
    PluginMetadata,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id
from aurora_studio.core.readiness import Readiness


class PluginManager:
    """Minimal Plugin Manager implementation.

    This class tracks only in-memory plugin metadata.

    It does not implement:
    - Plugin code loading
    - Plugin execution
    - Plugin sandboxing
    - Permission enforcement
    - Provider SDK imports
    - Database persistence
    - GUI behavior
    """

    module_name = "Plugin Manager"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._plugins: dict[str, PluginMetadata] = {}

    def get_readiness(self) -> Readiness:
        """Return module readiness."""

        return self.readiness

    def describe(self) -> str:
        """Return a short implementation description."""

        return (
            "Plugin Manager supports minimal in-memory plugin metadata tracking "
            "and remains not ready for full product implementation."
        )

    def register_plugin(
        self,
        name: str,
        version: str,
        capabilities: list[str] | tuple[str, ...] | None = None,
        permissions: list[str] | tuple[str, ...] | None = None,
    ) -> PluginMetadata:
        """Register a plugin by metadata only.

        This does not load or execute plugin code.
        """

        clean_name = self._validate_required_ref(name, "name")
        clean_version = self._validate_required_ref(version, "version")

        plugin = PluginMetadata(
            plugin_id=new_id("plugin"),
            name=clean_name,
            version=clean_version,
            capabilities=tuple(capabilities) if capabilities is not None else (),
            permissions=tuple(permissions) if permissions is not None else (),
            state=PLUGIN_STATE_DISCOVERED,
        )
        self._plugins[plugin.plugin_id] = plugin
        return plugin

    def list_plugins(self, state: str | None = None) -> list[PluginMetadata]:
        """List plugin metadata, optionally filtered by state."""

        plugins = list(self._plugins.values())
        if state is not None:
            plugins = [p for p in plugins if p.state == state]
        return plugins

    def get_plugin(self, plugin_id: str) -> PluginMetadata:
        """Return plugin metadata by ID."""

        clean_plugin_id = self._validate_required_ref(plugin_id, "plugin_id")
        try:
            return self._plugins[clean_plugin_id]
        except KeyError as exc:
            raise ValidationError(f"Plugin not found: {clean_plugin_id}") from exc

    def enable_plugin(self, plugin_id: str) -> PluginMetadata:
        """Enable a plugin by updating its state metadata."""

        plugin = self.get_plugin(plugin_id)
        updated = plugin.with_updates(state=PLUGIN_STATE_ENABLED)
        self._plugins[updated.plugin_id] = updated
        return updated

    def disable_plugin(self, plugin_id: str) -> PluginMetadata:
        """Disable a plugin by updating its state metadata."""

        plugin = self.get_plugin(plugin_id)
        updated = plugin.with_updates(state=PLUGIN_STATE_DISABLED)
        self._plugins[updated.plugin_id] = updated
        return updated

    def get_plugin_capabilities(self, plugin_id: str) -> tuple[str, ...]:
        """Return capabilities tuple for a plugin."""

        return self.get_plugin(plugin_id).capabilities

    def get_plugin_permissions(self, plugin_id: str) -> tuple[str, ...]:
        """Return permissions tuple for a plugin."""

        return self.get_plugin(plugin_id).permissions

    def _validate_required_ref(self, value: str, field_name: str) -> str:
        """Validate a required reference-like string."""

        clean_value = value.strip()
        if not clean_value:
            raise ValidationError(f"{field_name} must not be empty.")
        return clean_value

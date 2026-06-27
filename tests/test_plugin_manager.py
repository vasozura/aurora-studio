"""Tests for the first minimal Plugin Manager implementation."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.contracts.plugin import (
    PLUGIN_STATE_DISABLED,
    PLUGIN_STATE_DISCOVERED,
    PLUGIN_STATE_ENABLED,
    PluginMetadata,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.readiness import Readiness
from aurora_studio.modules.plugin_manager import PluginManager


class PluginManagerImplementationTests(unittest.TestCase):
    def test_register_plugin_returns_metadata(self) -> None:
        manager = PluginManager()

        plugin = manager.register_plugin("my-plugin", "1.0.0")

        self.assertIsInstance(plugin, PluginMetadata)
        self.assertTrue(plugin.plugin_id.startswith("plugin-"))
        self.assertEqual(plugin.name, "my-plugin")
        self.assertEqual(plugin.version, "1.0.0")
        self.assertEqual(plugin.state, PLUGIN_STATE_DISCOVERED)
        self.assertEqual(plugin.capabilities, ())
        self.assertEqual(plugin.permissions, ())

    def test_register_plugin_with_capabilities_and_permissions(self) -> None:
        manager = PluginManager()

        plugin = manager.register_plugin(
            "my-plugin", "1.0.0",
            capabilities=["export", "import"],
            permissions=["read_scenes"],
        )

        self.assertEqual(plugin.capabilities, ("export", "import"))
        self.assertEqual(plugin.permissions, ("read_scenes",))

    def test_register_plugin_default_empty_capabilities(self) -> None:
        manager = PluginManager()

        plugin = manager.register_plugin("my-plugin", "1.0.0")

        self.assertEqual(plugin.capabilities, ())
        self.assertEqual(plugin.permissions, ())

    def test_register_plugin_rejects_empty_name(self) -> None:
        manager = PluginManager()

        with self.assertRaises(ValidationError):
            manager.register_plugin("   ", "1.0.0")

    def test_register_plugin_rejects_empty_version(self) -> None:
        manager = PluginManager()

        with self.assertRaises(ValidationError):
            manager.register_plugin("my-plugin", "   ")

    def test_list_plugins_all_and_by_state(self) -> None:
        manager = PluginManager()
        a = manager.register_plugin("plugin-a", "1.0.0")
        b = manager.register_plugin("plugin-b", "2.0.0")
        manager.enable_plugin(a.plugin_id)

        all_plugins = manager.list_plugins()
        enabled_plugins = manager.list_plugins(PLUGIN_STATE_ENABLED)
        discovered_plugins = manager.list_plugins(PLUGIN_STATE_DISCOVERED)

        self.assertEqual(len(all_plugins), 2)
        self.assertEqual(len(enabled_plugins), 1)
        self.assertEqual(enabled_plugins[0].plugin_id, a.plugin_id)
        self.assertEqual(len(discovered_plugins), 1)
        self.assertEqual(discovered_plugins[0].plugin_id, b.plugin_id)

    def test_get_plugin_returns_existing(self) -> None:
        manager = PluginManager()
        registered = manager.register_plugin("my-plugin", "1.0.0")

        fetched = manager.get_plugin(registered.plugin_id)

        self.assertEqual(fetched.plugin_id, registered.plugin_id)

    def test_get_plugin_rejects_missing(self) -> None:
        manager = PluginManager()

        with self.assertRaises(ValidationError):
            manager.get_plugin("plugin-missing")

    def test_enable_plugin_changes_state(self) -> None:
        manager = PluginManager()
        registered = manager.register_plugin("my-plugin", "1.0.0")

        enabled = manager.enable_plugin(registered.plugin_id)

        self.assertEqual(enabled.state, PLUGIN_STATE_ENABLED)

    def test_disable_plugin_changes_state(self) -> None:
        manager = PluginManager()
        registered = manager.register_plugin("my-plugin", "1.0.0")
        manager.enable_plugin(registered.plugin_id)

        disabled = manager.disable_plugin(registered.plugin_id)

        self.assertEqual(disabled.state, PLUGIN_STATE_DISABLED)

    def test_get_plugin_capabilities(self) -> None:
        manager = PluginManager()
        registered = manager.register_plugin("my-plugin", "1.0.0", capabilities=["export"])

        caps = manager.get_plugin_capabilities(registered.plugin_id)

        self.assertEqual(caps, ("export",))

    def test_get_plugin_permissions(self) -> None:
        manager = PluginManager()
        registered = manager.register_plugin("my-plugin", "1.0.0", permissions=["read_scenes"])

        perms = manager.get_plugin_permissions(registered.plugin_id)

        self.assertEqual(perms, ("read_scenes",))

    def test_plugin_metadata_to_dict(self) -> None:
        manager = PluginManager()
        plugin = manager.register_plugin("my-plugin", "1.0.0", capabilities=["export"])

        data = plugin.to_dict()

        self.assertEqual(data["plugin_id"], plugin.plugin_id)
        self.assertEqual(data["name"], "my-plugin")
        self.assertEqual(data["state"], PLUGIN_STATE_DISCOVERED)

    def test_plugin_metadata_from_dict(self) -> None:
        manager = PluginManager()
        plugin = manager.register_plugin("my-plugin", "1.0.0", capabilities=["export"])

        restored = PluginMetadata.from_dict(plugin.to_dict())

        self.assertEqual(restored.plugin_id, plugin.plugin_id)
        self.assertEqual(restored.name, "my-plugin")
        self.assertEqual(restored.capabilities, ("export",))

    def test_plugin_manager_still_reports_not_ready(self) -> None:
        manager = PluginManager()

        self.assertEqual(manager.get_readiness(), Readiness.NOT_READY)
        self.assertIn("not ready", manager.describe().lower())


if __name__ == "__main__":
    unittest.main()

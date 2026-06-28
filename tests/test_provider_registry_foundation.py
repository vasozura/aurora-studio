"""Tests for TASK-000077: Provider Registry Foundation."""

import json
import unittest


def _make_registry():
    from aurora_studio.modules.provider_registry import ProviderRegistry
    return ProviderRegistry()


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


class TestProviderDefinitionSerialization(unittest.TestCase):
    def test_to_dict_json_serializable(self):
        from aurora_studio.contracts.provider import ProviderDefinition, ProviderCapability
        defn = ProviderDefinition(
            provider_id="test-p1",
            name="Test Provider",
            version="1.0",
            provider_type="text",
            capabilities=(ProviderCapability("text", "text gen"),),
        )
        d = defn.to_dict()
        json.dumps(d)  # must not raise

    def test_from_dict_roundtrip(self):
        from aurora_studio.contracts.provider import ProviderDefinition, ProviderCapability
        defn = ProviderDefinition(
            provider_id="test-p2",
            name="Round Trip",
            version="0.1",
            provider_type="image",
            capabilities=(ProviderCapability("image", "img gen"),),
        )
        restored = ProviderDefinition.from_dict(defn.to_dict())
        self.assertEqual(restored.provider_id, defn.provider_id)
        self.assertEqual(restored.name, defn.name)
        self.assertEqual(len(restored.capabilities), 1)


class TestRegistryBuiltInDryRun(unittest.TestCase):
    def test_dry_run_provider_always_present(self):
        reg = _make_registry()
        from aurora_studio.contracts.provider import DRY_RUN_PROVIDER_ID
        defn = reg.get_provider(DRY_RUN_PROVIDER_ID)
        self.assertEqual(defn.provider_id, DRY_RUN_PROVIDER_ID)

    def test_dry_run_provider_state_available(self):
        reg = _make_registry()
        from aurora_studio.contracts.provider import DRY_RUN_PROVIDER_ID
        defn = reg.get_provider(DRY_RUN_PROVIDER_ID)
        self.assertEqual(defn.state, "available")

    def test_dry_run_provider_no_api_key_required(self):
        reg = _make_registry()
        from aurora_studio.contracts.provider import DRY_RUN_PROVIDER_ID
        defn = reg.get_provider(DRY_RUN_PROVIDER_ID)
        self.assertFalse(defn.requires_api_key)


class TestRegisterProvider(unittest.TestCase):
    def test_register_provider(self):
        from aurora_studio.contracts.provider import ProviderDefinition
        reg = _make_registry()
        defn = ProviderDefinition(
            provider_id="custom-p1",
            name="Custom",
            version="1.0",
            provider_type="text",
        )
        result = reg.register_provider(defn)
        self.assertEqual(result.provider_id, "custom-p1")

    def test_register_invalid_type_raises(self):
        from aurora_studio.contracts.provider import ProviderDefinition
        from aurora_studio.core.errors import ValidationError
        reg = _make_registry()
        defn = ProviderDefinition(
            provider_id="bad-p",
            name="Bad",
            version="1.0",
            provider_type="quantum",
        )
        with self.assertRaises(ValidationError):
            reg.register_provider(defn)

    def test_register_empty_id_raises(self):
        from aurora_studio.contracts.provider import ProviderDefinition
        from aurora_studio.core.errors import ValidationError
        reg = _make_registry()
        defn = ProviderDefinition(
            provider_id="  ",
            name="Empty ID",
            version="1.0",
            provider_type="text",
        )
        with self.assertRaises(ValidationError):
            reg.register_provider(defn)


class TestListProviders(unittest.TestCase):
    def setUp(self):
        from aurora_studio.contracts.provider import ProviderDefinition
        self.reg = _make_registry()
        self.reg.register_provider(ProviderDefinition("img-p", "Image", "1.0", "image"))
        self.reg.register_provider(ProviderDefinition("txt-p", "Text", "1.0", "text"))

    def test_list_all(self):
        providers = self.reg.list_providers()
        self.assertGreaterEqual(len(providers), 3)

    def test_filter_by_type(self):
        providers = self.reg.list_providers(provider_type="image")
        self.assertTrue(all(p.provider_type == "image" for p in providers))

    def test_filter_by_state(self):
        providers = self.reg.list_providers(state="available")
        self.assertTrue(all(p.state == "available" for p in providers))


class TestEnableDisable(unittest.TestCase):
    def test_enable_provider(self):
        from aurora_studio.contracts.provider import ProviderDefinition
        reg = _make_registry()
        reg.register_provider(ProviderDefinition("en-p", "Enable", "1.0", "text", state="disabled"))
        updated = reg.enable_provider("en-p")
        self.assertEqual(updated.state, "available")

    def test_disable_provider(self):
        from aurora_studio.contracts.provider import ProviderDefinition
        reg = _make_registry()
        reg.register_provider(ProviderDefinition("dis-p", "Disable", "1.0", "text", state="available"))
        updated = reg.disable_provider("dis-p")
        self.assertEqual(updated.state, "disabled")


class TestProviderError(unittest.TestCase):
    def test_mark_error(self):
        from aurora_studio.contracts.provider import ProviderDefinition
        reg = _make_registry()
        reg.register_provider(ProviderDefinition("err-p", "Error", "1.0", "text"))
        updated = reg.mark_provider_error("err-p", "Something went wrong")
        self.assertEqual(updated.state, "error")
        self.assertEqual(updated.error_message, "Something went wrong")

    def test_clear_error(self):
        from aurora_studio.contracts.provider import ProviderDefinition
        reg = _make_registry()
        reg.register_provider(ProviderDefinition("clr-p", "Clear", "1.0", "text", state="error", error_message="oops"))
        updated = reg.clear_provider_error("clr-p")
        self.assertNotEqual(updated.state, "error")
        self.assertEqual(updated.error_message, "")


class TestListCapabilities(unittest.TestCase):
    def test_list_capabilities(self):
        from aurora_studio.contracts.provider import DRY_RUN_PROVIDER_ID
        reg = _make_registry()
        caps = reg.list_capabilities(DRY_RUN_PROVIDER_ID)
        self.assertGreater(len(caps), 0)
        for c in caps:
            self.assertIsInstance(c.name, str)


class TestUISessionProviderMethods(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()

    def test_list_providers_ok(self):
        r = self.sess.list_providers()
        self.assertTrue(r.ok, r.message)
        self.assertIn("providers", r.payload)

    def test_list_providers_json_serializable(self):
        r = self.sess.list_providers()
        self.assertTrue(r.ok)
        json.dumps(r.payload)

    def test_get_provider_ok(self):
        r = self.sess.get_provider("dry-run-local")
        self.assertTrue(r.ok, r.message)
        self.assertEqual(r.payload["provider"]["provider_id"], "dry-run-local")

    def test_get_provider_unknown_fails(self):
        r = self.sess.get_provider("nonexistent-provider")
        self.assertFalse(r.ok)

    def test_enable_provider_ok(self):
        r = self.sess.enable_provider("dry-run-local")
        self.assertTrue(r.ok, r.message)

    def test_disable_provider_ok(self):
        r = self.sess.disable_provider("dry-run-local")
        self.assertTrue(r.ok, r.message)
        self.assertEqual(r.payload["state"], "disabled")

    def test_filter_by_type(self):
        r = self.sess.list_providers(provider_type="dry_run")
        self.assertTrue(r.ok)
        for p in r.payload["providers"]:
            self.assertEqual(p["provider_type"], "dry_run")


class TestDesktopProviderMethods(unittest.TestCase):
    def test_refresh_providers_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "refresh_providers"))

    def test_enable_provider_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "enable_provider"))

    def test_disable_provider_method_exists(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        self.assertTrue(hasattr(DesktopShell, "disable_provider"))


class TestNoProviderSDKRequired(unittest.TestCase):
    def test_provider_registry_importable_without_sdk(self):
        # Must not raise even without openai/anthropic etc.
        from aurora_studio.modules.provider_registry import ProviderRegistry
        reg = ProviderRegistry()
        self.assertIsNotNone(reg)

    def test_provider_contracts_importable_without_sdk(self):
        from aurora_studio.contracts.provider import (
            ProviderDefinition, ProviderCapability, ProviderStatus,
        )
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()

"""Tests for TASK-000104: Provider Config UI Hardening.

No network calls. No provider SDK. Standard library only.
"""

import json
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"


class TestProviderConfigManager(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_config_manager import ProviderConfigManager
        self.mgr = ProviderConfigManager()

    def test_set_and_get_config_metadata(self):
        result = self.mgr.set_provider_config_metadata(
            "openai", display_name="OpenAI", provider_type="text"
        )
        self.assertEqual(result["provider_id"], "openai")
        self.assertEqual(result["display_name"], "OpenAI")

    def test_real_execution_allowed_defaults_false(self):
        result = self.mgr.set_provider_config_metadata("openai")
        self.assertFalse(result["real_execution_allowed"])

    def test_real_execution_allowed_cannot_be_set_true(self):
        result = self.mgr.set_provider_config_metadata(
            "openai", real_execution_allowed=True
        )
        self.assertFalse(result["real_execution_allowed"])

    def test_secret_fields_stripped_from_metadata(self):
        result = self.mgr.set_provider_config_metadata(
            "openai", api_key="real-secret", display_name="OpenAI"
        )
        self.assertNotIn("api_key", result)
        self.assertIn("display_name", result)

    def test_config_metadata_serializes_to_json(self):
        self.mgr.set_provider_config_metadata("openai", display_name="OpenAI")
        record = self.mgr.get_provider_config_metadata("openai")
        serialized = json.dumps(record)
        parsed = json.loads(serialized)
        self.assertFalse(parsed["real_execution_allowed"])

    def test_secret_storage_status_serializes(self):
        result = self.mgr.set_secret_storage_status("openai", "planned")
        self.assertEqual(result["secret_storage_status"], "planned")

    def test_invalid_secret_storage_status_normalized(self):
        result = self.mgr.set_secret_storage_status("openai", "nonsense_status")
        self.assertEqual(result["secret_storage_status"], "not_configured")

    def test_set_provider_enabled(self):
        self.mgr.set_provider_config_metadata("openai")
        result = self.mgr.set_provider_enabled("openai", True)
        self.assertTrue(result["enabled"])

    def test_set_provider_disabled(self):
        result = self.mgr.set_provider_enabled("openai", False)
        self.assertFalse(result["enabled"])

    def test_set_real_execution_allowed_returns_blocked(self):
        result = self.mgr.set_real_execution_allowed("openai", True)
        self.assertFalse(result["real_execution_allowed"])

    def test_build_safe_config_snapshot_no_secret_fields(self):
        self.mgr.set_provider_config_metadata(
            "openai", display_name="OpenAI"
        )
        # Manually inject a secret-like key (simulate a bug) to verify it gets stripped
        self.mgr._configs["openai"]["api_key"] = "leak"
        snapshot = self.mgr.build_safe_config_snapshot("openai")
        self.assertNotIn("api_key", snapshot)

    def test_build_safe_config_snapshot_missing_provider(self):
        snapshot = self.mgr.build_safe_config_snapshot("unknown")
        self.assertEqual(snapshot["config_status"], "not_configured")

    def test_list_provider_config_metadata(self):
        self.mgr.set_provider_config_metadata("openai")
        self.mgr.set_provider_config_metadata("anthropic")
        records = self.mgr.list_provider_config_metadata()
        ids = [r["provider_id"] for r in records]
        self.assertIn("openai", ids)
        self.assertIn("anthropic", ids)

    def test_empty_provider_id_raises(self):
        with self.assertRaises(ValueError):
            self.mgr.set_provider_config_metadata("")


class TestProviderConfigViewModel(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.ui.view_models import ProviderConfigViewModel
        self.cls = ProviderConfigViewModel

    def test_from_record_dict(self):
        vm = self.cls.from_record({
            "provider_id": "openai",
            "enabled": True,
            "config_status": "not_configured",
        })
        self.assertEqual(vm.provider_id, "openai")
        self.assertTrue(vm.enabled)

    def test_real_execution_allowed_always_false(self):
        vm = self.cls.from_record({"provider_id": "openai", "real_execution_allowed": True})
        self.assertFalse(vm.real_execution_allowed)

    def test_to_dict_json_serializable(self):
        vm = self.cls(provider_id="openai", config_status="not_configured")
        serialized = json.dumps(vm.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["real_execution_allowed"])

    def test_to_dict_no_secret_fields(self):
        vm = self.cls(provider_id="openai")
        d = vm.to_dict()
        self.assertNotIn("api_key", d)
        self.assertNotIn("token", d)
        self.assertNotIn("secret", d)


class TestUISessionProviderConfig(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_get_provider_config_ui_state_ok(self):
        result = self.sess.get_provider_config_ui_state("openai")
        self.assertTrue(result.ok)

    def test_get_provider_config_ui_state_json_serializable(self):
        result = self.sess.get_provider_config_ui_state("openai")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["payload"]["real_execution_allowed"])

    def test_list_provider_config_ui_states_ok(self):
        self.sess.update_provider_config_metadata("openai", {"display_name": "OpenAI"})
        result = self.sess.list_provider_config_ui_states()
        self.assertTrue(result.ok)
        self.assertIn("providers", result.payload)

    def test_update_provider_config_metadata_ok(self):
        result = self.sess.update_provider_config_metadata(
            "openai", {"display_name": "OpenAI", "provider_type": "text"}
        )
        self.assertTrue(result.ok)

    def test_update_strips_secret_fields(self):
        result = self.sess.update_provider_config_metadata(
            "openai", {"api_key": "secret", "display_name": "OpenAI"}
        )
        self.assertTrue(result.ok)
        self.assertNotIn("api_key", result.payload)

    def test_set_provider_enabled_ok(self):
        result = self.sess.set_provider_enabled("openai", True)
        self.assertTrue(result.ok)
        self.assertTrue(result.payload["enabled"])

    def test_set_provider_secret_storage_status_ok(self):
        result = self.sess.set_provider_secret_storage_status("openai", "planned")
        self.assertTrue(result.ok)

    def test_request_real_execution_enable_blocked(self):
        result = self.sess.request_real_execution_enable("openai")
        self.assertFalse(result.ok)
        self.assertIn("blocked" if "blocked" in result.message.lower() else "cannot", result.message.lower())

    def test_dry_run_provider_remains_usable(self):
        # dry-run provider registration should still work
        from aurora_studio.modules.provider_registry import ProviderRegistry
        reg = ProviderRegistry()
        providers = reg.list_providers()
        dry_run_ids = [p.provider_id for p in providers]
        self.assertTrue(any("dry" in pid.lower() for pid in dry_run_ids))


class TestProjectBundleNoBundledSecrets(unittest.TestCase):

    def test_bundle_save_does_not_include_secret_fields(self):
        import sys; sys.path.insert(0, str(SRC))
        import tempfile, json
        from aurora_studio.ui.actions import UISession
        sess = UISession()
        with tempfile.TemporaryDirectory() as tmp:
            sess.create_project(path=tmp, title="SecretTest")
            bundle_path = str(Path(tmp) / "aurora_project.json")
            sess.save_bundle(path=bundle_path)
            content = json.loads(Path(bundle_path).read_text())
            # Verify no secret-like fields in the bundle
            bundle_str = json.dumps(content).lower()
            self.assertNotIn('"api_key"', bundle_str)
            self.assertNotIn('"token":', bundle_str)
            self.assertNotIn('"password":', bundle_str)


if __name__ == "__main__":
    unittest.main()

"""Tests for TASK-000087: Plugin Permission Model."""

import json
import unittest


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


def _model():
    from aurora_studio.modules.plugin_permission_model import PluginPermissionModel
    return PluginPermissionModel()


ALL_REQUIRED_PERMISSIONS = [
    "read_project_metadata", "read_scenes", "read_shots", "read_assets",
    "read_characters", "write_export_artifact", "read_prompt_templates",
    "network_access", "file_system_read", "file_system_write",
    "provider_access", "secret_access", "execute_code",
]

ALLOWED_BY_DEFAULT = [
    "read_project_metadata", "read_scenes", "read_shots",
    "read_assets", "read_characters", "read_prompt_templates",
]

DENIED_BY_DEFAULT = [
    "network_access", "file_system_write", "provider_access",
    "secret_access", "execute_code",
]

REQUIRES_APPROVAL = [
    "write_export_artifact", "file_system_read",
]


class TestPermissionRegistry(unittest.TestCase):
    def test_all_required_permissions_registered(self):
        model = _model()
        perms = {p.name for p in model.list_known_permissions()}
        for pid in ALL_REQUIRED_PERMISSIONS:
            self.assertIn(pid, perms, f"Missing: {pid}")

    def test_get_permission_returns_correct(self):
        model = _model()
        p = model.get_permission("read_scenes")
        self.assertIsNotNone(p)
        self.assertEqual(p.name, "read_scenes")

    def test_get_unknown_permission_returns_none(self):
        model = _model()
        self.assertIsNone(model.get_permission("nonexistent_perm"))

    def test_is_permission_supported_true(self):
        self.assertTrue(_model().is_permission_supported("read_scenes"))

    def test_is_permission_supported_false(self):
        self.assertFalse(_model().is_permission_supported("unicorn_access"))

    def test_permission_serializable(self):
        model = _model()
        for p in model.list_known_permissions():
            json.dumps(p.to_dict())


class TestAllowedByDefault(unittest.TestCase):
    def test_read_permissions_allowed_by_default(self):
        model = _model()
        for pid in ALLOWED_BY_DEFAULT:
            self.assertTrue(model.is_permission_allowed_by_default(pid), f"Should be allowed: {pid}")

    def test_denied_permissions_not_allowed_by_default(self):
        model = _model()
        for pid in DENIED_BY_DEFAULT:
            self.assertFalse(model.is_permission_allowed_by_default(pid), f"Should be denied: {pid}")

    def test_secret_access_denied(self):
        self.assertFalse(_model().is_permission_allowed_by_default("secret_access"))

    def test_execute_code_denied(self):
        self.assertFalse(_model().is_permission_allowed_by_default("execute_code"))


class TestEvaluatePermissions(unittest.TestCase):
    def test_evaluate_empty_list(self):
        decisions = _model().evaluate_requested_permissions([])
        self.assertEqual(decisions, [])

    def test_evaluate_allowed_permission(self):
        decisions = _model().evaluate_requested_permissions(["read_scenes"])
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0].decision, "allowed")

    def test_evaluate_denied_permission(self):
        decisions = _model().evaluate_requested_permissions(["secret_access"])
        self.assertEqual(decisions[0].decision, "denied")

    def test_evaluate_requires_approval(self):
        decisions = _model().evaluate_requested_permissions(["write_export_artifact"])
        self.assertEqual(decisions[0].decision, "requires_approval")

    def test_evaluate_unknown_permission(self):
        decisions = _model().evaluate_requested_permissions(["unicorn_access"])
        self.assertEqual(decisions[0].decision, "not_supported")

    def test_evaluate_multiple(self):
        decisions = _model().evaluate_requested_permissions(["read_scenes", "secret_access", "unicorn"])
        self.assertEqual(len(decisions), 3)
        by_perm = {d.permission: d.decision for d in decisions}
        self.assertEqual(by_perm["read_scenes"], "allowed")
        self.assertEqual(by_perm["secret_access"], "denied")
        self.assertEqual(by_perm["unicorn"], "not_supported")

    def test_decisions_json_serializable(self):
        decisions = _model().evaluate_requested_permissions(ALL_REQUIRED_PERMISSIONS)
        for d in decisions:
            json.dumps(d.to_dict())

    def test_risk_level_included(self):
        decisions = _model().evaluate_requested_permissions(["secret_access"])
        self.assertEqual(decisions[0].risk_level, "critical")

    def test_read_permissions_low_risk(self):
        decisions = _model().evaluate_requested_permissions(["read_scenes"])
        self.assertEqual(decisions[0].risk_level, "low")


class TestUISessionPermissions(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()

    def test_list_plugin_permissions(self):
        r = self.sess.list_plugin_permissions()
        self.assertTrue(r.ok)
        self.assertGreaterEqual(r.payload["count"], 13)

    def test_list_plugin_permissions_serializable(self):
        r = self.sess.list_plugin_permissions()
        self.assertTrue(r.ok)
        json.dumps(r.payload)

    def test_evaluate_allowed(self):
        r = self.sess.evaluate_plugin_permissions(["read_scenes"])
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["decisions"][0]["decision"], "allowed")

    def test_evaluate_denied(self):
        r = self.sess.evaluate_plugin_permissions(["execute_code"])
        self.assertTrue(r.ok)
        self.assertEqual(r.payload["decisions"][0]["decision"], "denied")

    def test_evaluate_invalid_type(self):
        r = self.sess.evaluate_plugin_permissions("not a list")
        self.assertFalse(r.ok)

    def test_get_plugin_permission_summary_all_allowed(self):
        r = self.sess.get_plugin_permission_summary(["read_scenes", "read_shots"])
        self.assertTrue(r.ok)
        self.assertTrue(r.payload["all_allowed"])

    def test_get_plugin_permission_summary_with_denied(self):
        r = self.sess.get_plugin_permission_summary(["read_scenes", "secret_access"])
        self.assertTrue(r.ok)
        self.assertFalse(r.payload["all_allowed"])
        self.assertIn("secret_access", r.payload["denied"])

    def test_get_plugin_permission_summary_serializable(self):
        r = self.sess.get_plugin_permission_summary(ALL_REQUIRED_PERMISSIONS)
        self.assertTrue(r.ok)
        json.dumps(r.payload)


if __name__ == "__main__":
    unittest.main()

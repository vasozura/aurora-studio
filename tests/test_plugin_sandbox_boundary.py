"""Tests for TASK-000088: Plugin Sandbox Boundary."""

import json
import os
import unittest


def _make_session():
    from aurora_studio.services.application_service import ApplicationService
    from aurora_studio.ui.actions import UISession
    return UISession(ApplicationService())


def _sandbox():
    from aurora_studio.modules.plugin_sandbox import PluginSandbox
    return PluginSandbox()


class TestSandboxDocs(unittest.TestCase):
    BASE = "docs/v0_3"

    def test_sandbox_boundary_doc_exists(self):
        self.assertTrue(os.path.exists(os.path.join(self.BASE, "PLUGIN_SANDBOX_BOUNDARY.md")))

    def test_security_policy_doc_exists(self):
        self.assertTrue(os.path.exists(os.path.join(self.BASE, "PLUGIN_SECURITY_POLICY.md")))

    def test_boundary_doc_states_execution_disabled(self):
        with open(os.path.join(self.BASE, "PLUGIN_SANDBOX_BOUNDARY.md")) as f:
            content = f.read()
        self.assertIn("disabled", content.lower())

    def test_security_policy_states_execute_code_denied(self):
        with open(os.path.join(self.BASE, "PLUGIN_SECURITY_POLICY.md")) as f:
            content = f.read()
        self.assertIn("execute_code", content)

    def test_boundary_states_no_subprocess(self):
        with open(os.path.join(self.BASE, "PLUGIN_SANDBOX_BOUNDARY.md")) as f:
            content = f.read()
        self.assertIn("subprocess", content.lower())

    def test_policy_states_no_secrets_passed(self):
        with open(os.path.join(self.BASE, "PLUGIN_SECURITY_POLICY.md")) as f:
            content = f.read()
        self.assertIn("secret", content.lower())


class TestPluginSandbox(unittest.TestCase):
    def test_execution_always_denied(self):
        self.assertFalse(_sandbox().is_execution_allowed())

    def test_execution_denied_for_any_plugin(self):
        self.assertFalse(_sandbox().is_execution_allowed("plugin-xyz"))

    def test_get_policy_not_allowed(self):
        p = _sandbox().get_policy()
        self.assertFalse(p.allowed)

    def test_get_policy_has_reason(self):
        p = _sandbox().get_policy()
        self.assertIn("disabled", p.reason.lower())

    def test_get_policy_has_version(self):
        p = _sandbox().get_policy()
        self.assertIn("v0.3", p.policy_version)

    def test_policy_result_json_serializable(self):
        p = _sandbox().get_policy()
        json.dumps(p.to_dict())

    def test_sandbox_module_does_not_import_subprocess(self):
        import sys
        import aurora_studio.modules.plugin_sandbox as sb_module
        src = open(sb_module.__file__).read()
        self.assertNotIn("import subprocess", src)

    def test_sandbox_does_not_call_importlib(self):
        import aurora_studio.modules.plugin_sandbox as sb_module
        src = open(sb_module.__file__).read()
        self.assertNotIn("importlib.import_module", src)


class TestUISessionSandbox(unittest.TestCase):
    def setUp(self):
        self.sess = _make_session()

    def test_get_sandbox_policy_ok(self):
        r = self.sess.get_plugin_sandbox_policy()
        self.assertTrue(r.ok)
        self.assertFalse(r.payload["allowed"])

    def test_is_execution_allowed_false(self):
        r = self.sess.is_plugin_execution_allowed("my-plugin")
        self.assertTrue(r.ok)
        self.assertFalse(r.payload["allowed"])

    def test_sandbox_payload_serializable(self):
        r = self.sess.get_plugin_sandbox_policy()
        self.assertTrue(r.ok)
        json.dumps(r.payload)


if __name__ == "__main__":
    unittest.main()

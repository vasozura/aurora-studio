"""Tests for TASK-000090: Plugin QA / Security Checklist Pack."""

import json
import os
import subprocess
import sys
import unittest

BASE_DOCS = "docs/v0_3"
BASE_QA = "docs/v0_3"


class TestQAChecklistDocs(unittest.TestCase):
    def test_foundation_qa_checklist_exists(self):
        self.assertTrue(os.path.exists(os.path.join(BASE_DOCS, "PLUGIN_FOUNDATION_QA_CHECKLIST.md")))

    def test_security_review_checklist_exists(self):
        self.assertTrue(os.path.exists(os.path.join(BASE_DOCS, "PLUGIN_SECURITY_REVIEW_CHECKLIST.md")))

    def test_qa_checklist_mentions_manifest_validation(self):
        with open(os.path.join(BASE_DOCS, "PLUGIN_FOUNDATION_QA_CHECKLIST.md")) as f:
            content = f.read()
        self.assertIn("manifest", content.lower())

    def test_qa_checklist_mentions_permissions(self):
        with open(os.path.join(BASE_DOCS, "PLUGIN_FOUNDATION_QA_CHECKLIST.md")) as f:
            content = f.read()
        self.assertIn("permission", content.lower())

    def test_qa_checklist_mentions_sandbox(self):
        with open(os.path.join(BASE_DOCS, "PLUGIN_FOUNDATION_QA_CHECKLIST.md")) as f:
            content = f.read()
        self.assertIn("sandbox", content.lower())

    def test_qa_checklist_mentions_runtime_stub(self):
        with open(os.path.join(BASE_DOCS, "PLUGIN_FOUNDATION_QA_CHECKLIST.md")) as f:
            content = f.read()
        self.assertIn("stub", content.lower())

    def test_security_review_mentions_no_subprocess(self):
        with open(os.path.join(BASE_DOCS, "PLUGIN_SECURITY_REVIEW_CHECKLIST.md")) as f:
            content = f.read()
        self.assertIn("subprocess", content.lower())

    def test_security_review_mentions_secret_access_denied(self):
        with open(os.path.join(BASE_DOCS, "PLUGIN_SECURITY_REVIEW_CHECKLIST.md")) as f:
            content = f.read()
        self.assertIn("secret_access", content)

    def test_security_review_mentions_execute_code(self):
        with open(os.path.join(BASE_DOCS, "PLUGIN_SECURITY_REVIEW_CHECKLIST.md")) as f:
            content = f.read()
        self.assertIn("execute_code", content)

    def test_security_review_mentions_no_network(self):
        with open(os.path.join(BASE_DOCS, "PLUGIN_SECURITY_REVIEW_CHECKLIST.md")) as f:
            content = f.read()
        self.assertIn("network", content.lower())


class TestPluginSmokeCommand(unittest.TestCase):
    def _run_plugin_smoke(self):
        result = subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli", "plugin-smoke"],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "src", "PYTHONPYCACHEPREFIX": "/tmp/pycache"},
        )
        return result

    def test_plugin_smoke_exits_zero(self):
        r = self._run_plugin_smoke()
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_plugin_smoke_output_is_json(self):
        r = self._run_plugin_smoke()
        data = json.loads(r.stdout)
        self.assertIsInstance(data, dict)

    def test_plugin_smoke_ok_true(self):
        r = self._run_plugin_smoke()
        data = json.loads(r.stdout)
        self.assertTrue(data["ok"])

    def test_plugin_smoke_mode_correct(self):
        r = self._run_plugin_smoke()
        data = json.loads(r.stdout)
        self.assertEqual(data["mode"], "plugin-smoke")

    def test_plugin_smoke_manifest_validates(self):
        r = self._run_plugin_smoke()
        data = json.loads(r.stdout)
        self.assertEqual(data["manifest_validation_status"], "pass")

    def test_plugin_smoke_sandbox_not_allowed(self):
        r = self._run_plugin_smoke()
        data = json.loads(r.stdout)
        self.assertFalse(data["sandbox_allowed"])

    def test_plugin_smoke_stub_blocked(self):
        r = self._run_plugin_smoke()
        data = json.loads(r.stdout)
        self.assertEqual(data["stub_status"], "blocked")


class TestPluginBoundaryEnforcement(unittest.TestCase):
    """Verify that no plugin source file contains forbidden patterns."""

    PLUGIN_MODULES = [
        "src/aurora_studio/modules/plugin_manifest_validator.py",
        "src/aurora_studio/modules/plugin_permission_model.py",
        "src/aurora_studio/modules/plugin_sandbox.py",
        "src/aurora_studio/modules/plugin_runtime_stub.py",
        "src/aurora_studio/modules/plugin_manager.py",
    ]

    def _source(self, path):
        with open(path) as f:
            return f.read()

    def test_no_subprocess_in_validator(self):
        self.assertNotIn("import subprocess", self._source(self.PLUGIN_MODULES[0]))

    def test_no_subprocess_in_permission_model(self):
        self.assertNotIn("import subprocess", self._source(self.PLUGIN_MODULES[1]))

    def test_no_subprocess_in_sandbox(self):
        self.assertNotIn("import subprocess", self._source(self.PLUGIN_MODULES[2]))

    def test_no_subprocess_in_runtime_stub(self):
        self.assertNotIn("import subprocess", self._source(self.PLUGIN_MODULES[3]))

    def test_no_importlib_import_in_sandbox(self):
        self.assertNotIn("importlib.import_module", self._source(self.PLUGIN_MODULES[2]))

    def test_no_importlib_import_in_stub(self):
        self.assertNotIn("importlib.import_module", self._source(self.PLUGIN_MODULES[3]))

    def test_validator_never_opens_entry_point(self):
        src = self._source(self.PLUGIN_MODULES[0])
        self.assertNotIn("__import__", src)

    def test_sandbox_execution_always_false(self):
        from aurora_studio.modules.plugin_sandbox import PluginSandbox
        for pid in ["", "plugin-a", "plugin-b", "untrusted"]:
            self.assertFalse(PluginSandbox().is_execution_allowed(pid))

    def test_stub_always_blocked(self):
        from aurora_studio.modules.plugin_runtime_stub import (
            PluginExecutionRequest,
            PluginRuntimeStub,
        )
        stub = PluginRuntimeStub()
        for pid in ["p1", "p2", "p3"]:
            req = PluginExecutionRequest(plugin_id=pid, action="run")
            self.assertEqual(stub.execute(req).status, "blocked")

    def test_permission_secret_access_denied(self):
        from aurora_studio.modules.plugin_permission_model import PluginPermissionModel
        model = PluginPermissionModel()
        decisions = model.evaluate_requested_permissions(["secret_access"])
        self.assertEqual(decisions[0].decision, "denied")

    def test_permission_execute_code_denied(self):
        from aurora_studio.modules.plugin_permission_model import PluginPermissionModel
        model = PluginPermissionModel()
        decisions = model.evaluate_requested_permissions(["execute_code"])
        self.assertEqual(decisions[0].decision, "denied")


if __name__ == "__main__":
    unittest.main()

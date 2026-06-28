"""Tests for TASK-000096: v0.3 Full Health Audit Pack."""

import os
import subprocess
import sys
import unittest

REPORT_PATH = "docs/qa/V0_3_FULL_HEALTH_AUDIT_REPORT.md"


def _content():
    with open(REPORT_PATH) as f:
        return f.read()


class TestAuditReportExists(unittest.TestCase):
    def test_report_exists(self):
        self.assertTrue(os.path.exists(REPORT_PATH))

    def test_report_contains_command_list(self):
        self.assertIn("python -m unittest", _content())

    def test_report_contains_safety_boundary(self):
        c = _content()
        self.assertIn("Safety Boundary Confirmation", c)

    def test_report_states_no_provider_sdk(self):
        self.assertIn("No provider SDK was added", _content())

    def test_report_states_no_plugin_execution(self):
        self.assertIn("No plugin execution was added", _content())

    def test_report_states_no_database(self):
        self.assertIn("No database was added", _content())

    def test_report_states_no_media_decoding(self):
        self.assertIn("No media decoding was added", _content())

    def test_report_states_no_background_worker(self):
        self.assertIn("No background worker was added", _content())


class TestImportSafety(unittest.TestCase):
    def test_contracts_importable(self):
        import aurora_studio.contracts.plugin
        import aurora_studio.contracts.plugin_permission
        import aurora_studio.contracts.recovery
        import aurora_studio.contracts.autosave
        import aurora_studio.contracts.command

    def test_modules_importable(self):
        import aurora_studio.modules.plugin_manifest_validator
        import aurora_studio.modules.plugin_permission_model
        import aurora_studio.modules.plugin_sandbox
        import aurora_studio.modules.plugin_runtime_stub
        import aurora_studio.modules.project_backup
        import aurora_studio.modules.project_recovery
        import aurora_studio.modules.autosave_manager
        import aurora_studio.modules.command_stack

    def test_ui_session_importable(self):
        from aurora_studio.ui.actions import UISession
        from aurora_studio.services.application_service import ApplicationService
        sess = UISession(ApplicationService())
        self.assertIsNotNone(sess)

    def test_desktop_shell_importable(self):
        import aurora_studio.ui.desktop_shell


class TestSmokeSanity(unittest.TestCase):
    def _run(self, *args):
        return subprocess.run(
            [sys.executable, "-m"] + list(args),
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": "src", "PYTHONPYCACHEPREFIX": "/tmp/pycache"},
        )

    def test_smoke_command(self):
        r = self._run("aurora_studio.cli", "smoke")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_provider_smoke(self):
        r = self._run("aurora_studio.cli", "provider-smoke")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_plugin_smoke(self):
        r = self._run("aurora_studio.cli", "plugin-smoke")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_headless_smoke(self):
        r = self._run("aurora_studio.ui.desktop_shell", "--headless-smoke")
        self.assertEqual(r.returncode, 0, r.stderr)


class TestSafetyBoundaryVerification(unittest.TestCase):
    """Verify key safety invariants hold across the codebase."""

    def test_plugin_execution_disabled(self):
        from aurora_studio.modules.plugin_sandbox import PluginSandbox
        self.assertFalse(PluginSandbox().is_execution_allowed())

    def test_plugin_stub_always_blocked(self):
        from aurora_studio.modules.plugin_runtime_stub import (
            PluginExecutionRequest, PluginRuntimeStub,
        )
        req = PluginExecutionRequest(plugin_id="test")
        self.assertEqual(PluginRuntimeStub().execute(req).status, "blocked")

    def test_secret_access_denied(self):
        from aurora_studio.modules.plugin_permission_model import PluginPermissionModel
        d = PluginPermissionModel().evaluate_requested_permissions(["secret_access"])
        self.assertEqual(d[0].decision, "denied")

    def test_autosave_no_thread(self):
        import threading
        before = threading.active_count()
        from aurora_studio.modules.autosave_manager import AutosaveManager
        AutosaveManager().enable_autosave(".")
        self.assertEqual(threading.active_count(), before)

    def test_command_stack_in_memory(self):
        from aurora_studio.modules.command_stack import CommandStack
        s1 = CommandStack()
        from aurora_studio.modules.command_stack import make_command
        s1.push(make_command("update_scene_detail", "scene", "s1", {}, {}))
        # New stack has no knowledge of s1
        s2 = CommandStack()
        self.assertEqual(s2.get_state().undo_count, 0)


if __name__ == "__main__":
    unittest.main()

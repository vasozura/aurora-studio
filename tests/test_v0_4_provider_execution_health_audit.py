"""TASK-000121: v0.4 Provider Execution Health Audit tests.

Verifies the audit report exists with all required safety confirmations.
Also verifies provider workflows are operational via UISession.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
DOCS_QA = Path(__file__).parent.parent / "docs" / "qa"


class TestHealthAuditReportExists(unittest.TestCase):

    def _report_text(self):
        path = DOCS_QA / "V0_4_PROVIDER_EXECUTION_HEALTH_AUDIT_REPORT.md"
        self.assertTrue(path.exists(), "Health audit report missing")
        return path.read_text(encoding="utf-8")

    def test_report_exists(self):
        self.assertTrue((DOCS_QA / "V0_4_PROVIDER_EXECUTION_HEALTH_AUDIT_REPORT.md").exists())

    def test_report_states_no_provider_sdk(self):
        self.assertIn("No provider SDK was added.", self._report_text())

    def test_report_states_no_real_api_keys(self):
        self.assertIn("No real API keys are stored.", self._report_text())

    def test_report_states_no_secrets_in_artifacts(self):
        self.assertIn("No secrets are written to project JSON", self._report_text())

    def test_report_states_text_real_blocked(self):
        self.assertIn("Real text execution remains blocked by default.", self._report_text())

    def test_report_states_image_real_blocked(self):
        self.assertIn("Real image execution remains blocked by default.", self._report_text())

    def test_report_states_video_real_blocked(self):
        self.assertIn("Real video execution remains blocked by default.", self._report_text())

    def test_report_states_no_media_generation(self):
        self.assertIn("No image/video/media generation was added.", self._report_text())

    def test_report_states_no_media_decoding(self):
        self.assertIn("No media decoding was added.", self._report_text())

    def test_report_states_no_plugin_execution(self):
        self.assertIn("No plugin execution was added.", self._report_text())

    def test_report_states_no_database(self):
        self.assertIn("No database was added.", self._report_text())

    def test_report_states_no_background_worker(self):
        self.assertIn("No background worker was added.", self._report_text())


class TestProviderWorkflowsOperational(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_text_provider_gate_dry_run_allowed(self):
        result = self.sess.evaluate_provider_execution_gate(
            "openai-compatible", "generate", mode="dry_run"
        )
        self.assertTrue(result.ok)
        self.assertTrue(result.payload["allowed"])

    def test_text_provider_gate_real_blocked(self):
        result = self.sess.evaluate_provider_execution_gate(
            "openai-compatible", "generate", mode="real_text"
        )
        self.assertTrue(result.ok)
        self.assertFalse(result.payload["allowed"])

    def test_image_provider_gate_mock_allowed(self):
        result = self.sess.evaluate_image_provider_execution_gate(
            "mock-image", "generate", mode="mock_image"
        )
        self.assertTrue(result.ok)
        self.assertTrue(result.payload["allowed"])

    def test_image_provider_gate_real_blocked(self):
        result = self.sess.evaluate_image_provider_execution_gate(
            "mock-image", "generate", mode="real_image"
        )
        self.assertTrue(result.ok)
        self.assertFalse(result.payload["allowed"])

    def test_video_provider_gate_mock_allowed(self):
        result = self.sess.evaluate_video_provider_execution_gate(
            "mock-video", "generate", mode="mock_video"
        )
        self.assertTrue(result.ok)
        self.assertTrue(result.payload["allowed"])

    def test_video_provider_gate_real_blocked(self):
        result = self.sess.evaluate_video_provider_execution_gate(
            "mock-video", "generate", mode="real_video"
        )
        self.assertTrue(result.ok)
        self.assertFalse(result.payload["allowed"])

    def test_execute_image_provider_mock_ok(self):
        result = self.sess.execute_image_provider_mock("mock-image", "Test prompt")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")

    def test_execute_video_provider_mock_ok(self):
        result = self.sess.execute_video_provider_mock("mock-video", "Test prompt")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")

    def test_provider_registry_has_all_builtins(self):
        from aurora_studio.modules.provider_registry import ProviderRegistry
        reg = ProviderRegistry()
        self.assertIsNotNone(reg.get_provider("dry-run-local"))
        self.assertIsNotNone(reg.get_provider("mock-image"))
        self.assertIsNotNone(reg.get_provider("mock-video"))

    def test_desktop_shell_importable(self):
        import importlib.util
        spec = importlib.util.find_spec("aurora_studio.ui.desktop_shell")
        self.assertIsNotNone(spec)

    def test_all_prereqs_unsatisfied_text(self):
        result = self.sess.list_real_text_provider_prerequisites()
        self.assertTrue(result.ok)
        for p in result.payload["prerequisites"]:
            self.assertFalse(p["satisfied"])

    def test_all_prereqs_unsatisfied_image(self):
        result = self.sess.list_real_image_provider_prerequisites()
        self.assertTrue(result.ok)
        for p in result.payload["prerequisites"]:
            self.assertFalse(p["satisfied"])

    def test_all_prereqs_unsatisfied_video(self):
        result = self.sess.list_real_video_provider_prerequisites()
        self.assertTrue(result.ok)
        for p in result.payload["prerequisites"]:
            self.assertFalse(p["satisfied"])


class TestPluginRuntimeStillBlocked(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))

    def test_plugin_runtime_disabled(self):
        from aurora_studio.modules.plugin_runtime_stub import PluginRuntimeStub
        from aurora_studio.modules.plugin_runtime_stub import PluginExecutionRequest
        stub = PluginRuntimeStub()
        self.assertFalse(stub.is_runtime_enabled())
        req = PluginExecutionRequest(plugin_id="any-plugin", action="run", payload={})
        result = stub.execute(req)
        self.assertNotEqual(result.status, "executed")


if __name__ == "__main__":
    unittest.main()

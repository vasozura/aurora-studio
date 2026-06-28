"""Tests for TASK-000114: Image Prompt Export Bridge UI/CLI Pack.

No network calls. No image generation. No image files. Standard library only.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"


class TestImagePromptExportBridge(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.image_prompt_export_bridge import ImagePromptExportBridge
        self.bridge = ImagePromptExportBridge()

    def test_run_mock_image_from_prompt_ok(self):
        result = self.bridge.run_mock_image_from_prompt("mock-image", "A sunset")
        self.assertEqual(result["status"], "mock")

    def test_run_mock_image_from_prompt_has_image_uri(self):
        result = self.bridge.run_mock_image_from_prompt("mock-image", "A sunset")
        self.assertTrue(result["image_uri"].startswith("mock://image/"))

    def test_run_mock_image_from_prompt_no_network(self):
        result = self.bridge.run_mock_image_from_prompt("mock-image", "A sunset")
        self.assertFalse(result["network_call"])

    def test_run_mock_image_from_prompt_no_image_file(self):
        before = set(os.listdir(tempfile.gettempdir()))
        self.bridge.run_mock_image_from_prompt("mock-image", "A sunset")
        after = set(os.listdir(tempfile.gettempdir()))
        new_files = after - before
        image_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
        for f in new_files:
            self.assertFalse(any(f.endswith(e) for e in image_exts))

    def test_run_mock_image_from_prompt_json_serializable(self):
        result = self.bridge.run_mock_image_from_prompt("mock-image", "A sunset")
        serialized = json.dumps(result)
        parsed = json.loads(serialized)
        self.assertEqual(parsed["status"], "mock")

    def test_run_mock_image_from_prompt_no_secret_in_result(self):
        result = self.bridge.run_mock_image_from_prompt("mock-image", "A sunset")
        serialized = json.dumps(result)
        self.assertNotIn("api_key", serialized)
        self.assertNotIn("secret", serialized)

    def test_run_mock_image_from_export_ok(self):
        result = self.bridge.run_mock_image_from_export("mock-image", "export-001")
        self.assertEqual(result["status"], "mock")

    def test_run_mock_image_from_export_has_image_uri(self):
        result = self.bridge.run_mock_image_from_export("mock-image", "export-001")
        self.assertTrue(result["image_uri"].startswith("mock://image/"))

    def test_run_mock_image_from_export_source_tagged(self):
        result = self.bridge.run_mock_image_from_export("mock-image", "export-001")
        self.assertEqual(result["source"], "export")

    def test_run_mock_image_from_template_ok(self):
        result = self.bridge.run_mock_image_from_template(
            "mock-image", "character", "char-001",
            template_id="t1", profile_id="p1"
        )
        self.assertEqual(result["status"], "mock")

    def test_run_mock_image_from_template_source_tagged(self):
        result = self.bridge.run_mock_image_from_template(
            "mock-image", "character", "char-001"
        )
        self.assertEqual(result["source"], "template")

    def test_list_image_provider_runs_empty_initially(self):
        from aurora_studio.modules.image_prompt_export_bridge import ImagePromptExportBridge
        fresh = ImagePromptExportBridge()
        self.assertEqual(len(fresh.list_image_provider_runs()), 0)

    def test_list_image_provider_runs_after_run(self):
        self.bridge.run_mock_image_from_prompt("mock-image", "A sunset")
        runs = self.bridge.list_image_provider_runs()
        self.assertGreater(len(runs), 0)

    def test_list_image_provider_runs_filter_by_provider(self):
        self.bridge.run_mock_image_from_prompt("mock-image", "A sunset")
        runs = self.bridge.list_image_provider_runs(provider_id="mock-image")
        for r in runs:
            self.assertEqual(r["provider_id"], "mock-image")

    def test_list_image_provider_runs_filter_by_status(self):
        self.bridge.run_mock_image_from_prompt("mock-image", "A sunset")
        runs = self.bridge.list_image_provider_runs(status="mock")
        self.assertGreater(len(runs), 0)

    def test_build_prompt_from_export_returns_string(self):
        prompt = self.bridge.build_image_prompt_from_export("export-abc")
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)

    def test_build_prompt_from_template_returns_string(self):
        prompt = self.bridge.build_image_prompt_from_template("scene", "scene-001")
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)

    def test_create_request_from_prompt_valid(self):
        req = self.bridge.create_image_provider_request_from_prompt(
            "mock-image", "A sunset", model="mock-v1"
        )
        self.assertEqual(req.provider_id, "mock-image")
        self.assertEqual(req.mode, "mock_image")


class TestUISessionImageBridge(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_run_mock_image_from_prompt_ok(self):
        result = self.sess.run_mock_image_from_prompt("mock-image", "A golden field")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")

    def test_run_mock_image_from_prompt_no_network(self):
        result = self.sess.run_mock_image_from_prompt("mock-image", "A golden field")
        self.assertFalse(result.payload["network_call"])

    def test_run_mock_image_from_prompt_json_serializable(self):
        result = self.sess.run_mock_image_from_prompt("mock-image", "A golden field")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["payload"]["status"], "mock")

    def test_run_mock_image_from_export_ok(self):
        result = self.sess.run_mock_image_from_export("mock-image", "export-42")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")

    def test_run_mock_image_from_template_ok(self):
        result = self.sess.run_mock_image_from_template(
            "mock-image", "scene", "scene-001"
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")

    def test_list_image_provider_runs_ok(self):
        self.sess.run_mock_image_from_prompt("mock-image", "First")
        result = self.sess.list_image_provider_runs()
        self.assertTrue(result.ok)
        self.assertGreaterEqual(result.payload["total"], 1)

    def test_list_image_provider_runs_json_serializable(self):
        result = self.sess.list_image_provider_runs()
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertIn("total", parsed["payload"])

    def test_image_bridge_methods_exist(self):
        self.assertTrue(hasattr(self.sess, "run_mock_image_from_prompt"))
        self.assertTrue(hasattr(self.sess, "run_mock_image_from_export"))
        self.assertTrue(hasattr(self.sess, "run_mock_image_from_template"))
        self.assertTrue(hasattr(self.sess, "list_image_provider_runs"))

    def test_evaluate_image_real_readiness_blocked(self):
        result = self.sess.evaluate_image_provider_real_readiness("mock-image")
        self.assertTrue(result.ok)
        self.assertFalse(result.payload["real_image_execution_ready"])


class TestCLIImageProvider(unittest.TestCase):

    def _run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli.main"] + list(args),
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(SRC)},
        )

    def test_image_provider_mock_exits_zero(self):
        r = self._run_cli("image-provider-mock", "--provider", "mock-image",
                          "--prompt", "A sunset")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_image_provider_mock_json_output(self):
        r = self._run_cli("image-provider-mock", "--provider", "mock-image",
                          "--prompt", "A sunset")
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["command"], "image-provider-mock")
        self.assertEqual(parsed["status"], "mock")

    def test_image_provider_mock_no_network(self):
        r = self._run_cli("image-provider-mock", "--provider", "mock-image",
                          "--prompt", "A sunset")
        parsed = json.loads(r.stdout)
        self.assertFalse(parsed["network_call"])

    def test_image_provider_mock_image_uri_scheme(self):
        r = self._run_cli("image-provider-mock", "--provider", "mock-image",
                          "--prompt", "A sunset")
        parsed = json.loads(r.stdout)
        self.assertTrue(parsed["image_uri"].startswith("mock://image/"))

    def test_image_provider_mock_no_secret_in_output(self):
        r = self._run_cli("image-provider-mock", "--provider", "mock-image",
                          "--prompt", "A sunset")
        self.assertNotIn("api_key", r.stdout)
        self.assertNotIn("sk-", r.stdout)

    def test_image_provider_readiness_exits_zero(self):
        r = self._run_cli("image-provider-readiness", "--provider", "mock-image",
                          "--prompt", "A sunset")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_image_provider_readiness_json_output(self):
        r = self._run_cli("image-provider-readiness", "--provider", "mock-image")
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["command"], "image-provider-readiness")
        self.assertFalse(parsed["real_image_execution_ready"])

    def test_image_provider_readiness_has_missing_conditions(self):
        r = self._run_cli("image-provider-readiness", "--provider", "mock-image")
        parsed = json.loads(r.stdout)
        self.assertGreater(len(parsed["missing_conditions"]), 0)


if __name__ == "__main__":
    unittest.main()

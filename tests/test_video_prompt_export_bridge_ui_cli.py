"""TASK-000119: Video Prompt Export Bridge UI/CLI tests.

No network. No video files. No ffmpeg. Standard library only.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"


class TestVideoPromptExportBridge(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.video_prompt_export_bridge import VideoPromptExportBridge
        self.bridge = VideoPromptExportBridge()

    def test_run_mock_video_from_prompt_ok(self):
        result = self.bridge.run_mock_video_from_prompt("mock-video", "A timelapse of clouds")
        self.assertEqual(result["status"], "mock")

    def test_run_mock_video_from_prompt_has_video_uri(self):
        result = self.bridge.run_mock_video_from_prompt("mock-video", "A timelapse")
        self.assertTrue(result["video_uri"].startswith("mock://video/"))

    def test_run_mock_video_from_prompt_has_job_id(self):
        result = self.bridge.run_mock_video_from_prompt("mock-video", "A timelapse")
        self.assertTrue(result["job_id"].startswith("mock-job-"))

    def test_run_mock_video_from_prompt_no_network(self):
        result = self.bridge.run_mock_video_from_prompt("mock-video", "A timelapse")
        self.assertFalse(result["network_call"])

    def test_run_mock_video_from_prompt_no_video_file(self):
        before = set(os.listdir(tempfile.gettempdir()))
        self.bridge.run_mock_video_from_prompt("mock-video", "A timelapse")
        after = set(os.listdir(tempfile.gettempdir()))
        video_exts = {".mp4", ".mov", ".webm", ".avi", ".mkv"}
        for f in (after - before):
            self.assertFalse(any(f.endswith(e) for e in video_exts))

    def test_run_mock_video_from_prompt_json_serializable(self):
        result = self.bridge.run_mock_video_from_prompt("mock-video", "A timelapse")
        serialized = json.dumps(result)
        parsed = json.loads(serialized)
        self.assertEqual(parsed["status"], "mock")

    def test_run_mock_video_from_prompt_no_secret(self):
        result = self.bridge.run_mock_video_from_prompt("mock-video", "A timelapse")
        serialized = json.dumps(result)
        self.assertNotIn("api_key", serialized)
        self.assertNotIn("secret", serialized)

    def test_run_mock_video_from_export_ok(self):
        result = self.bridge.run_mock_video_from_export("mock-video", "export-001")
        self.assertEqual(result["status"], "mock")

    def test_run_mock_video_from_export_has_video_uri(self):
        result = self.bridge.run_mock_video_from_export("mock-video", "export-001")
        self.assertTrue(result["video_uri"].startswith("mock://video/"))

    def test_run_mock_video_from_export_source_tagged(self):
        result = self.bridge.run_mock_video_from_export("mock-video", "export-001")
        self.assertEqual(result["source"], "export")

    def test_run_mock_video_from_template_ok(self):
        result = self.bridge.run_mock_video_from_template(
            "mock-video", "scene", "scene-001", template_id="t1", profile_id="p1"
        )
        self.assertEqual(result["status"], "mock")

    def test_run_mock_video_from_template_source_tagged(self):
        result = self.bridge.run_mock_video_from_template("mock-video", "scene", "s1")
        self.assertEqual(result["source"], "template")

    def test_list_video_provider_runs_empty_initially(self):
        from aurora_studio.modules.video_prompt_export_bridge import VideoPromptExportBridge
        fresh = VideoPromptExportBridge()
        self.assertEqual(len(fresh.list_video_provider_runs()), 0)

    def test_list_video_provider_runs_after_run(self):
        self.bridge.run_mock_video_from_prompt("mock-video", "A timelapse")
        runs = self.bridge.list_video_provider_runs()
        self.assertGreater(len(runs), 0)

    def test_list_video_provider_runs_filter_by_provider(self):
        self.bridge.run_mock_video_from_prompt("mock-video", "A timelapse")
        runs = self.bridge.list_video_provider_runs(provider_id="mock-video")
        for r in runs:
            self.assertEqual(r["provider_id"], "mock-video")

    def test_list_video_provider_runs_filter_by_status(self):
        self.bridge.run_mock_video_from_prompt("mock-video", "A timelapse")
        runs = self.bridge.list_video_provider_runs(status="mock")
        self.assertGreater(len(runs), 0)

    def test_build_prompt_from_export_returns_string(self):
        prompt = self.bridge.build_video_prompt_from_export("export-xyz")
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)

    def test_build_prompt_from_template_returns_string(self):
        prompt = self.bridge.build_video_prompt_from_template("scene", "s1")
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)

    def test_create_request_from_prompt_valid(self):
        req = self.bridge.create_video_provider_request_from_prompt(
            "mock-video", "A timelapse", model="mock-v1"
        )
        self.assertEqual(req.provider_id, "mock-video")
        self.assertEqual(req.mode, "mock_video")


class TestUISessionVideoBridge(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_run_mock_video_from_prompt_ok(self):
        result = self.sess.run_mock_video_from_prompt("mock-video", "A sweeping vista")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")

    def test_run_mock_video_from_prompt_no_network(self):
        result = self.sess.run_mock_video_from_prompt("mock-video", "A sweeping vista")
        self.assertFalse(result.payload["network_call"])

    def test_run_mock_video_from_prompt_json_serializable(self):
        result = self.sess.run_mock_video_from_prompt("mock-video", "A sweeping vista")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["payload"]["status"], "mock")

    def test_run_mock_video_from_export_ok(self):
        result = self.sess.run_mock_video_from_export("mock-video", "export-42")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")

    def test_run_mock_video_from_template_ok(self):
        result = self.sess.run_mock_video_from_template("mock-video", "scene", "s001")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")

    def test_list_video_provider_runs_ok(self):
        self.sess.run_mock_video_from_prompt("mock-video", "First run")
        result = self.sess.list_video_provider_runs()
        self.assertTrue(result.ok)
        self.assertGreaterEqual(result.payload["total"], 1)

    def test_list_video_provider_runs_json_serializable(self):
        result = self.sess.list_video_provider_runs()
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertIn("total", parsed["payload"])

    def test_video_bridge_methods_exist(self):
        self.assertTrue(hasattr(self.sess, "run_mock_video_from_prompt"))
        self.assertTrue(hasattr(self.sess, "run_mock_video_from_export"))
        self.assertTrue(hasattr(self.sess, "run_mock_video_from_template"))
        self.assertTrue(hasattr(self.sess, "list_video_provider_runs"))

    def test_evaluate_video_real_readiness_blocked(self):
        result = self.sess.evaluate_video_provider_real_readiness("mock-video")
        self.assertTrue(result.ok)
        self.assertFalse(result.payload["real_video_execution_ready"])


class TestCLIVideoProvider(unittest.TestCase):

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli.main"] + list(args),
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(SRC)},
        )

    def test_video_provider_mock_exits_zero(self):
        r = self._run("video-provider-mock", "--provider", "mock-video",
                      "--prompt", "A timelapse of clouds")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_video_provider_mock_json_output(self):
        r = self._run("video-provider-mock", "--provider", "mock-video",
                      "--prompt", "A timelapse")
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["command"], "video-provider-mock")
        self.assertEqual(parsed["status"], "mock")

    def test_video_provider_mock_no_network(self):
        r = self._run("video-provider-mock", "--provider", "mock-video",
                      "--prompt", "A timelapse")
        parsed = json.loads(r.stdout)
        self.assertFalse(parsed["network_call"])

    def test_video_provider_mock_video_uri_scheme(self):
        r = self._run("video-provider-mock", "--provider", "mock-video",
                      "--prompt", "A timelapse")
        parsed = json.loads(r.stdout)
        self.assertTrue(parsed["video_uri"].startswith("mock://video/"))

    def test_video_provider_mock_no_secret_in_output(self):
        r = self._run("video-provider-mock", "--provider", "mock-video",
                      "--prompt", "A timelapse")
        self.assertNotIn("api_key", r.stdout)
        self.assertNotIn("sk-", r.stdout)

    def test_video_provider_readiness_exits_zero(self):
        r = self._run("video-provider-readiness", "--provider", "mock-video")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_video_provider_readiness_json_output(self):
        r = self._run("video-provider-readiness", "--provider", "mock-video")
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["command"], "video-provider-readiness")
        self.assertFalse(parsed["real_video_execution_ready"])

    def test_video_provider_readiness_has_missing_conditions(self):
        r = self._run("video-provider-readiness", "--provider", "mock-video")
        parsed = json.loads(r.stdout)
        self.assertGreater(len(parsed["missing_conditions"]), 0)


if __name__ == "__main__":
    unittest.main()

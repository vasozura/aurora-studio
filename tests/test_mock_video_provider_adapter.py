"""TASK-000118: Mock Video Provider Adapter tests.

No network. No video files. Standard library only.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"


class TestMockVideoProviderAdapter(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.mock_video_provider_adapter import MockVideoProviderAdapter
        from aurora_studio.contracts.video_provider import VideoProviderRequest
        self.adapter = MockVideoProviderAdapter()
        self.Request = VideoProviderRequest

    def _req(self, mode="mock_video", prompt="A timelapse of clouds"):
        return self.Request(
            request_id="test-r1", provider_id="mock-video",
            mode=mode, prompt_text=prompt,
        )

    def test_supports_mock_video(self):
        self.assertTrue(self.adapter.supports("mock-video"))

    def test_supports_mock_video_alias(self):
        self.assertTrue(self.adapter.supports("mock-vid"))

    def test_execute_mock_status_mock(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertEqual(resp.status, "mock")

    def test_execute_mock_deterministic(self):
        r = self._req()
        resp1 = self.adapter.execute_mock(r)
        resp2 = self.adapter.execute_mock(r)
        self.assertEqual(resp1.video_uri, resp2.video_uri)

    def test_execute_mock_video_uri_scheme(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertTrue(resp.video_uri.startswith("mock://video/"))

    def test_execute_mock_job_id_wellformed(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertTrue(resp.job_id.startswith("mock-job-"))

    def test_execute_mock_no_network(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertFalse(resp.network_call)

    def test_execute_mock_is_mock_response(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertTrue(resp.mock_response)

    def test_execute_no_secret_required(self):
        resp = self.adapter.execute(self._req())
        self.assertEqual(resp.status, "mock")

    def test_execute_real_video_blocked(self):
        resp = self.adapter.execute(self._req(mode="real_video"), secret_value="fake")
        self.assertEqual(resp.status, "blocked")

    def test_execute_blocked_real_video_blocked(self):
        resp = self.adapter.execute(self._req(mode="blocked_real_video"))
        self.assertEqual(resp.status, "blocked")

    def test_no_video_file_created(self):
        before = set(os.listdir(tempfile.gettempdir()))
        self.adapter.execute_mock(self._req())
        after = set(os.listdir(tempfile.gettempdir()))
        video_exts = {".mp4", ".mov", ".webm", ".avi", ".gif", ".mkv"}
        for f in (after - before):
            self.assertFalse(any(f.endswith(e) for e in video_exts))

    def test_build_mock_video_uri_contains_request_id(self):
        r = self._req()
        uri = self.adapter.build_mock_video_uri(r)
        self.assertIn(r.request_id, uri)

    def test_build_mock_job_id_contains_request_id(self):
        r = self._req()
        job_id = self.adapter.build_mock_job_id(r)
        self.assertIn(r.request_id, job_id)

    def test_build_mock_response_returns_response(self):
        r = self._req()
        resp = self.adapter.build_mock_response(r)
        self.assertEqual(resp.status, "mock")
        self.assertTrue(resp.video_uri.startswith("mock://"))

    def test_sanitize_error_redacts_sensitive(self):
        msg = self.adapter.sanitize_error(Exception("api_key=sk-abc123"))
        self.assertNotIn("sk-abc123", msg)

    def test_response_json_serializable(self):
        resp = self.adapter.execute_mock(self._req())
        serialized = json.dumps(resp.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["status"], "mock")

    def test_response_no_secret_fields(self):
        resp = self.adapter.execute_mock(self._req())
        d = resp.to_dict()
        for bad in ("api_key", "secret", "token", "password"):
            self.assertNotIn(bad, d)

    def test_invalid_prompt_returns_invalid_request(self):
        req = self.Request(
            request_id="r1", provider_id="mock-video",
            mode="mock_video", prompt_text=""
        )
        resp = self.adapter.execute_mock(req)
        self.assertEqual(resp.status, "invalid_request")


class TestProviderRegistryMockVideo(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_registry import ProviderRegistry
        self.registry = ProviderRegistry()

    def test_mock_video_provider_registered(self):
        provider = self.registry.get_provider("mock-video")
        self.assertIsNotNone(provider)

    def test_mock_video_provider_type_is_video(self):
        provider = self.registry.get_provider("mock-video")
        self.assertEqual(provider.provider_type, "video")

    def test_mock_video_requires_no_api_key(self):
        provider = self.registry.get_provider("mock-video")
        self.assertFalse(provider.requires_api_key)

    def test_mock_image_still_registered(self):
        provider = self.registry.get_provider("mock-image")
        self.assertIsNotNone(provider)

    def test_dry_run_still_registered(self):
        provider = self.registry.get_provider("dry-run-local")
        self.assertIsNotNone(provider)


class TestUISessionMockVideo(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_execute_video_provider_mock_ok(self):
        result = self.sess.execute_video_provider_mock(
            "mock-video", "A sweeping aerial view"
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")

    def test_execute_video_provider_mock_no_network(self):
        result = self.sess.execute_video_provider_mock(
            "mock-video", "A sweeping aerial view"
        )
        self.assertFalse(result.payload["network_call"])

    def test_execute_video_provider_mock_has_video_uri(self):
        result = self.sess.execute_video_provider_mock(
            "mock-video", "A sweeping aerial view"
        )
        self.assertTrue(result.payload["video_uri"].startswith("mock://"))

    def test_execute_video_provider_mock_json_serializable(self):
        result = self.sess.execute_video_provider_mock(
            "mock-video", "A sweeping aerial view"
        )
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["payload"]["status"], "mock")

    def test_evaluate_video_real_readiness_blocked(self):
        result = self.sess.evaluate_video_provider_real_readiness("mock-video", "test")
        self.assertTrue(result.ok)
        self.assertFalse(result.payload["real_video_execution_ready"])

    def test_evaluate_video_real_readiness_has_missing(self):
        result = self.sess.evaluate_video_provider_real_readiness("mock-video", "test")
        self.assertGreater(len(result.payload["missing_conditions"]), 0)

    def test_evaluate_video_real_readiness_json_serializable(self):
        result = self.sess.evaluate_video_provider_real_readiness("mock-video", "test")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["payload"]["real_video_execution_ready"])


class TestDesktopImportSafe118(unittest.TestCase):

    def test_desktop_shell_importable(self):
        sys.path.insert(0, str(SRC))
        import importlib.util
        spec = importlib.util.find_spec("aurora_studio.ui.desktop_shell")
        self.assertIsNotNone(spec)


if __name__ == "__main__":
    unittest.main()

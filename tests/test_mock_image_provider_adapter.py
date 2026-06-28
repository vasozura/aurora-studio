"""Tests for TASK-000113: Mock Image Provider Adapter Pack.

No network calls. No image generation. No image files. Standard library only.
"""

import json
import sys
import tempfile
import os
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"


class TestMockImageProviderAdapter(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.mock_image_provider_adapter import MockImageProviderAdapter
        from aurora_studio.contracts.image_provider import ImageProviderRequest
        self.adapter = MockImageProviderAdapter()
        self.Request = ImageProviderRequest

    def _make_request(self, prompt="A sunset", provider="mock-image"):
        return self.Request(
            request_id="test-r1",
            provider_id=provider,
            mode="mock_image",
            prompt_text=prompt,
        )

    def test_supports_mock_image(self):
        self.assertTrue(self.adapter.supports("mock-image"))

    def test_supports_mock_alias(self):
        self.assertTrue(self.adapter.supports("mock"))

    def test_execute_mock_returns_mock_status(self):
        r = self._make_request()
        resp = self.adapter.execute_mock(r)
        self.assertEqual(resp.status, "mock")

    def test_execute_mock_is_deterministic(self):
        r = self._make_request()
        resp1 = self.adapter.execute_mock(r)
        resp2 = self.adapter.execute_mock(r)
        self.assertEqual(resp1.image_uri, resp2.image_uri)

    def test_execute_mock_image_uri_scheme(self):
        r = self._make_request()
        resp = self.adapter.execute_mock(r)
        self.assertTrue(resp.image_uri.startswith("mock://image/"))

    def test_execute_mock_no_network(self):
        r = self._make_request()
        resp = self.adapter.execute_mock(r)
        self.assertFalse(resp.network_call)

    def test_execute_mock_is_mock_response(self):
        r = self._make_request()
        resp = self.adapter.execute_mock(r)
        self.assertTrue(resp.mock_response)

    def test_execute_mock_no_secret_required(self):
        r = self._make_request()
        resp = self.adapter.execute(r)  # no secret_value arg
        self.assertEqual(resp.status, "mock")

    def test_execute_real_blocked(self):
        r = self.Request(
            request_id="r1", provider_id="mock-image",
            mode="real_image", prompt_text="A sunset"
        )
        resp = self.adapter.execute(r, secret_value="fake")
        self.assertEqual(resp.status, "blocked")

    def test_execute_blocked_real_image_blocked(self):
        r = self.Request(
            request_id="r1", provider_id="mock-image",
            mode="blocked_real_image", prompt_text="A sunset"
        )
        resp = self.adapter.execute(r)
        self.assertEqual(resp.status, "blocked")

    def test_no_image_file_created(self):
        before = set(os.listdir(tempfile.gettempdir()))
        r = self._make_request()
        self.adapter.execute_mock(r)
        after = set(os.listdir(tempfile.gettempdir()))
        new_files = after - before
        image_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
        for f in new_files:
            self.assertFalse(any(f.endswith(e) for e in image_exts))

    def test_build_mock_image_uri_contains_request_id(self):
        r = self._make_request()
        uri = self.adapter.build_mock_image_uri(r)
        self.assertIn(r.request_id, uri)

    def test_build_mock_response_returns_response(self):
        r = self._make_request()
        resp = self.adapter.build_mock_response(r)
        self.assertEqual(resp.status, "mock")
        self.assertTrue(resp.image_uri.startswith("mock://"))

    def test_sanitize_error_redacts_sensitive_words(self):
        msg = self.adapter.sanitize_error(Exception("api_key=abc123"))
        self.assertNotIn("abc123", msg)

    def test_response_json_serializable(self):
        r = self._make_request()
        resp = self.adapter.execute_mock(r)
        serialized = json.dumps(resp.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["status"], "mock")

    def test_response_no_secret_fields(self):
        r = self._make_request()
        resp = self.adapter.execute_mock(r)
        d = resp.to_dict()
        secret_keys = {"api_key", "secret", "token", "password"}
        self.assertTrue(secret_keys.isdisjoint(d.keys()))

    def test_invalid_prompt_returns_invalid_request(self):
        r = self.Request(
            request_id="r1", provider_id="mock-image",
            mode="mock_image", prompt_text=""
        )
        resp = self.adapter.execute_mock(r)
        self.assertEqual(resp.status, "invalid_request")


class TestProviderRegistryMockImage(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_registry import ProviderRegistry
        self.registry = ProviderRegistry()

    def test_mock_image_provider_registered(self):
        provider = self.registry.get_provider("mock-image")
        self.assertIsNotNone(provider)

    def test_mock_image_provider_type_is_image(self):
        provider = self.registry.get_provider("mock-image")
        self.assertEqual(provider.provider_type, "image")

    def test_mock_image_requires_no_api_key(self):
        provider = self.registry.get_provider("mock-image")
        self.assertFalse(provider.requires_api_key)

    def test_dry_run_provider_still_registered(self):
        provider = self.registry.get_provider("dry-run-local")
        self.assertIsNotNone(provider)


class TestUISessionMockImage(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_execute_image_provider_mock_ok(self):
        result = self.sess.execute_image_provider_mock(
            "mock-image", "A sunset over mountains"
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")

    def test_execute_image_provider_mock_no_network(self):
        result = self.sess.execute_image_provider_mock(
            "mock-image", "A sunset"
        )
        self.assertFalse(result.payload["network_call"])

    def test_execute_image_provider_mock_has_image_uri(self):
        result = self.sess.execute_image_provider_mock(
            "mock-image", "A sunset"
        )
        self.assertTrue(result.payload["image_uri"].startswith("mock://"))

    def test_execute_image_provider_mock_json_serializable(self):
        result = self.sess.execute_image_provider_mock(
            "mock-image", "A sunset"
        )
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["payload"]["status"], "mock")

    def test_evaluate_image_real_readiness_blocked(self):
        result = self.sess.evaluate_image_provider_real_readiness("mock-image", "A sunset")
        self.assertTrue(result.ok)
        self.assertFalse(result.payload["real_image_execution_ready"])

    def test_evaluate_image_real_readiness_has_missing_conditions(self):
        result = self.sess.evaluate_image_provider_real_readiness("mock-image", "A sunset")
        self.assertGreater(len(result.payload["missing_conditions"]), 0)

    def test_evaluate_image_real_readiness_json_serializable(self):
        result = self.sess.evaluate_image_provider_real_readiness("mock-image", "A sunset")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["payload"]["real_image_execution_ready"])


class TestDesktopImportSafe113(unittest.TestCase):

    def test_desktop_shell_importable(self):
        sys.path.insert(0, str(SRC))
        import importlib.util
        spec = importlib.util.find_spec("aurora_studio.ui.desktop_shell")
        self.assertIsNotNone(spec)


if __name__ == "__main__":
    unittest.main()

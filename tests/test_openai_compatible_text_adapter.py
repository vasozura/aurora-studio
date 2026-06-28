"""Tests for TASK-000108: OpenAI-Compatible Text Provider Adapter Pack.

All tests use dry_run or mock modes — no real network calls.
Real execution path is monkeypatched to prevent any accidental network access.
No openai SDK. No requests/httpx/aiohttp.
"""

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

SRC = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC))


class TestAdapterMockExecution(unittest.TestCase):

    def setUp(self):
        from aurora_studio.modules.openai_compatible_text_adapter import OpenAICompatibleTextAdapter
        from aurora_studio.contracts.text_provider import TextProviderRequest
        self.Adapter = OpenAICompatibleTextAdapter
        self.Request = TextProviderRequest

    def test_mock_returns_mock_status(self):
        adapter = self.Adapter(provider_id="openai")
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="mock")
        resp = adapter.execute_mock(r)
        self.assertEqual(resp.status, "mock")

    def test_mock_no_network_call(self):
        adapter = self.Adapter(provider_id="openai")
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="mock")
        resp = adapter.execute_mock(r)
        self.assertFalse(resp.network_call)

    def test_mock_is_mock_response(self):
        adapter = self.Adapter(provider_id="openai")
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="mock")
        resp = adapter.execute_mock(r)
        self.assertTrue(resp.mock_response)

    def test_mock_text_contains_provider_id(self):
        adapter = self.Adapter(provider_id="openai")
        r = self.Request(provider_id="openai", prompt="Hello", model_id="gpt-4", execution_mode="mock")
        resp = adapter.execute_mock(r)
        self.assertIn("openai", resp.text)

    def test_mock_text_contains_v04(self):
        adapter = self.Adapter(provider_id="openai")
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="mock")
        resp = adapter.execute_mock(r)
        self.assertIn("v0.4", resp.text)

    def test_mock_invalid_prompt_returns_invalid_request(self):
        adapter = self.Adapter(provider_id="openai")
        r = self.Request(provider_id="openai", prompt="", execution_mode="mock")
        resp = adapter.execute_mock(r)
        self.assertEqual(resp.status, "invalid_request")

    def test_mock_uses_default_model_if_not_specified(self):
        from aurora_studio.modules.openai_compatible_text_adapter import DEFAULT_MODEL
        adapter = self.Adapter(provider_id="openai")
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="mock")
        resp = adapter.execute_mock(r)
        self.assertEqual(resp.model_id, DEFAULT_MODEL)


class TestAdapterDryRun(unittest.TestCase):

    def setUp(self):
        from aurora_studio.modules.openai_compatible_text_adapter import OpenAICompatibleTextAdapter
        from aurora_studio.contracts.text_provider import TextProviderRequest
        self.adapter = OpenAICompatibleTextAdapter(provider_id="openai")
        self.Request = TextProviderRequest

    def test_dry_run_returns_dry_run_status(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="dry_run")
        resp = self.adapter.execute(r)
        self.assertEqual(resp.status, "dry_run")

    def test_dry_run_no_network(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="dry_run")
        resp = self.adapter.execute(r)
        self.assertFalse(resp.network_call)


class TestAdapterRealBlocked(unittest.TestCase):

    def setUp(self):
        from aurora_studio.modules.openai_compatible_text_adapter import OpenAICompatibleTextAdapter
        from aurora_studio.contracts.text_provider import TextProviderRequest
        self.adapter = OpenAICompatibleTextAdapter(provider_id="openai")
        self.Request = TextProviderRequest

    def test_real_text_blocked_without_gate(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="real_text")
        resp = self.adapter.execute(r)
        self.assertEqual(resp.status, "blocked")

    def test_real_text_blocked_no_network(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="real_text")
        resp = self.adapter.execute(r)
        self.assertFalse(resp.network_call)

    def test_real_text_blocked_without_secret(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="real_text")
        resp = self.adapter.execute(r, ephemeral_secret="")
        self.assertEqual(resp.status, "blocked")

    def test_execute_real_text_without_secret_is_blocked(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="real_text")
        resp = self.adapter.execute_real_text(r, ephemeral_secret="")
        self.assertEqual(resp.status, "blocked")

    def test_blocked_real_mode_is_blocked(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="blocked_real")
        resp = self.adapter.execute(r)
        self.assertEqual(resp.status, "blocked")


class TestAdapterRealMonkeypatched(unittest.TestCase):
    """Test real text path with monkeypatched urllib — no actual network calls."""

    def setUp(self):
        from aurora_studio.modules.openai_compatible_text_adapter import OpenAICompatibleTextAdapter
        from aurora_studio.contracts.text_provider import TextProviderRequest
        self.adapter = OpenAICompatibleTextAdapter(provider_id="openai")
        self.Request = TextProviderRequest

    def _make_mock_response(self, text: str) -> MagicMock:
        body = {
            "choices": [{"message": {"content": text}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 10},
        }
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(body).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    @patch("aurora_studio.modules.openai_compatible_text_adapter.OpenAICompatibleTextAdapter.execute_real_text")
    def test_execute_real_text_monkeypatched_blocked_by_gate(self, mock_exec):
        """Real execution path is still blocked by gate even with monkeypatch in place."""
        mock_exec.return_value = MagicMock(status="success", network_call=False)
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="real_text")
        resp = self.adapter.execute(r, ephemeral_secret="fake-secret")
        # Gate blocks before execute_real_text is called
        self.assertEqual(resp.status, "blocked")
        mock_exec.assert_not_called()

    def test_execute_real_text_directly_monkeypatched(self):
        """Direct call to execute_real_text with urllib monkeypatched."""
        mock_resp = self._make_mock_response("Hello from monkeypatched API")
        r = self.Request(
            provider_id="openai", prompt="Hello", model_id="gpt-4",
            execution_mode="real_text",
        )
        with patch("urllib.request.urlopen", return_value=mock_resp):
            resp = self.adapter.execute_real_text(r, ephemeral_secret="sk-fake-token")
        self.assertEqual(resp.status, "success")
        self.assertIn("Hello from monkeypatched API", resp.text)
        self.assertTrue(resp.network_call)

    def test_execute_real_text_error_does_not_expose_secret(self):
        """Error response must not contain the ephemeral secret."""
        import urllib.error
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="real_text")
        fake_secret = "sk-supersecret-abc123"
        with patch("urllib.request.urlopen", side_effect=Exception(f"failed: {fake_secret}")):
            resp = self.adapter.execute_real_text(r, ephemeral_secret=fake_secret)
        self.assertNotIn(fake_secret, resp.error_message)
        self.assertEqual(resp.status, "error")


class TestUISessionMock108(unittest.TestCase):

    def setUp(self):
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_execute_text_provider_mock_ok(self):
        result = self.sess.execute_text_provider_mock("openai", "Hello world")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")

    def test_execute_text_provider_mock_no_network(self):
        result = self.sess.execute_text_provider_mock("openai", "Hello world")
        self.assertFalse(result.payload["network_call"])

    def test_execute_text_provider_mock_json_serializable(self):
        result = self.sess.execute_text_provider_mock("openai", "Hello world")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["payload"]["status"], "mock")

    def test_execute_text_provider_real_blocked_returns_blocked(self):
        result = self.sess.execute_text_provider_real_blocked("openai", "Hello world")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "blocked")

    def test_execute_text_provider_real_blocked_no_network(self):
        result = self.sess.execute_text_provider_real_blocked("openai", "Hello world")
        self.assertFalse(result.payload["network_call"])

    def test_execute_real_with_ephemeral_requires_confirm(self):
        result = self.sess.execute_text_provider_real_with_ephemeral_secret(
            "openai", "Hello", "sk-fake", confirm=False
        )
        self.assertFalse(result.ok)

    def test_execute_real_with_ephemeral_confirm_true_blocked_by_gate(self):
        result = self.sess.execute_text_provider_real_with_ephemeral_secret(
            "openai", "Hello", "sk-fake", confirm=True
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "blocked")

    def test_execute_real_payload_does_not_contain_secret(self):
        result = self.sess.execute_text_provider_real_with_ephemeral_secret(
            "openai", "Hello", "sk-top-secret-key", confirm=True
        )
        payload_str = json.dumps(result.to_dict())
        self.assertNotIn("sk-top-secret-key", payload_str)


class TestNoForbiddenImports108(unittest.TestCase):

    def test_adapter_does_not_import_openai_sdk(self):
        path = Path(SRC) / "aurora_studio" / "modules" / "openai_compatible_text_adapter.py"
        content = path.read_text()
        self.assertNotIn("import openai", content)
        self.assertNotIn("from openai", content)

    def test_adapter_does_not_import_requests(self):
        path = Path(SRC) / "aurora_studio" / "modules" / "openai_compatible_text_adapter.py"
        content = path.read_text()
        self.assertNotIn("import requests", content)
        self.assertNotIn("import httpx", content)
        self.assertNotIn("import aiohttp", content)

    def test_adapter_does_not_store_secret(self):
        path = Path(SRC) / "aurora_studio" / "modules" / "openai_compatible_text_adapter.py"
        content = path.read_text()
        self.assertNotIn("self.secret", content)
        self.assertNotIn("self.api_key", content)
        self.assertNotIn("self.token", content)


if __name__ == "__main__":
    unittest.main()

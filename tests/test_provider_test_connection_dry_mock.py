"""Tests for TASK-000105: Provider Test Connection Dry/Mock Pack.

No network calls. No provider SDK. Standard library only.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"


class TestProviderTestConnectionManager(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_test_connection import ProviderTestConnectionManager
        self.mgr = ProviderTestConnectionManager()

    def test_dry_run_passes_for_known_provider(self):
        result = self.mgr.test_dry_run_connection("dry-run-local")
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.mode, "dry_run")

    def test_dry_run_passes_for_any_nonempty_provider(self):
        result = self.mgr.test_dry_run_connection("openai")
        self.assertEqual(result.status, "pass")

    def test_dry_run_fails_for_empty_provider(self):
        result = self.mgr.test_dry_run_connection("")
        self.assertEqual(result.status, "fail")
        self.assertIn("required", result.message.lower())

    def test_mock_passes_deterministically(self):
        r1 = self.mgr.test_mock_connection("openai")
        r2 = self.mgr.test_mock_connection("openai")
        self.assertEqual(r1.status, "pass")
        self.assertEqual(r2.status, "pass")
        # mock response is deterministic based on provider_id
        self.assertEqual(r1.details.get("mock_response"), r2.details.get("mock_response"))

    def test_mock_passes_for_any_provider(self):
        result = self.mgr.test_mock_connection("anthropic")
        self.assertEqual(result.status, "pass")
        self.assertTrue(result.details.get("mock"))

    def test_mock_fails_for_empty_provider(self):
        result = self.mgr.test_mock_connection("")
        self.assertEqual(result.status, "fail")

    def test_blocked_real_returns_blocked(self):
        result = self.mgr.block_real_connection_test("openai")
        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.mode, "blocked_real")

    def test_blocked_real_says_blocked_in_message(self):
        result = self.mgr.block_real_connection_test("openai")
        self.assertIn("blocked", result.message.lower())

    def test_blocked_real_no_network_call_in_details(self):
        result = self.mgr.block_real_connection_test("openai")
        self.assertFalse(result.details.get("network_call", True))

    def test_test_connection_dry_run_mode(self):
        result = self.mgr.test_connection("dry-run-local", "dry_run")
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.mode, "dry_run")

    def test_test_connection_mock_mode(self):
        result = self.mgr.test_connection("openai", "mock")
        self.assertEqual(result.status, "pass")

    def test_test_connection_blocked_real_mode(self):
        result = self.mgr.test_connection("openai", "blocked_real")
        self.assertEqual(result.status, "blocked")

    def test_test_connection_empty_provider_fails(self):
        result = self.mgr.test_connection("", "dry_run")
        self.assertEqual(result.status, "fail")

    def test_test_connection_invalid_mode_fails(self):
        result = self.mgr.test_connection("openai", "real_network")
        self.assertEqual(result.status, "fail")
        self.assertIn("mode", result.message.lower())

    def test_result_json_serializable(self):
        result = self.mgr.test_dry_run_connection("dry-run-local")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["status"], "pass")
        self.assertFalse(parsed["details"]["network_call"])

    def test_mock_result_json_serializable(self):
        result = self.mgr.test_mock_connection("openai")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["status"], "pass")

    def test_blocked_result_json_serializable(self):
        result = self.mgr.block_real_connection_test("openai")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["status"], "blocked")

    def test_no_provider_sdk_imported(self):
        # Check that the openai and anthropic SDK top-level packages are not imported.
        # Our own adapter module (openai_compatible_text_adapter) is intentionally excluded.
        sdk_forbidden = {"openai", "anthropic"}
        imported_top_level = {mod.split(".")[0] for mod in sys.modules}
        for sdk in sdk_forbidden:
            self.assertNotIn(sdk, imported_top_level,
                             f"{sdk} SDK top-level package must not be imported")

    def test_no_network_in_dry_run_details(self):
        result = self.mgr.test_dry_run_connection("openai")
        self.assertFalse(result.details.get("network_call", True))

    def test_no_provider_sdk_in_dry_run_details(self):
        result = self.mgr.test_dry_run_connection("openai")
        self.assertFalse(result.details.get("provider_sdk", True))


class TestProviderTestConnectionContracts(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))

    def test_request_contract_json_serializable(self):
        from aurora_studio.contracts.provider import ProviderTestConnectionRequest
        req = ProviderTestConnectionRequest(
            request_id="r1", provider_id="openai", mode="dry_run"
        )
        serialized = json.dumps(req.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["mode"], "dry_run")

    def test_result_contract_from_dict(self):
        from aurora_studio.contracts.provider import ProviderTestConnectionResult
        d = {
            "result_id": "res1", "request_id": "req1",
            "provider_id": "openai", "mode": "dry_run",
            "status": "pass", "message": "ok",
        }
        result = ProviderTestConnectionResult.from_dict(d)
        self.assertEqual(result.status, "pass")

    def test_test_connection_modes_constant(self):
        from aurora_studio.contracts.provider import TEST_CONNECTION_MODES
        self.assertIn("dry_run", TEST_CONNECTION_MODES)
        self.assertIn("mock", TEST_CONNECTION_MODES)
        self.assertIn("blocked_real", TEST_CONNECTION_MODES)

    def test_test_connection_statuses_constant(self):
        from aurora_studio.contracts.provider import TEST_CONNECTION_STATUSES
        self.assertIn("pass", TEST_CONNECTION_STATUSES)
        self.assertIn("blocked", TEST_CONNECTION_STATUSES)
        self.assertIn("not_configured", TEST_CONNECTION_STATUSES)


class TestUISessionTestConnection(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_test_provider_connection_dry_run_ok(self):
        result = self.sess.test_provider_connection("dry-run-local", "dry_run")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "pass")

    def test_test_provider_connection_mock_ok(self):
        result = self.sess.test_provider_connection("openai", "mock")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "pass")

    def test_test_provider_connection_blocked_real(self):
        result = self.sess.test_provider_connection("openai", "blocked_real")
        self.assertTrue(result.ok)  # UIAction ok; payload status = blocked
        self.assertEqual(result.payload["status"], "blocked")

    def test_test_provider_connection_empty_provider_fails(self):
        result = self.sess.test_provider_connection("", "dry_run")
        self.assertFalse(result.ok)

    def test_test_provider_connection_invalid_mode_fails(self):
        result = self.sess.test_provider_connection("openai", "realnet")
        self.assertFalse(result.ok)

    def test_test_provider_connection_json_serializable(self):
        result = self.sess.test_provider_connection("dry-run-local", "dry_run")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["payload"]["status"], "pass")

    def test_desktop_method_exists(self):
        self.assertTrue(hasattr(self.sess, "test_provider_connection"))


class TestProviderTestConnectionCLI(unittest.TestCase):

    def _run_cli(self, *args):
        result = subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli"] + list(args),
            capture_output=True, text=True,
            env={**__import__("os").environ, "PYTHONPATH": str(SRC)},
        )
        return result

    def test_cli_provider_test_dry_run_outputs_json(self):
        r = self._run_cli("provider-test", "--provider", "dry-run-local", "--mode", "dry_run")
        self.assertEqual(r.returncode, 0)
        parsed = json.loads(r.stdout)
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["status"], "pass")

    def test_cli_provider_test_mock_outputs_json(self):
        r = self._run_cli("provider-test", "--provider", "openai", "--mode", "mock")
        self.assertEqual(r.returncode, 0)
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["status"], "pass")

    def test_cli_provider_test_blocked_real_outputs_json(self):
        r = self._run_cli("provider-test", "--provider", "openai", "--mode", "blocked_real")
        self.assertEqual(r.returncode, 0)
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["status"], "blocked")

    def test_cli_provider_test_no_network_call(self):
        r = self._run_cli("provider-test", "--provider", "dry-run-local", "--mode", "dry_run")
        parsed = json.loads(r.stdout)
        self.assertFalse(parsed["details"]["network_call"])

    def test_cli_provider_test_command_field(self):
        r = self._run_cli("provider-test", "--provider", "dry-run-local", "--mode", "dry_run")
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["command"], "provider-test")


if __name__ == "__main__":
    unittest.main()

"""Tests for TASK-000109: Text Provider Execution UI/CLI Pack.

No network calls. No provider SDK. Standard library only.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"


class TestEvaluateTextProviderRealReadiness(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_readiness_returns_ok(self):
        result = self.sess.evaluate_text_provider_real_readiness("openai")
        self.assertTrue(result.ok)

    def test_readiness_not_ready_by_default(self):
        result = self.sess.evaluate_text_provider_real_readiness("openai")
        self.assertFalse(result.payload["real_execution_ready"])

    def test_readiness_includes_prerequisites(self):
        result = self.sess.evaluate_text_provider_real_readiness("openai")
        self.assertIn("prerequisites", result.payload)
        self.assertGreater(len(result.payload["prerequisites"]), 0)

    def test_readiness_includes_missing_conditions(self):
        result = self.sess.evaluate_text_provider_real_readiness("openai")
        self.assertIn("missing_conditions", result.payload)
        self.assertGreater(len(result.payload["missing_conditions"]), 0)

    def test_readiness_includes_gate_decision(self):
        result = self.sess.evaluate_text_provider_real_readiness("openai")
        self.assertIn("gate_decision", result.payload)
        self.assertFalse(result.payload["gate_decision"]["allowed"])

    def test_readiness_json_serializable(self):
        result = self.sess.evaluate_text_provider_real_readiness("openai")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["payload"]["real_execution_ready"])

    def test_readiness_with_all_conditions_satisfied(self):
        from aurora_studio.contracts.provider_security import REAL_TEXT_PREREQUISITES
        fake_config = {p: True for p in REAL_TEXT_PREREQUISITES}
        result = self.sess.evaluate_text_provider_real_readiness("openai", config=fake_config)
        self.assertTrue(result.ok)
        self.assertTrue(result.payload["real_execution_ready"])
        self.assertEqual(len(result.payload["missing_conditions"]), 0)


class TestListTextProviderRuns(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_list_runs_ok_empty(self):
        result = self.sess.list_text_provider_runs()
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["total"], 0)

    def test_list_runs_json_serializable(self):
        result = self.sess.list_text_provider_runs()
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertIn("total", parsed["payload"])

    def test_list_runs_filter_by_provider(self):
        result = self.sess.list_text_provider_runs(provider_id="openai")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["provider_id"], "openai")

    def test_record_and_list_run(self):
        self.sess._record_text_provider_run({
            "provider_id": "openai",
            "status": "mock",
            "text": "hello",
        })
        result = self.sess.list_text_provider_runs(provider_id="openai")
        self.assertEqual(result.payload["total"], 1)

    def test_record_run_strips_secret_fields(self):
        self.sess._record_text_provider_run({
            "provider_id": "openai",
            "status": "mock",
            "ephemeral_secret": "sk-should-not-be-stored",
            "api_key": "sk-also-no",
        })
        result = self.sess.list_text_provider_runs()
        for run in result.payload["runs"]:
            self.assertNotIn("ephemeral_secret", run)
            self.assertNotIn("api_key", run)

    def test_list_runs_limit(self):
        for i in range(10):
            self.sess._record_text_provider_run({"provider_id": "openai", "status": "mock", "n": i})
        result = self.sess.list_text_provider_runs(limit=3)
        self.assertLessEqual(len(result.payload["runs"]), 3)


class TestUISessionTextProviderMock(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_execute_text_provider_mock_ok(self):
        result = self.sess.execute_text_provider_mock("openai", "Test prompt")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")

    def test_execute_text_provider_mock_no_network(self):
        result = self.sess.execute_text_provider_mock("openai", "Test prompt")
        self.assertFalse(result.payload["network_call"])

    def test_execute_text_provider_real_blocked_ok(self):
        result = self.sess.execute_text_provider_real_blocked("openai", "Test prompt")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "blocked")

    def test_execute_real_with_ephemeral_no_confirm_fails(self):
        result = self.sess.execute_text_provider_real_with_ephemeral_secret(
            "openai", "test", "sk-fake", confirm=False
        )
        self.assertFalse(result.ok)

    def test_execute_real_confirm_true_blocked_by_gate(self):
        result = self.sess.execute_text_provider_real_with_ephemeral_secret(
            "openai", "test", "sk-fake", confirm=True
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "blocked")

    def test_execute_real_payload_no_secret(self):
        result = self.sess.execute_text_provider_real_with_ephemeral_secret(
            "openai", "test", "sk-supersecret", confirm=True
        )
        payload_str = json.dumps(result.to_dict())
        self.assertNotIn("sk-supersecret", payload_str)


class TestCLITextProviderMock(unittest.TestCase):

    def _run_cli(self, *args):
        result = subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli.main"] + list(args),
            capture_output=True, text=True,
            env={**__import__("os").environ, "PYTHONPATH": str(SRC)},
        )
        return result

    def test_text_provider_mock_exits_zero(self):
        r = self._run_cli("text-provider-mock", "--provider", "openai", "--prompt", "Test")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_text_provider_mock_json_output(self):
        r = self._run_cli("text-provider-mock", "--provider", "openai", "--prompt", "Test")
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["command"], "text-provider-mock")
        self.assertEqual(parsed["status"], "mock")
        self.assertFalse(parsed["network_call"])

    def test_text_provider_mock_no_secret_in_output(self):
        r = self._run_cli("text-provider-mock", "--provider", "openai", "--prompt", "Test")
        self.assertNotIn("sk-", r.stdout)

    def test_text_provider_readiness_exits_zero(self):
        r = self._run_cli("text-provider-readiness", "--provider", "openai")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_text_provider_readiness_json_output(self):
        r = self._run_cli("text-provider-readiness", "--provider", "openai")
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["command"], "text-provider-readiness")
        self.assertFalse(parsed["real_execution_ready"])
        self.assertIn("prerequisites", parsed)

    def test_text_provider_readiness_missing_conditions_present(self):
        r = self._run_cli("text-provider-readiness", "--provider", "openai")
        parsed = json.loads(r.stdout)
        self.assertGreater(len(parsed["missing_conditions"]), 0)


if __name__ == "__main__":
    unittest.main()

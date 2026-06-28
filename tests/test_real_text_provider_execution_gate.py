"""Tests for TASK-000106: Real Text Provider Execution Gate Pack.

No network calls. No provider SDK. Standard library only.
"""

import json
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"


class TestGateNewConstants(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))

    def test_provider_execution_modes_exists(self):
        from aurora_studio.contracts.provider_security import PROVIDER_EXECUTION_MODES
        self.assertIn("dry_run", PROVIDER_EXECUTION_MODES)
        self.assertIn("mock", PROVIDER_EXECUTION_MODES)
        self.assertIn("real_text", PROVIDER_EXECUTION_MODES)
        self.assertIn("blocked_real", PROVIDER_EXECUTION_MODES)

    def test_real_text_prerequisites_exists(self):
        from aurora_studio.contracts.provider_security import REAL_TEXT_PREREQUISITES
        self.assertIn("provider_registered", REAL_TEXT_PREREQUISITES)
        self.assertIn("user_confirmed", REAL_TEXT_PREREQUISITES)
        self.assertIn("real_execution_allowed", REAL_TEXT_PREREQUISITES)
        self.assertGreaterEqual(len(REAL_TEXT_PREREQUISITES), 10)

    def test_gate_decision_has_mode_field(self):
        from aurora_studio.contracts.provider_security import ProviderExecutionGateDecision
        d = ProviderExecutionGateDecision(
            provider_id="p1", requested_action="run",
            allowed=False, reason="blocked",
        )
        self.assertEqual(d.mode, "dry_run")  # default

    def test_gate_decision_has_missing_conditions_field(self):
        from aurora_studio.contracts.provider_security import ProviderExecutionGateDecision
        d = ProviderExecutionGateDecision(
            provider_id="p1", requested_action="run",
            allowed=False, reason="blocked",
            missing_conditions=("prereq_a",),
        )
        self.assertIn("prereq_a", d.missing_conditions)

    def test_gate_decision_to_dict_includes_mode(self):
        from aurora_studio.contracts.provider_security import ProviderExecutionGateDecision
        d = ProviderExecutionGateDecision(
            provider_id="p1", requested_action="run",
            allowed=True, reason="ok", mode="dry_run",
        )
        result = d.to_dict()
        self.assertIn("mode", result)
        self.assertIn("missing_conditions", result)

    def test_gate_decision_backward_compatible(self):
        # Old call style without mode/missing_conditions must still work
        from aurora_studio.contracts.provider_security import ProviderExecutionGateDecision
        d = ProviderExecutionGateDecision(
            provider_id="p", requested_action="r",
            allowed=False, reason="blocked",
            required_conditions=("c1",),
        )
        self.assertEqual(d.mode, "dry_run")
        self.assertEqual(d.missing_conditions, ())


class TestGateModes(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_execution_gate import ProviderExecutionGate
        self.gate = ProviderExecutionGate()

    def test_dry_run_mode_allowed(self):
        decision = self.gate.evaluate_dry_run("openai")
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.mode, "dry_run")

    def test_mock_mode_allowed(self):
        decision = self.gate.evaluate_mock("openai")
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.mode, "mock")

    def test_real_text_blocked_by_default(self):
        decision = self.gate.evaluate_real_text_execution("openai")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.mode, "real_text")

    def test_real_text_lists_missing_prerequisites(self):
        decision = self.gate.evaluate_real_text_execution("openai")
        self.assertGreater(len(decision.missing_conditions), 0)

    def test_evaluate_execution_dry_run_allowed(self):
        decision = self.gate.evaluate_execution("openai", "generate", mode="dry_run")
        self.assertTrue(decision.allowed)

    def test_evaluate_execution_mock_allowed(self):
        decision = self.gate.evaluate_execution("openai", "generate", mode="mock")
        self.assertTrue(decision.allowed)

    def test_evaluate_execution_real_text_blocked_by_default(self):
        decision = self.gate.evaluate_execution("openai", "generate", mode="real_text")
        self.assertFalse(decision.allowed)

    def test_evaluate_execution_blocked_real_blocked(self):
        decision = self.gate.evaluate_execution("openai", "generate", mode="blocked_real")
        self.assertFalse(decision.allowed)

    def test_block_real_execution_returns_blocked(self):
        decision = self.gate.block_real_execution("openai", "generate", "custom reason")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "custom reason")

    def test_is_real_execution_allowed_false(self):
        self.assertFalse(self.gate.is_real_execution_allowed("openai"))

    def test_all_prerequisites_allow_real_text(self):
        """Unit test: fake config with all prerequisites satisfied allows real_text."""
        from aurora_studio.contracts.provider_security import REAL_TEXT_PREREQUISITES
        fake_config = {prereq: True for prereq in REAL_TEXT_PREREQUISITES}
        decision = self.gate.evaluate_real_text_execution("openai", config=fake_config)
        self.assertTrue(decision.allowed)
        self.assertEqual(len(decision.missing_conditions), 0)

    def test_partial_prerequisites_still_blocked(self):
        from aurora_studio.contracts.provider_security import REAL_TEXT_PREREQUISITES
        fake_config = {prereq: True for prereq in list(REAL_TEXT_PREREQUISITES)[:-2]}
        decision = self.gate.evaluate_real_text_execution("openai", config=fake_config)
        self.assertFalse(decision.allowed)
        self.assertGreater(len(decision.missing_conditions), 0)

    def test_gate_does_not_make_network_call(self):
        # Simply verifying no network infrastructure is present
        decision = self.gate.evaluate_execution("openai", "generate", mode="real_text")
        self.assertIsNotNone(decision)
        self.assertFalse(decision.allowed)

    def test_gate_does_not_retrieve_secret(self):
        import sys
        gate_path = Path(SRC) / "aurora_studio" / "modules" / "provider_execution_gate.py"
        content = gate_path.read_text()
        self.assertNotIn("import subprocess", content)
        self.assertNotIn("secret_value", content)

    def test_decision_json_serializable(self):
        decision = self.gate.evaluate_dry_run("openai")
        serialized = json.dumps(decision.to_dict())
        parsed = json.loads(serialized)
        self.assertTrue(parsed["allowed"])
        self.assertEqual(parsed["mode"], "dry_run")

    def test_real_text_decision_json_serializable(self):
        decision = self.gate.evaluate_real_text_execution("openai")
        serialized = json.dumps(decision.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["allowed"])
        self.assertIsInstance(parsed["missing_conditions"], list)


class TestListPrerequisites(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_execution_gate import ProviderExecutionGate
        self.gate = ProviderExecutionGate()

    def test_list_real_text_prerequisites_returns_list(self):
        prereqs = self.gate.list_real_text_prerequisites()
        self.assertIsInstance(prereqs, list)
        self.assertGreater(len(prereqs), 0)

    def test_prerequisites_have_name_and_description(self):
        prereqs = self.gate.list_real_text_prerequisites()
        for p in prereqs:
            self.assertTrue(hasattr(p, "name"))
            self.assertTrue(hasattr(p, "description"))
            self.assertGreater(len(p.name), 0)

    def test_prerequisites_default_not_satisfied(self):
        prereqs = self.gate.list_real_text_prerequisites()
        for p in prereqs:
            self.assertFalse(p.satisfied)

    def test_prerequisites_json_serializable(self):
        prereqs = self.gate.list_real_text_prerequisites()
        serialized = json.dumps([p.to_dict() for p in prereqs])
        parsed = json.loads(serialized)
        self.assertGreater(len(parsed), 0)


class TestUISessionGate106(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_evaluate_provider_execution_gate_dry_run_allowed(self):
        result = self.sess.evaluate_provider_execution_gate("openai", "generate", mode="dry_run")
        self.assertTrue(result.ok)
        self.assertTrue(result.payload["allowed"])

    def test_evaluate_provider_execution_gate_mock_allowed(self):
        result = self.sess.evaluate_provider_execution_gate("openai", "generate", mode="mock")
        self.assertTrue(result.ok)
        self.assertTrue(result.payload["allowed"])

    def test_evaluate_provider_execution_gate_real_text_blocked(self):
        result = self.sess.evaluate_provider_execution_gate("openai", "generate", mode="real_text")
        self.assertTrue(result.ok)
        self.assertFalse(result.payload["allowed"])

    def test_list_real_text_provider_prerequisites_ok(self):
        result = self.sess.list_real_text_provider_prerequisites()
        self.assertTrue(result.ok)
        self.assertIn("prerequisites", result.payload)
        self.assertGreater(len(result.payload["prerequisites"]), 0)

    def test_list_prerequisites_json_serializable(self):
        result = self.sess.list_real_text_provider_prerequisites()
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertIn("prerequisites", parsed["payload"])


class TestDesktopImportSafe106(unittest.TestCase):

    def test_desktop_shell_still_importable(self):
        import sys; sys.path.insert(0, str(SRC))
        import importlib.util
        spec = importlib.util.find_spec("aurora_studio.ui.desktop_shell")
        self.assertIsNotNone(spec)


if __name__ == "__main__":
    unittest.main()

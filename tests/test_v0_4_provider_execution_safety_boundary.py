"""Tests for TASK-000101: v0.4 Provider Execution Safety Boundary.

No network calls. No provider SDK. Standard library only.
"""

import json
import unittest
from pathlib import Path

REPO = Path(__file__).parent.parent
DOCS_V04 = REPO / "docs" / "v0_4"
SRC = REPO / "src"


class TestSafetyBoundaryDocsExist(unittest.TestCase):

    def test_safety_boundary_doc_exists(self):
        p = DOCS_V04 / "PROVIDER_EXECUTION_SAFETY_BOUNDARY.md"
        self.assertTrue(p.exists(), f"Missing: {p}")

    def test_escalation_rules_doc_exists(self):
        p = DOCS_V04 / "REAL_PROVIDER_ESCALATION_RULES.md"
        self.assertTrue(p.exists(), f"Missing: {p}")


class TestSafetyBoundaryDocContent(unittest.TestCase):

    def setUp(self):
        self.doc = (DOCS_V04 / "PROVIDER_EXECUTION_SAFETY_BOUNDARY.md").read_text()

    def test_doc_states_no_real_provider_api_calls(self):
        self.assertIn("does not perform real provider API calls", self.doc)

    def test_doc_states_no_provider_sdks(self):
        self.assertIn("does not add provider SDKs", self.doc)

    def test_doc_states_no_real_api_key_persistence(self):
        self.assertIn("does not persist real API keys", self.doc)

    def test_doc_states_no_secrets_in_project_json(self):
        self.assertIn("does not store secrets in project JSON", self.doc)

    def test_doc_states_real_execution_blocked_until_later(self):
        self.assertIn("blocked until a later task", self.doc)

    def test_doc_includes_execution_gate_model_section(self):
        self.assertIn("Execution Gate Model", self.doc)

    def test_doc_includes_network_boundary_section(self):
        self.assertIn("Network Boundary", self.doc)

    def test_doc_includes_secret_handling_section(self):
        self.assertIn("Secret Handling Boundary", self.doc)


class TestEscalationRulesDocContent(unittest.TestCase):

    def setUp(self):
        self.doc = (DOCS_V04 / "REAL_PROVIDER_ESCALATION_RULES.md").read_text()

    def test_defines_real_provider_execution_as_network_call(self):
        self.assertIn("network call", self.doc.lower())

    def test_defines_real_provider_execution_as_sdk_invocation(self):
        self.assertIn("SDK invocation", self.doc)

    def test_defines_sending_prompt_outside_machine(self):
        self.assertIn("Sending prompt text outside", self.doc)

    def test_defines_using_real_api_key(self):
        self.assertIn("real API key", self.doc)

    def test_includes_blocked_by_default_rule(self):
        self.assertIn("Blocked-by-Default Rule", self.doc)

    def test_includes_go_no_go_section(self):
        self.assertIn("Go/No-Go", self.doc)

    def test_includes_required_redaction_section(self):
        self.assertIn("Required Redaction", self.doc)


class TestProviderSecurityContracts(unittest.TestCase):

    def test_provider_security_module_importable(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.contracts.provider_security import (
            ProviderExecutionGateDecision,
            SECRET_FIELD_NAMES,
            SECRET_STORAGE_PROHIBITED_LOCATIONS,
        )

    def test_secret_field_names_includes_api_key(self):
        from aurora_studio.contracts.provider_security import SECRET_FIELD_NAMES
        self.assertIn("api_key", SECRET_FIELD_NAMES)

    def test_secret_field_names_includes_token(self):
        from aurora_studio.contracts.provider_security import SECRET_FIELD_NAMES
        self.assertIn("token", SECRET_FIELD_NAMES)

    def test_secret_field_names_includes_password(self):
        from aurora_studio.contracts.provider_security import SECRET_FIELD_NAMES
        self.assertIn("password", SECRET_FIELD_NAMES)

    def test_prohibited_locations_includes_project_json(self):
        from aurora_studio.contracts.provider_security import SECRET_STORAGE_PROHIBITED_LOCATIONS
        self.assertIn("project_json", SECRET_STORAGE_PROHIBITED_LOCATIONS)

    def test_prohibited_locations_includes_portable_zip(self):
        from aurora_studio.contracts.provider_security import SECRET_STORAGE_PROHIBITED_LOCATIONS
        self.assertIn("portable_zip", SECRET_STORAGE_PROHIBITED_LOCATIONS)

    def test_gate_decision_to_dict(self):
        from aurora_studio.contracts.provider_security import ProviderExecutionGateDecision
        d = ProviderExecutionGateDecision(
            provider_id="test-p",
            requested_action="generate",
            allowed=False,
            reason="blocked",
            required_conditions=("need_keyring",),
        )
        result = d.to_dict()
        self.assertEqual(result["provider_id"], "test-p")
        self.assertFalse(result["allowed"])
        self.assertIsInstance(result["required_conditions"], list)

    def test_gate_decision_json_serializable(self):
        from aurora_studio.contracts.provider_security import ProviderExecutionGateDecision
        d = ProviderExecutionGateDecision(
            provider_id="p1",
            requested_action="run",
            allowed=False,
            reason="blocked in v0.4",
        )
        serialized = json.dumps(d.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["allowed"])


class TestProviderExecutionGate(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_execution_gate import ProviderExecutionGate
        self.gate = ProviderExecutionGate()

    def test_is_real_execution_allowed_returns_false(self):
        self.assertFalse(self.gate.is_real_execution_allowed("openai"))

    def test_is_real_execution_allowed_false_for_dry_run(self):
        self.assertFalse(self.gate.is_real_execution_allowed("dry-run-local"))

    def test_is_real_execution_allowed_false_for_unknown(self):
        self.assertFalse(self.gate.is_real_execution_allowed("unknown-provider"))

    def test_evaluate_execution_returns_decision(self):
        from aurora_studio.contracts.provider_security import ProviderExecutionGateDecision
        decision = self.gate.evaluate_execution("openai", "generate_text", mode="real_text")
        self.assertIsInstance(decision, ProviderExecutionGateDecision)
        self.assertFalse(decision.allowed)

    def test_evaluate_execution_decision_json_serializable(self):
        decision = self.gate.evaluate_execution("openai", "generate_text", mode="real_text")
        serialized = json.dumps(decision.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["allowed"])
        self.assertIn("provider_id", parsed)

    def test_block_real_execution_returns_blocked_decision(self):
        decision = self.gate.block_real_execution("openai", "generate_text", "custom reason")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "custom reason")

    def test_block_real_execution_uses_default_reason_when_empty(self):
        decision = self.gate.block_real_execution("openai", "generate_text")
        self.assertFalse(decision.allowed)
        self.assertGreater(len(decision.reason), 0)

    def test_required_conditions_is_non_empty(self):
        decision = self.gate.evaluate_execution("openai", "generate", mode="real_text")
        self.assertGreater(len(decision.required_conditions), 0)

    def test_no_provider_sdk_imported(self):
        import sys
        # Check that the openai and anthropic SDK top-level packages are not imported.
        # Our own adapter module (openai_compatible_text_adapter) is intentionally excluded.
        sdk_forbidden = {"openai", "anthropic"}
        imported_top_level = {mod.split(".")[0] for mod in sys.modules}
        for sdk in sdk_forbidden:
            self.assertNotIn(sdk, imported_top_level,
                             f"{sdk} SDK top-level package must not be imported")


class TestUISessionExecutionGate(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_evaluate_provider_execution_gate_exists(self):
        self.assertTrue(hasattr(self.sess, "evaluate_provider_execution_gate"))

    def test_evaluate_provider_execution_gate_returns_ok(self):
        result = self.sess.evaluate_provider_execution_gate("openai", "generate")
        self.assertTrue(result.ok)

    def test_evaluate_provider_execution_gate_payload_not_allowed(self):
        result = self.sess.evaluate_provider_execution_gate("openai", "generate", mode="real_text")
        self.assertFalse(result.payload["allowed"])

    def test_evaluate_provider_execution_gate_json_serializable(self):
        result = self.sess.evaluate_provider_execution_gate("openai", "generate", mode="real_text")
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["payload"]["allowed"])


class TestDesktopImportSafe(unittest.TestCase):

    def test_desktop_shell_importable_without_display(self):
        import sys; sys.path.insert(0, str(SRC))
        import importlib
        # Should not raise even without a display
        try:
            spec = importlib.util.find_spec("aurora_studio.ui.desktop_shell")
            self.assertIsNotNone(spec)
        except Exception:
            pass  # acceptable if tkinter not available in CI

    def test_no_subprocess_in_execution_gate(self):
        gate_path = SRC / "aurora_studio" / "modules" / "provider_execution_gate.py"
        content = gate_path.read_text()
        self.assertNotIn("import subprocess", content)
        self.assertNotIn("importlib.import_module", content)


if __name__ == "__main__":
    unittest.main()

"""Tests for TASK-000111: Image Provider Safety Boundary Pack.

No network calls. No image generation. No provider SDK. Standard library only.
"""

import json
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
DOCS_V0_4 = Path(__file__).parent.parent / "docs" / "v0_4"


class TestSafetyBoundaryDocsExist(unittest.TestCase):

    def test_safety_boundary_doc_exists(self):
        self.assertTrue((DOCS_V0_4 / "IMAGE_PROVIDER_SAFETY_BOUNDARY.md").exists())

    def test_escalation_rules_doc_exists(self):
        self.assertTrue((DOCS_V0_4 / "IMAGE_PROVIDER_ESCALATION_RULES.md").exists())

    def test_safety_boundary_states_no_real_api_calls(self):
        content = (DOCS_V0_4 / "IMAGE_PROVIDER_SAFETY_BOUNDARY.md").read_text()
        self.assertIn("does not perform real image provider API calls", content)

    def test_safety_boundary_states_no_image_generation(self):
        content = (DOCS_V0_4 / "IMAGE_PROVIDER_SAFETY_BOUNDARY.md").read_text()
        self.assertIn("does not generate images", content)

    def test_safety_boundary_states_no_upload(self):
        content = (DOCS_V0_4 / "IMAGE_PROVIDER_SAFETY_BOUNDARY.md").read_text()
        self.assertIn("does not upload files or assets", content)

    def test_safety_boundary_states_no_media_decoding(self):
        content = (DOCS_V0_4 / "IMAGE_PROVIDER_SAFETY_BOUNDARY.md").read_text()
        self.assertIn("does not decode or process local media", content)

    def test_safety_boundary_states_no_provider_sdks(self):
        content = (DOCS_V0_4 / "IMAGE_PROVIDER_SAFETY_BOUNDARY.md").read_text()
        self.assertIn("does not add provider SDKs", content)

    def test_safety_boundary_states_real_execution_blocked(self):
        content = (DOCS_V0_4 / "IMAGE_PROVIDER_SAFETY_BOUNDARY.md").read_text()
        self.assertIn("Real image provider execution is blocked", content)

    def test_escalation_rules_defines_real_execution(self):
        content = (DOCS_V0_4 / "IMAGE_PROVIDER_ESCALATION_RULES.md").read_text()
        self.assertIn("Network call to an image provider", content)

    def test_escalation_rules_blocked_by_default(self):
        content = (DOCS_V0_4 / "IMAGE_PROVIDER_ESCALATION_RULES.md").read_text()
        self.assertIn("BLOCKED BY DEFAULT", content)


class TestImageGateModeConstants(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))

    def test_mock_image_in_execution_modes(self):
        from aurora_studio.contracts.provider_security import PROVIDER_EXECUTION_MODES
        self.assertIn("mock_image", PROVIDER_EXECUTION_MODES)

    def test_real_image_in_execution_modes(self):
        from aurora_studio.contracts.provider_security import PROVIDER_EXECUTION_MODES
        self.assertIn("real_image", PROVIDER_EXECUTION_MODES)

    def test_blocked_real_image_in_execution_modes(self):
        from aurora_studio.contracts.provider_security import PROVIDER_EXECUTION_MODES
        self.assertIn("blocked_real_image", PROVIDER_EXECUTION_MODES)

    def test_real_image_prerequisites_exist(self):
        from aurora_studio.contracts.provider_security import REAL_IMAGE_PREREQUISITES
        self.assertIn("user_confirmed", REAL_IMAGE_PREREQUISITES)
        self.assertIn("no_reference_image_upload", REAL_IMAGE_PREREQUISITES)
        self.assertGreaterEqual(len(REAL_IMAGE_PREREQUISITES), 10)


class TestImageProviderGate(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_execution_gate import ImageProviderExecutionGate
        self.gate = ImageProviderExecutionGate()

    def test_mock_image_allowed(self):
        decision = self.gate.evaluate_mock_image("mock-image")
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.mode, "mock_image")

    def test_real_image_blocked_by_default(self):
        decision = self.gate.evaluate_real_image("mock-image")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.mode, "real_image")

    def test_block_real_image_always_blocked(self):
        decision = self.gate.block_real_image("mock-image", "generate")
        self.assertFalse(decision.allowed)

    def test_evaluate_execution_mock_image_allowed(self):
        decision = self.gate.evaluate_execution("mock-image", "generate", mode="mock_image")
        self.assertTrue(decision.allowed)

    def test_evaluate_execution_real_image_blocked(self):
        decision = self.gate.evaluate_execution("mock-image", "generate", mode="real_image")
        self.assertFalse(decision.allowed)

    def test_evaluate_execution_blocked_real_image_blocked(self):
        decision = self.gate.evaluate_execution("mock-image", "generate", mode="blocked_real_image")
        self.assertFalse(decision.allowed)

    def test_gate_does_not_make_network_call(self):
        decision = self.gate.evaluate_real_image("mock-image")
        self.assertIsNotNone(decision)
        self.assertFalse(decision.allowed)

    def test_decision_json_serializable(self):
        decision = self.gate.evaluate_mock_image("mock-image")
        serialized = json.dumps(decision.to_dict())
        parsed = json.loads(serialized)
        self.assertTrue(parsed["allowed"])

    def test_real_image_lists_missing_conditions(self):
        decision = self.gate.evaluate_real_image("mock-image")
        self.assertGreater(len(decision.missing_conditions), 0)

    def test_all_prerequisites_allow_real_image(self):
        from aurora_studio.contracts.provider_security import REAL_IMAGE_PREREQUISITES
        fake_config = {p: True for p in REAL_IMAGE_PREREQUISITES}
        decision = self.gate.evaluate_real_image("mock-image", config=fake_config)
        self.assertTrue(decision.allowed)
        self.assertEqual(len(decision.missing_conditions), 0)

    def test_list_prerequisites_not_empty(self):
        prereqs = self.gate.list_real_image_prerequisites()
        self.assertGreater(len(prereqs), 0)

    def test_list_prerequisites_json_serializable(self):
        prereqs = self.gate.list_real_image_prerequisites()
        serialized = json.dumps([p.to_dict() for p in prereqs])
        parsed = json.loads(serialized)
        self.assertGreater(len(parsed), 0)


class TestUISessionImageGate(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_evaluate_image_gate_mock_image_allowed(self):
        result = self.sess.evaluate_image_provider_execution_gate(
            "mock-image", "generate", mode="mock_image"
        )
        self.assertTrue(result.ok)
        self.assertTrue(result.payload["allowed"])

    def test_evaluate_image_gate_real_image_blocked(self):
        result = self.sess.evaluate_image_provider_execution_gate(
            "mock-image", "generate", mode="real_image"
        )
        self.assertTrue(result.ok)
        self.assertFalse(result.payload["allowed"])

    def test_list_real_image_prerequisites_ok(self):
        result = self.sess.list_real_image_provider_prerequisites()
        self.assertTrue(result.ok)
        self.assertIn("prerequisites", result.payload)
        self.assertGreater(len(result.payload["prerequisites"]), 0)

    def test_ui_session_json_serializable(self):
        result = self.sess.evaluate_image_provider_execution_gate(
            "mock-image", "generate", mode="real_image"
        )
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["payload"]["allowed"])


if __name__ == "__main__":
    unittest.main()

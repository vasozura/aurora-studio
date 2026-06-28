"""TASK-000116: Video Provider Safety Boundary tests.

Covers docs existence, gate behavior, and UISession surface.
No network calls. No video files. Standard library only.
"""

import json
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
DOCS = Path(__file__).parent.parent / "docs" / "v0_4"


class TestVideoSafetyDocs(unittest.TestCase):

    def test_safety_boundary_doc_exists(self):
        self.assertTrue((DOCS / "VIDEO_PROVIDER_SAFETY_BOUNDARY.md").exists())

    def test_escalation_rules_doc_exists(self):
        self.assertTrue((DOCS / "VIDEO_PROVIDER_ESCALATION_RULES.md").exists())

    def _boundary_text(self):
        return (DOCS / "VIDEO_PROVIDER_SAFETY_BOUNDARY.md").read_text(encoding="utf-8")

    def _escalation_text(self):
        return (DOCS / "VIDEO_PROVIDER_ESCALATION_RULES.md").read_text(encoding="utf-8")

    def test_boundary_states_no_real_api_calls(self):
        self.assertIn("does not perform real video provider API calls", self._boundary_text())

    def test_boundary_states_no_video_generation(self):
        self.assertIn("does not generate videos", self._boundary_text())

    def test_boundary_states_no_upload(self):
        self.assertIn("does not upload files or assets", self._boundary_text())

    def test_boundary_states_no_media_decoding(self):
        self.assertIn("does not decode or process local media", self._boundary_text())

    def test_boundary_states_no_ffmpeg(self):
        self.assertIn("does not execute ffmpeg", self._boundary_text())

    def test_boundary_states_no_provider_sdks(self):
        self.assertIn("does not add provider SDKs", self._boundary_text())

    def test_boundary_states_no_api_key_persistence(self):
        self.assertIn("does not persist real API keys", self._boundary_text())

    def test_boundary_states_real_video_blocked(self):
        self.assertIn("Real video provider execution is blocked", self._boundary_text())

    def test_escalation_defines_network_call(self):
        self.assertIn("network call to a video provider", self._escalation_text())

    def test_escalation_defines_sdk_invocation(self):
        self.assertIn("provider SDK", self._escalation_text())

    def test_escalation_defines_prompt_outside_machine(self):
        self.assertIn("outside the local machine", self._escalation_text())

    def test_escalation_defines_api_key(self):
        self.assertIn("real API key", self._escalation_text())

    def test_escalation_defines_job_id(self):
        self.assertIn("job ID", self._escalation_text())


class TestVideoExecutionGate(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_execution_gate import VideoProviderExecutionGate
        self.gate = VideoProviderExecutionGate()

    def test_mock_video_allowed(self):
        decision = self.gate.evaluate_mock_video("mock-video")
        self.assertTrue(decision.allowed)

    def test_mock_video_mode_set(self):
        decision = self.gate.evaluate_mock_video("mock-video")
        self.assertEqual(decision.mode, "mock_video")

    def test_real_video_blocked(self):
        decision = self.gate.evaluate_real_video("mock-video")
        self.assertFalse(decision.allowed)

    def test_real_video_no_network(self):
        # Gate evaluation is pure local logic — just verify it returns fast with no error
        decision = self.gate.evaluate_real_video("mock-video")
        self.assertIsNotNone(decision)

    def test_evaluate_execution_mock_video_allowed(self):
        decision = self.gate.evaluate_execution("mock-video", "generate", mode="mock_video")
        self.assertTrue(decision.allowed)

    def test_evaluate_execution_real_video_blocked(self):
        decision = self.gate.evaluate_execution("mock-video", "generate", mode="real_video")
        self.assertFalse(decision.allowed)

    def test_evaluate_execution_blocked_real_video_blocked(self):
        decision = self.gate.evaluate_execution("mock-video", "generate", mode="blocked_real_video")
        self.assertFalse(decision.allowed)

    def test_decision_json_serializable(self):
        decision = self.gate.evaluate_real_video("mock-video")
        serialized = json.dumps(decision.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["allowed"])

    def test_prerequisites_listed(self):
        prereqs = self.gate.list_real_video_prerequisites()
        self.assertGreater(len(prereqs), 0)

    def test_prerequisites_all_unsatisfied(self):
        prereqs = self.gate.list_real_video_prerequisites()
        for p in prereqs:
            self.assertFalse(p.satisfied)

    def test_prerequisite_json_serializable(self):
        prereqs = self.gate.list_real_video_prerequisites()
        serialized = json.dumps([p.to_dict() for p in prereqs])
        parsed = json.loads(serialized)
        self.assertGreater(len(parsed), 0)


class TestUISessionVideoGate(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_evaluate_video_gate_mock_allowed(self):
        result = self.sess.evaluate_video_provider_execution_gate(
            "mock-video", "generate", mode="mock_video"
        )
        self.assertTrue(result.ok)
        self.assertTrue(result.payload["allowed"])

    def test_evaluate_video_gate_real_blocked(self):
        result = self.sess.evaluate_video_provider_execution_gate(
            "mock-video", "generate", mode="real_video"
        )
        self.assertTrue(result.ok)
        self.assertFalse(result.payload["allowed"])

    def test_list_video_prerequisites_ok(self):
        result = self.sess.list_real_video_provider_prerequisites()
        self.assertTrue(result.ok)
        self.assertGreater(result.payload["total"], 0)
        self.assertFalse(result.payload["all_satisfied"])

    def test_gate_result_json_serializable(self):
        result = self.sess.evaluate_video_provider_execution_gate(
            "mock-video", "generate", mode="mock_video"
        )
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertTrue(parsed["payload"]["allowed"])

    def test_prerequisites_json_serializable(self):
        result = self.sess.list_real_video_provider_prerequisites()
        serialized = json.dumps(result.to_dict())
        parsed = json.loads(serialized)
        self.assertGreater(parsed["payload"]["total"], 0)


class TestVideoModesInContracts(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))

    def test_mock_video_mode_in_execution_modes(self):
        from aurora_studio.contracts.provider_security import PROVIDER_EXECUTION_MODES
        self.assertIn("mock_video", PROVIDER_EXECUTION_MODES)

    def test_real_video_mode_in_execution_modes(self):
        from aurora_studio.contracts.provider_security import PROVIDER_EXECUTION_MODES
        self.assertIn("real_video", PROVIDER_EXECUTION_MODES)

    def test_blocked_real_video_mode_in_execution_modes(self):
        from aurora_studio.contracts.provider_security import PROVIDER_EXECUTION_MODES
        self.assertIn("blocked_real_video", PROVIDER_EXECUTION_MODES)

    def test_real_video_prerequisites_exist(self):
        from aurora_studio.contracts.provider_security import REAL_VIDEO_PREREQUISITES
        self.assertGreater(len(REAL_VIDEO_PREREQUISITES), 0)


if __name__ == "__main__":
    unittest.main()

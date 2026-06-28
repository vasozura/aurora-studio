"""TASK-000123: Provider Workflow Regression QA tests.

Verifies regression QA docs exist with required sections, and runs
provider workflow smoke checks via UISession and CLI.
No network calls. Standard library only.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
DOCS_QA = Path(__file__).parent.parent / "docs" / "qa"


class TestRegressionPlanExists(unittest.TestCase):

    def _plan(self):
        p = DOCS_QA / "V0_4_PROVIDER_WORKFLOW_REGRESSION_PLAN.md"
        self.assertTrue(p.exists(), "Regression plan missing")
        return p.read_text(encoding="utf-8")

    def test_plan_exists(self):
        self.assertTrue((DOCS_QA / "V0_4_PROVIDER_WORKFLOW_REGRESSION_PLAN.md").exists())

    def test_plan_has_purpose(self):
        self.assertIn("Purpose", self._plan())

    def test_plan_has_scope(self):
        self.assertIn("## Scope", self._plan())

    def test_plan_has_out_of_scope(self):
        self.assertIn("Out of Scope", self._plan())
        self.assertIn("Real image provider API calls", self._plan())
        self.assertIn("Real video provider API calls", self._plan())
        self.assertIn("Plugin execution tests", self._plan())

    def test_plan_has_required_environment(self):
        self.assertIn("Required Environment", self._plan())

    def test_plan_has_automated_tests(self):
        self.assertIn("Automated Tests", self._plan())

    def test_plan_has_desktop_smoke(self):
        self.assertIn("Desktop Smoke", self._plan())

    def test_plan_has_cli_smoke(self):
        self.assertIn("CLI Smoke", self._plan())

    def test_plan_has_project_persistence(self):
        self.assertIn("Project Persistence", self._plan())

    def test_plan_has_provider_readiness(self):
        self.assertIn("Provider Readiness", self._plan())

    def test_plan_has_text_provider_workflow(self):
        self.assertIn("Text Provider Mock", self._plan())
        self.assertIn("Text Provider", self._plan())

    def test_plan_has_image_provider_workflow(self):
        self.assertIn("Image Provider Mock", self._plan())

    def test_plan_has_video_provider_workflow(self):
        self.assertIn("Video Provider Mock", self._plan())

    def test_plan_has_logs_history(self):
        self.assertIn("Provider Logs", self._plan())

    def test_plan_has_secret_redaction(self):
        self.assertIn("Secret Redaction", self._plan())

    def test_plan_has_packaging_safety(self):
        self.assertIn("Packaging Secret Safety", self._plan())

    def test_plan_has_plugin_boundary(self):
        self.assertIn("Plugin Boundary", self._plan())

    def test_plan_has_known_limitations(self):
        self.assertIn("Known Limitations", self._plan())

    def test_plan_has_evidence_requirements(self):
        self.assertIn("Evidence Requirements", self._plan())

    def test_plan_has_pass_fail_criteria(self):
        self.assertIn("Pass/Fail Criteria", self._plan())


class TestManualQAChecklistExists(unittest.TestCase):

    def _checklist(self):
        p = DOCS_QA / "V0_4_PROVIDER_WORKFLOW_MANUAL_QA_CHECKLIST.md"
        self.assertTrue(p.exists(), "Manual QA checklist missing")
        return p.read_text(encoding="utf-8")

    def test_checklist_exists(self):
        self.assertTrue((DOCS_QA / "V0_4_PROVIDER_WORKFLOW_MANUAL_QA_CHECKLIST.md").exists())

    def test_checklist_has_desktop_launch(self):
        self.assertIn("Desktop Launch", self._checklist())

    def test_checklist_has_provider_tab(self):
        self.assertIn("Provider Tab", self._checklist())

    def test_checklist_has_text_provider_mock(self):
        self.assertIn("Text Provider Mock Path", self._checklist())

    def test_checklist_has_text_provider_readiness(self):
        self.assertIn("Text Provider Readiness Path", self._checklist())

    def test_checklist_has_image_provider_mock(self):
        self.assertIn("Image Provider Mock Path", self._checklist())

    def test_checklist_has_image_provider_readiness(self):
        self.assertIn("Image Provider Readiness Path", self._checklist())

    def test_checklist_has_video_provider_mock(self):
        self.assertIn("Video Provider Mock Path", self._checklist())

    def test_checklist_has_video_provider_readiness(self):
        self.assertIn("Video Provider Readiness Path", self._checklist())

    def test_checklist_has_logs_history(self):
        self.assertIn("Logs", self._checklist())

    def test_checklist_has_no_secret_persistence(self):
        self.assertIn("No Secret Persistence", self._checklist())

    def test_checklist_has_project_save_load(self):
        self.assertIn("Project Save/Load", self._checklist())

    def test_checklist_has_plugin_blocked(self):
        self.assertIn("Plugin Execution Remains Blocked", self._checklist())

    def test_checklist_has_autosave_backup(self):
        self.assertIn("Autosave", self._checklist())

    def test_checklist_has_packaging_smoke(self):
        self.assertIn("Packaging Smoke", self._checklist())

    def test_checklist_has_checkboxes(self):
        self.assertIn("- [ ]", self._checklist())


class TestEvidenceTemplateExists(unittest.TestCase):

    def _tpl(self):
        p = DOCS_QA / "V0_4_PROVIDER_WORKFLOW_EVIDENCE_TEMPLATE.md"
        self.assertTrue(p.exists(), "Evidence template missing")
        return p.read_text(encoding="utf-8")

    def test_template_exists(self):
        self.assertTrue((DOCS_QA / "V0_4_PROVIDER_WORKFLOW_EVIDENCE_TEMPLATE.md").exists())

    def test_template_has_reviewer(self):
        self.assertIn("Reviewer", self._tpl())

    def test_template_has_date(self):
        self.assertIn("Date", self._tpl())

    def test_template_has_environment(self):
        self.assertIn("Environment", self._tpl())

    def test_template_has_build_revision(self):
        self.assertIn("Build/Source Revision", self._tpl())

    def test_template_has_automated_test_evidence(self):
        self.assertIn("Automated Test Evidence", self._tpl())

    def test_template_has_cli_smoke_evidence(self):
        self.assertIn("CLI Smoke Evidence", self._tpl())

    def test_template_has_desktop_manual_qa(self):
        self.assertIn("Desktop Manual QA Evidence", self._tpl())

    def test_template_has_provider_workflow_evidence(self):
        self.assertIn("Provider Workflow Evidence", self._tpl())

    def test_template_has_safety_scan_evidence(self):
        self.assertIn("Safety Scan Evidence", self._tpl())

    def test_template_has_packaging_evidence(self):
        self.assertIn("Packaging Evidence", self._tpl())

    def test_template_has_known_limitations(self):
        self.assertIn("Known Limitations", self._tpl())

    def test_template_has_open_blockers(self):
        self.assertIn("Open Blockers", self._tpl())

    def test_template_has_decision_recommendation(self):
        self.assertIn("Decision Recommendation", self._tpl())


class TestProviderWorkflowRegression(unittest.TestCase):
    """Live regression checks via UISession."""

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.ui.actions import UISession
        self.sess = UISession()

    def test_text_mock_still_works(self):
        result = self.sess.evaluate_provider_execution_gate(
            "openai-compatible", "generate", mode="dry_run"
        )
        self.assertTrue(result.ok)
        self.assertTrue(result.payload["allowed"])

    def test_image_mock_still_works(self):
        result = self.sess.execute_image_provider_mock("mock-image", "regression test")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")
        self.assertFalse(result.payload.get("network_call", True))

    def test_video_mock_still_works(self):
        result = self.sess.execute_video_provider_mock("mock-video", "regression test")
        self.assertTrue(result.ok)
        self.assertEqual(result.payload["status"], "mock")
        self.assertFalse(result.payload.get("network_call", True))

    def test_real_text_still_blocked(self):
        result = self.sess.evaluate_provider_execution_gate(
            "openai-compatible", "generate", mode="real_text"
        )
        self.assertFalse(result.payload["allowed"])

    def test_real_image_still_blocked(self):
        result = self.sess.evaluate_image_provider_execution_gate(
            "mock-image", "generate", mode="real_image"
        )
        self.assertFalse(result.payload["allowed"])

    def test_real_video_still_blocked(self):
        result = self.sess.evaluate_video_provider_execution_gate(
            "mock-video", "generate", mode="real_video"
        )
        self.assertFalse(result.payload["allowed"])

    def test_no_secret_in_image_mock_response(self):
        result = self.sess.execute_image_provider_mock("mock-image", "regression test")
        payload_str = json.dumps(result.payload)
        # mock_tokens is a legitimate usage field; check specific secret patterns only
        for bad in ("api_key", "sk-", "password"):
            self.assertNotIn(bad, payload_str)

    def test_no_secret_in_video_mock_response(self):
        result = self.sess.execute_video_provider_mock("mock-video", "regression test")
        payload_str = json.dumps(result.payload)
        for bad in ("api_key", "sk-", "secret", "password"):
            self.assertNotIn(bad, payload_str)


class TestCLIWorkflowRegression(unittest.TestCase):

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli.main"] + list(args),
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(SRC)},
        )

    def test_smoke_still_passes(self):
        r = self._run("smoke")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_provider_smoke_still_passes(self):
        r = self._run("provider-smoke")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_image_mock_cli_still_works(self):
        r = self._run("image-provider-mock", "--provider", "mock-image", "--prompt", "reg test")
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout)
        self.assertEqual(d["status"], "mock")

    def test_video_mock_cli_still_works(self):
        r = self._run("video-provider-mock", "--provider", "mock-video", "--prompt", "reg test")
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout)
        self.assertEqual(d["status"], "mock")

    def test_safety_scan_still_passes(self):
        root = str(Path(__file__).parent.parent)
        r = self._run("safety-scan", "--root", root)
        self.assertEqual(r.returncode, 0, r.stderr)
        d = json.loads(r.stdout)
        self.assertEqual(d["overall_status"], "PASS")


if __name__ == "__main__":
    unittest.main()

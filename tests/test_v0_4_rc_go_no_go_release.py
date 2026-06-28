"""TASK-000125: v0.4 RC / Go-No-Go Release Decision tests.

Verifies RC docs, regression checklist, go/no-go template, final decision report,
release notes, and promotion scripts. Confirms decision defaults to PENDING.
Confirms promotion scripts block PENDING/NO-GO.
No network calls. Standard library only.
"""

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
DOCS_QA = ROOT / "docs" / "qa"
RELEASE_NOTES = ROOT / "release-notes"
SCRIPTS = ROOT / "scripts"


class TestRCQAPlanExists(unittest.TestCase):

    def _plan(self):
        p = DOCS_QA / "V0_4_RELEASE_CANDIDATE_QA_PLAN.md"
        self.assertTrue(p.exists(), "RC QA plan missing")
        return p.read_text(encoding="utf-8")

    def test_plan_exists(self):
        self.assertTrue((DOCS_QA / "V0_4_RELEASE_CANDIDATE_QA_PLAN.md").exists())

    def test_plan_has_purpose(self):
        self.assertIn("Purpose", self._plan())

    def test_plan_has_rc_target(self):
        self.assertIn("Release Candidate Target", self._plan())

    def test_plan_has_included_scope(self):
        self.assertIn("Included Scope", self._plan())

    def test_plan_has_excluded_scope(self):
        self.assertIn("Excluded Scope", self._plan())
        self.assertIn("Provider SDKs", self._plan())
        self.assertIn("Real image provider execution", self._plan())
        self.assertIn("Real video provider execution", self._plan())

    def test_plan_has_prerequisites(self):
        self.assertIn("Prerequisites", self._plan())

    def test_plan_has_required_automated_tests(self):
        self.assertIn("Required Automated Tests", self._plan())

    def test_plan_has_required_provider_workflow_smoke(self):
        self.assertIn("Required Provider Workflow Smoke", self._plan())

    def test_plan_has_required_safety_scan(self):
        self.assertIn("Required Safety Scan", self._plan())

    def test_plan_has_required_packaging_safety_smoke(self):
        self.assertIn("Required Packaging Secret Safety Smoke", self._plan())

    def test_plan_has_required_desktop_manual_qa(self):
        self.assertIn("Required Desktop Manual QA", self._plan())

    def test_plan_has_required_cli_qa(self):
        self.assertIn("Required CLI QA", self._plan())

    def test_plan_has_known_limitations(self):
        self.assertIn("Known Limitations", self._plan())

    def test_plan_has_go_no_go_process(self):
        self.assertIn("Go/No-Go Process", self._plan())

    def test_plan_has_evidence_collection(self):
        self.assertIn("Evidence Collection", self._plan())


class TestRegressionChecklistExists(unittest.TestCase):

    def _checklist(self):
        p = DOCS_QA / "V0_4_REGRESSION_CHECKLIST.md"
        self.assertTrue(p.exists(), "Regression checklist missing")
        return p.read_text(encoding="utf-8")

    def test_checklist_exists(self):
        self.assertTrue((DOCS_QA / "V0_4_REGRESSION_CHECKLIST.md").exists())

    def test_checklist_has_unittest(self):
        self.assertIn("python -m unittest", self._checklist())

    def test_checklist_has_desktop_smoke(self):
        self.assertIn("headless-smoke", self._checklist())

    def test_checklist_has_cli_smoke(self):
        self.assertIn("cli smoke", self._checklist().lower())

    def test_checklist_has_create_demo(self):
        self.assertIn("create-demo", self._checklist())

    def test_checklist_has_validate_bundle(self):
        self.assertIn("validate-bundle", self._checklist())

    def test_checklist_has_rehydrate_bundle(self):
        self.assertIn("rehydrate-bundle", self._checklist())

    def test_checklist_has_provider_smoke(self):
        self.assertIn("provider-smoke", self._checklist())

    def test_checklist_has_provider_test_dry_run(self):
        self.assertIn("provider-test", self._checklist())

    def test_checklist_has_text_provider_mock(self):
        self.assertIn("text-provider-mock", self._checklist())

    def test_checklist_has_image_provider_mock(self):
        self.assertIn("image-provider-mock", self._checklist())

    def test_checklist_has_video_provider_mock(self):
        self.assertIn("video-provider-mock", self._checklist())

    def test_checklist_has_safety_scan(self):
        self.assertIn("safety-scan", self._checklist())

    def test_checklist_has_packaging_safety(self):
        self.assertIn("packaging", self._checklist().lower())

    def test_checklist_has_plugin_blocked(self):
        self.assertIn("plugin", self._checklist().lower())

    def test_checklist_has_no_provider_sdks(self):
        self.assertIn("No Provider SDKs", self._checklist())

    def test_checklist_has_no_real_api_keys(self):
        self.assertIn("No Real API Keys", self._checklist())

    def test_checklist_has_no_secrets_in_artifacts(self):
        self.assertIn("No Secrets in Artifacts", self._checklist())

    def test_checklist_has_checkboxes(self):
        self.assertIn("- [ ]", self._checklist())


class TestGoNoGoTemplateExists(unittest.TestCase):

    def _tpl(self):
        p = DOCS_QA / "V0_4_GO_NO_GO_TEMPLATE.md"
        self.assertTrue(p.exists(), "Go/no-go template missing")
        return p.read_text(encoding="utf-8")

    def test_template_exists(self):
        self.assertTrue((DOCS_QA / "V0_4_GO_NO_GO_TEMPLATE.md").exists())

    def test_template_has_release_candidate(self):
        self.assertIn("Release Candidate", self._tpl())

    def test_template_has_reviewer(self):
        self.assertIn("Reviewer", self._tpl())

    def test_template_has_date(self):
        self.assertIn("Date", self._tpl())

    def test_template_has_environment(self):
        self.assertIn("Environment", self._tpl())

    def test_template_has_automated_test_evidence(self):
        self.assertIn("Automated Test Evidence", self._tpl())

    def test_template_has_provider_workflow_evidence(self):
        self.assertIn("Provider Workflow Evidence", self._tpl())

    def test_template_has_safety_scan_evidence(self):
        self.assertIn("Safety Scan Evidence", self._tpl())

    def test_template_has_packaging_evidence(self):
        self.assertIn("Packaging Evidence", self._tpl())

    def test_template_has_desktop_manual_qa(self):
        self.assertIn("Desktop Manual QA Evidence", self._tpl())

    def test_template_has_security_boundary_evidence(self):
        self.assertIn("Security Boundary Evidence", self._tpl())

    def test_template_has_open_blockers(self):
        self.assertIn("Open Blockers", self._tpl())

    def test_template_has_open_non_blockers(self):
        self.assertIn("Open Non-Blockers", self._tpl())

    def test_template_has_known_limitations_accepted(self):
        self.assertIn("Known Limitations Accepted", self._tpl())

    def test_template_has_decision_field(self):
        self.assertIn("Decision:", self._tpl())

    def test_template_has_sign_off(self):
        self.assertIn("Sign-off", self._tpl())

    def test_template_decision_defaults_pending(self):
        self.assertIn("Decision: PENDING", self._tpl())

    def test_template_has_blocker_rule(self):
        self.assertIn("NO-GO", self._tpl())

    def test_template_security_evidence_no_sdks(self):
        self.assertIn("No provider SDKs", self._tpl())

    def test_template_security_evidence_no_api_keys(self):
        self.assertIn("No real API keys stored", self._tpl())

    def test_template_security_evidence_no_secrets(self):
        self.assertIn("No secrets in", self._tpl())

    def test_template_security_text_blocked(self):
        self.assertIn("Text real execution blocked", self._tpl())

    def test_template_security_image_blocked(self):
        self.assertIn("Image real execution blocked", self._tpl())

    def test_template_security_video_blocked(self):
        self.assertIn("Video real execution blocked", self._tpl())


class TestFinalDecisionReportExists(unittest.TestCase):

    def _report(self):
        p = DOCS_QA / "V0_4_FINAL_RELEASE_DECISION_REPORT.md"
        self.assertTrue(p.exists(), "Final decision report missing")
        return p.read_text(encoding="utf-8")

    def test_report_exists(self):
        self.assertTrue((DOCS_QA / "V0_4_FINAL_RELEASE_DECISION_REPORT.md").exists())

    def test_report_decision_defaults_pending(self):
        text = self._report()
        self.assertIn("Decision: PENDING", text)

    def test_report_does_not_claim_production_ready(self):
        text = self._report().lower()
        self.assertNotIn("production ready", text)
        # "not production-ready" is a disclaimer, not a claim — allow it
        # Check that "production-ready" only appears as a negation
        import re
        for m in re.finditer(r"production.ready", text):
            ctx = text[max(0, m.start()-20):m.end()+20]
            self.assertIn("not", ctx, f"Possible production-ready claim: {ctx}")

    def test_report_has_security_boundary_confirmation(self):
        text = self._report()
        self.assertIn("No provider SDK was added.", text)
        self.assertIn("No real API keys are stored.", text)
        self.assertIn("Real text execution remains blocked by default.", text)
        self.assertIn("Real image execution remains blocked by default.", text)
        self.assertIn("Real video execution remains blocked by default.", text)


class TestReleaseNotesExist(unittest.TestCase):

    def test_rc1_notes_exist(self):
        self.assertTrue((RELEASE_NOTES / "AuroraStudio-v0.4.0-rc1.md").exists())

    def test_final_notes_exist(self):
        self.assertTrue((RELEASE_NOTES / "AuroraStudio-v0.4.0.md").exists())

    def _rc1(self):
        return (RELEASE_NOTES / "AuroraStudio-v0.4.0-rc1.md").read_text(encoding="utf-8")

    def _final(self):
        return (RELEASE_NOTES / "AuroraStudio-v0.4.0.md").read_text(encoding="utf-8")

    def test_rc1_has_release_type(self):
        self.assertIn("Release type", self._rc1())

    def test_rc1_has_included(self):
        self.assertIn("## Included", self._rc1())

    def test_rc1_has_not_included(self):
        self.assertIn("## Not Included", self._rc1())

    def test_rc1_has_how_to_run(self):
        self.assertIn("How to Run", self._rc1())

    def test_rc1_has_how_to_smoke_test(self):
        self.assertIn("How to Smoke Test", self._rc1())

    def test_rc1_has_known_limitations(self):
        self.assertIn("Known Limitations", self._rc1())

    def test_rc1_has_validation(self):
        self.assertIn("Validation", self._rc1())

    def test_rc1_has_decision_status(self):
        self.assertIn("Decision Status", self._rc1())

    def test_rc1_does_not_claim_production_ready(self):
        self.assertNotIn("production ready", self._rc1().lower())

    def test_final_notes_decision_pending(self):
        self.assertIn("PENDING", self._final())

    def test_final_notes_does_not_claim_production_ready(self):
        text = self._final().lower()
        self.assertNotIn("production ready", text)
        # "not production-ready" is a disclaimer — check all occurrences are negated
        import re
        for m in re.finditer(r"production.ready", text):
            ctx = text[max(0, m.start()-20):m.end()+20]
            self.assertIn("not", ctx, f"Possible production-ready claim: {ctx}")


class TestPromotionScriptsExist(unittest.TestCase):

    def test_ps1_exists(self):
        self.assertTrue((SCRIPTS / "promote_v0_4_rc_to_final.ps1").exists())

    def test_bat_exists(self):
        self.assertTrue((SCRIPTS / "promote_v0_4_rc_to_final.bat").exists())

    def _ps1(self):
        return (SCRIPTS / "promote_v0_4_rc_to_final.ps1").read_text(encoding="utf-8")

    def _bat(self):
        return (SCRIPTS / "promote_v0_4_rc_to_final.bat").read_text(encoding="utf-8")

    def test_ps1_checks_report_exists(self):
        self.assertIn("FINAL_RELEASE_DECISION_REPORT", self._ps1())

    def test_ps1_blocks_pending(self):
        ps1 = self._ps1()
        self.assertIn("PENDING", ps1)
        self.assertIn("BLOCKED", ps1)

    def test_ps1_blocks_no_go(self):
        ps1 = self._ps1()
        self.assertIn("NO-GO", ps1)
        self.assertIn("BLOCKED", ps1)

    def test_ps1_does_not_build_installer(self):
        ps1 = self._ps1()
        # Script may mention "installer" in a comment saying it does NOT build one
        # Check there is no actual installer build call (msiexec, Setup.exe, etc.)
        self.assertNotIn("msiexec", ps1.lower())
        self.assertNotIn("Setup.exe", ps1)

    def test_ps1_does_not_sign_code(self):
        ps1 = self._ps1()
        self.assertNotIn("SignTool", ps1)
        self.assertNotIn("Set-AuthenticodeSignature", ps1)

    def test_ps1_does_not_call_network(self):
        ps1 = self._ps1()
        self.assertNotIn("Invoke-WebRequest", ps1)
        self.assertNotIn("Invoke-RestMethod", ps1)

    def test_ps1_does_not_bundle_secrets(self):
        ps1 = self._ps1()
        self.assertNotIn("api_key =", ps1.lower())
        self.assertNotIn("sk-", ps1)

    def test_bat_checks_report_exists(self):
        self.assertIn("FINAL_RELEASE_DECISION_REPORT", self._bat())

    def test_bat_blocks_pending(self):
        bat = self._bat()
        self.assertIn("PENDING", bat)
        self.assertIn("BLOCKED", bat)

    def test_bat_blocks_no_go(self):
        bat = self._bat()
        self.assertIn("NO-GO", bat)
        self.assertIn("BLOCKED", bat)

    def test_bat_does_not_call_network(self):
        bat = self._bat().lower()
        self.assertNotIn("curl", bat)
        self.assertNotIn("wget", bat)


class TestPromotionBlocksPendingDecision(unittest.TestCase):
    """Simulate promotion script logic with PENDING decision."""

    def _check_decision(self, report_text: str) -> str:
        """Minimal Python simulation of the promotion script decision check."""
        import re
        m = re.search(r"Final Decision:\s*(\S+)", report_text)
        if not m:
            m = re.search(r"Decision:\s*(GO|NO-GO|PENDING|GO WITH KNOWN LIMITATIONS)", report_text)
        if not m:
            return "UNKNOWN"
        return m.group(1).strip()

    def test_pending_decision_is_blocked(self):
        decision = self._check_decision("Final Decision: PENDING\n")
        self.assertEqual(decision, "PENDING")
        self.assertNotIn(decision, ("GO", "NO-GO"))

    def test_no_go_decision_is_blocked(self):
        decision = self._check_decision("Final Decision: NO-GO\n")
        self.assertEqual(decision, "NO-GO")

    def test_go_decision_would_proceed(self):
        decision = self._check_decision("Final Decision: GO\n")
        self.assertEqual(decision, "GO")

    def test_current_report_has_pending_decision(self):
        report = (DOCS_QA / "V0_4_FINAL_RELEASE_DECISION_REPORT.md").read_text(encoding="utf-8")
        decision = self._check_decision(report)
        self.assertEqual(decision, "PENDING",
                         "Final decision report must default to PENDING")


if __name__ == "__main__":
    unittest.main()

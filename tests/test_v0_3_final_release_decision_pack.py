"""Tests for TASK-000100: v0.3 Final Release Decision Pack."""

import os
import unittest

PROCESS_DOC = "docs/qa/V0_3_FINAL_RELEASE_DECISION_PROCESS.md"
REPORT_DOC = "docs/qa/V0_3_FINAL_RELEASE_DECISION_REPORT.md"
EVIDENCE_DOC = "docs/qa/V0_3_FINAL_RELEASE_EVIDENCE_CHECKLIST.md"
RELEASE_NOTES = "release-notes/AuroraStudio-v0.3.0.md"
PROMOTE_PS1 = "scripts/promote_v0_3_rc_to_final.ps1"
PROMOTE_BAT = "scripts/promote_v0_3_rc_to_final.bat"
SMOKE_PS1 = "scripts/smoke_v0_3_final_portable_zip.ps1"
SMOKE_BAT = "scripts/smoke_v0_3_final_portable_zip.bat"


def _c(path):
    with open(path) as f:
        return f.read()


class TestDecisionDocsExist(unittest.TestCase):
    def test_process_doc_exists(self):
        self.assertTrue(os.path.exists(PROCESS_DOC))

    def test_report_doc_exists(self):
        self.assertTrue(os.path.exists(REPORT_DOC))

    def test_evidence_checklist_exists(self):
        self.assertTrue(os.path.exists(EVIDENCE_DOC))

    def test_final_release_notes_exist(self):
        self.assertTrue(os.path.exists(RELEASE_NOTES))


class TestPromotionScriptsExist(unittest.TestCase):
    def test_promote_ps1_exists(self):
        self.assertTrue(os.path.exists(PROMOTE_PS1))

    def test_promote_bat_exists(self):
        self.assertTrue(os.path.exists(PROMOTE_BAT))

    def test_final_smoke_ps1_exists(self):
        self.assertTrue(os.path.exists(SMOKE_PS1))

    def test_final_smoke_bat_exists(self):
        self.assertTrue(os.path.exists(SMOKE_BAT))


class TestDecisionReportDefaults(unittest.TestCase):
    def test_report_defaults_to_pending(self):
        self.assertIn("PENDING", _c(REPORT_DOC))

    def test_report_does_not_say_go_without_pending(self):
        c = _c(REPORT_DOC)
        # Must contain PENDING as the explicit decision status
        self.assertIn("**PENDING**", c)


class TestProcessDocContent(unittest.TestCase):
    def test_states_no_automatic_approval(self):
        c = _c(PROCESS_DOC).lower()
        self.assertIn("cannot be approved automatically", c)

    def test_states_default_pending(self):
        self.assertIn("PENDING", _c(PROCESS_DOC))

    def test_states_blockers_force_no_go(self):
        c = _c(PROCESS_DOC)
        self.assertIn("NO-GO", c)
        self.assertIn("blocker", c.lower())

    def test_states_go_requires_evidence(self):
        c = _c(PROCESS_DOC).lower()
        self.assertIn("evidence", c)

    def test_lists_allowed_decisions(self):
        c = _c(PROCESS_DOC)
        self.assertIn("GO", c)
        self.assertIn("NO-GO", c)
        self.assertIn("PENDING", c)

    def test_has_promotion_process(self):
        self.assertIn("Promotion Process", _c(PROCESS_DOC))

    def test_has_rollback_rule(self):
        self.assertIn("Rollback Rule", _c(PROCESS_DOC))

    def test_has_no_automatic_approval_rule(self):
        self.assertIn("No Automatic Approval Rule", _c(PROCESS_DOC))


class TestPromotionScriptContent(unittest.TestCase):
    def test_promote_script_blocks_pending(self):
        c = _c(PROMOTE_PS1)
        self.assertIn("PENDING", c)
        self.assertIn("BLOCKED", c)

    def test_promote_script_blocks_no_go(self):
        c = _c(PROMOTE_PS1)
        self.assertIn("NO-GO", c)

    def test_promote_script_requires_go(self):
        c = _c(PROMOTE_PS1).lower()
        self.assertIn("go", c)

    def test_promote_script_requires_decision_report(self):
        self.assertIn("DecisionReport", _c(PROMOTE_PS1))

    def test_smoke_script_validates_sha256(self):
        self.assertIn("SHA256", _c(SMOKE_PS1))

    def test_smoke_script_checks_run_bat(self):
        self.assertIn("run_desktop.bat", _c(SMOKE_PS1))


class TestFinalReleaseNotes(unittest.TestCase):
    def test_decision_status_pending(self):
        self.assertIn("PENDING", _c(RELEASE_NOTES))

    def test_does_not_claim_production_readiness(self):
        self.assertNotIn("production ready", _c(RELEASE_NOTES).lower())

    def test_not_included_provider_sdk(self):
        self.assertIn("Provider SDKs", _c(RELEASE_NOTES))

    def test_not_included_plugin_execution(self):
        self.assertIn("Plugin execution", _c(RELEASE_NOTES))

    def test_not_included_database(self):
        self.assertIn("Database", _c(RELEASE_NOTES))


if __name__ == "__main__":
    unittest.main()

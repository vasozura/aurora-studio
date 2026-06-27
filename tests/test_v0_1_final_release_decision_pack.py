"""
tests/test_v0_1_final_release_decision_pack.py

TASK-000050: v0.1 Final Release Decision Pack
Tests for decision process, decision report (PENDING), evidence checklist,
final release notes, promotion scripts, and final ZIP smoke scripts.

Rules:
- Standard-library unittest only
- No display required
- No PyInstaller required
- No built EXE required
- No ZIP created or promoted by default
- No Windows required
"""

import os
import pathlib
import unittest

_REPO = pathlib.Path(__file__).parent.parent
_QA_DIR = _REPO / "docs" / "qa"
_SCRIPTS = _REPO / "scripts"

_DECISION_PROCESS   = _QA_DIR / "V0_1_FINAL_RELEASE_DECISION_PROCESS.md"
_DECISION_REPORT    = _QA_DIR / "V0_1_FINAL_RELEASE_DECISION_REPORT.md"
_EVIDENCE_CHECKLIST = _QA_DIR / "V0_1_FINAL_RELEASE_EVIDENCE_CHECKLIST.md"
_FINAL_NOTES        = _REPO / "release-notes" / "AuroraStudio-v0.1.0.md"

_PROMOTE_PS1  = _SCRIPTS / "promote_rc_to_final.ps1"
_PROMOTE_BAT  = _SCRIPTS / "promote_rc_to_final.bat"
_SMOKE_PS1    = _SCRIPTS / "smoke_final_portable_zip.ps1"
_SMOKE_BAT    = _SCRIPTS / "smoke_final_portable_zip.bat"

_GITIGNORE = _REPO / ".gitignore"


def _read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Decision Process
# ---------------------------------------------------------------------------

class TestDecisionProcessExists(unittest.TestCase):

    def test_decision_process_exists(self):
        self.assertTrue(_DECISION_PROCESS.is_file(), f"Missing: {_DECISION_PROCESS}")


class TestDecisionProcessContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_DECISION_PROCESS)
        self.lower = self.text.lower()

    def test_contains_go_option(self):
        self.assertIn("GO", self.text)

    def test_contains_no_go_option(self):
        self.assertIn("NO-GO", self.text)

    def test_contains_go_with_known_limitations_option(self):
        self.assertIn("GO WITH KNOWN LIMITATIONS", self.text)

    def test_contains_blocker_stop_rule(self):
        self.assertIn("blocker", self.lower)
        self.assertIn("no-go", self.lower)

    def test_no_go_forbids_promotion(self):
        self.assertIn("no-go", self.lower)
        self.assertIn("promotion", self.lower)

    def test_states_no_installer(self):
        self.assertIn("no installer", self.lower)

    def test_states_no_msix(self):
        self.assertIn("no msix", self.lower)

    def test_states_no_code_signing(self):
        self.assertIn("no code sign", self.lower)

    def test_states_no_database(self):
        self.assertIn("no database", self.lower)

    def test_has_required_evidence_section(self):
        self.assertIn("Required Evidence", self.text)

    def test_has_promotion_rules_section(self):
        self.assertIn("Promotion Rules", self.text)

    def test_has_rollback_rules_section(self):
        self.assertIn("Rollback", self.text)

    def test_has_final_artifact_naming(self):
        self.assertIn("Final Artifact Naming", self.text)

    def test_references_qa_plan(self):
        self.assertIn("V0_1_RELEASE_CANDIDATE_QA_PLAN.md", self.text)

    def test_references_rc_zip(self):
        self.assertIn("AuroraStudio-v0.1.0-rc1-windows-portable.zip", self.text)


# ---------------------------------------------------------------------------
# Decision Report — PENDING
# ---------------------------------------------------------------------------

class TestDecisionReportExists(unittest.TestCase):

    def test_decision_report_exists(self):
        self.assertTrue(_DECISION_REPORT.is_file(), f"Missing: {_DECISION_REPORT}")


class TestDecisionReportContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_DECISION_REPORT)
        self.lower = self.text.lower()

    def test_decision_starts_as_pending(self):
        self.assertIn("Decision: PENDING", self.text)

    def test_decision_report_does_not_claim_tests_passed(self):
        # must not contain phrases like "tests passed" as a factual claim
        self.assertNotIn("tests passed", self.lower)

    def test_decision_report_does_not_claim_manual_qa_executed(self):
        self.assertNotIn("manual qa executed", self.lower)

    def test_decision_report_does_not_claim_final_promotion_occurred(self):
        self.assertNotIn("promotion complete", self.lower)
        self.assertNotIn("promotion occurred", self.lower)

    def test_contains_known_limitations_no_installer(self):
        self.assertIn("no installer", self.lower)

    def test_contains_known_limitations_no_msix(self):
        self.assertIn("no msix", self.lower)

    def test_contains_known_limitations_no_code_signing(self):
        self.assertIn("no code signing", self.lower)

    def test_contains_known_limitations_no_database(self):
        self.assertIn("no database", self.lower)

    def test_contains_known_limitations_no_provider(self):
        self.assertIn("no provider", self.lower)

    def test_contains_known_limitations_no_plugin_execution(self):
        self.assertIn("no plugin execution", self.lower)

    def test_contains_known_limitations_not_production_ready(self):
        self.assertIn("not production ready", self.lower)

    def test_promotion_rule_present(self):
        self.assertIn("allowed only after Decision is GO", self.text)

    def test_contains_open_blockers_section(self):
        self.assertIn("Open Blockers", self.text)

    def test_contains_sign_off_section(self):
        self.assertIn("Sign-Off", self.text)

    def test_contains_automated_test_evidence_section(self):
        self.assertIn("Automated Test Evidence", self.text)

    def test_contains_headless_smoke_evidence_section(self):
        self.assertIn("Headless Smoke Evidence", self.text)

    def test_contains_promotion_status_section(self):
        self.assertIn("Promotion Status", self.text)


# ---------------------------------------------------------------------------
# Evidence Checklist
# ---------------------------------------------------------------------------

class TestEvidenceChecklistExists(unittest.TestCase):

    def test_evidence_checklist_exists(self):
        self.assertTrue(_EVIDENCE_CHECKLIST.is_file(), f"Missing: {_EVIDENCE_CHECKLIST}")


class TestEvidenceChecklistContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_EVIDENCE_CHECKLIST)
        self.lower = self.text.lower()

    def test_contains_python_unittest_command(self):
        self.assertIn("python -m unittest", self.text)

    def test_contains_headless_smoke_command(self):
        self.assertIn("--headless-smoke", self.text)

    def test_contains_cli_smoke_command(self):
        self.assertIn("python -m aurora_studio.cli smoke", self.text)

    def test_contains_promote_bat_command(self):
        self.assertIn("promote_rc_to_final.bat", self.text)

    def test_contains_smoke_final_bat_command(self):
        self.assertIn("smoke_final_portable_zip.bat", self.text)

    def test_contains_ps1_equivalents(self):
        self.assertIn("promote_rc_to_final.ps1", self.text)
        self.assertIn("smoke_final_portable_zip.ps1", self.text)

    def test_requires_decision_before_promotion(self):
        self.assertIn("GO or GO WITH KNOWN LIMITATIONS", self.text)
        # must appear in context of promotion requirement
        combined = self.text
        self.assertIn("before final promotion", self.lower)

    def test_requires_no_open_blocker(self):
        self.assertIn("No open blocker", self.text)

    def test_contains_final_promotion_group(self):
        self.assertIn("Final Promotion", self.text)

    def test_contains_final_zip_smoke_group(self):
        self.assertIn("Final ZIP Smoke", self.text)

    def test_contains_checksum_group(self):
        self.assertIn("Checksum Verification", self.text)

    def test_uses_checkbox_format(self):
        self.assertIn("- [ ]", self.text)


# ---------------------------------------------------------------------------
# Final Release Notes
# ---------------------------------------------------------------------------

class TestFinalReleaseNotesExists(unittest.TestCase):

    def test_final_release_notes_exist(self):
        self.assertTrue(_FINAL_NOTES.is_file(), f"Missing: {_FINAL_NOTES}")


class TestFinalReleaseNotesContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_FINAL_NOTES)
        self.lower = self.text.lower()

    def test_states_validity_depends_on_decision(self):
        self.assertIn("GO or GO WITH KNOWN LIMITATIONS", self.text)
        self.assertIn("V0_1_FINAL_RELEASE_DECISION_REPORT.md", self.text)

    def test_states_no_installer(self):
        self.assertIn("no installer", self.lower)

    def test_states_no_msix(self):
        self.assertIn("no msix", self.lower)

    def test_states_no_code_signing(self):
        self.assertIn("no code signing", self.lower)

    def test_states_no_database(self):
        self.assertIn("no database", self.lower)

    def test_states_no_provider_integration(self):
        self.assertIn("no provider integration", self.lower)

    def test_states_no_plugin_execution(self):
        self.assertIn("no plugin execution", self.lower)

    def test_states_no_production_readiness(self):
        self.assertIn("no production readiness", self.lower)

    def test_lists_local_desktop_shell(self):
        self.assertIn("Local desktop shell", self.text)

    def test_lists_bundle_save_load(self):
        self.assertIn("bundle save", self.lower)

    def test_lists_cli_smoke_commands(self):
        self.assertIn("CLI smoke", self.text)

    def test_has_known_limitations_section(self):
        self.assertIn("Known Limitations", self.text)

    def test_has_final_artifact_section(self):
        self.assertIn("Final Artifact", self.text)

    def test_does_not_claim_production_ready(self):
        # "not production ready" is fine; must not claim it is production ready
        self.assertNotIn("is production ready", self.lower)
        self.assertNotIn("production-ready release", self.lower)


# ---------------------------------------------------------------------------
# Promotion Scripts
# ---------------------------------------------------------------------------

class TestPromotionScriptsExist(unittest.TestCase):

    def test_promote_ps1_exists(self):
        self.assertTrue(_PROMOTE_PS1.is_file(), f"Missing: {_PROMOTE_PS1}")

    def test_promote_bat_exists(self):
        self.assertTrue(_PROMOTE_BAT.is_file(), f"Missing: {_PROMOTE_BAT}")


class TestPromotionScriptContent(unittest.TestCase):

    def setUp(self):
        self.ps1 = _read(_PROMOTE_PS1)
        self.bat = _read(_PROMOTE_BAT)
        self.ps1_lower = self.ps1.lower()
        self.bat_lower = self.bat.lower()

    def test_ps1_checks_decision_report(self):
        self.assertIn("V0_1_FINAL_RELEASE_DECISION_REPORT.md", self.ps1)

    def test_ps1_blocks_pending(self):
        self.assertIn("PENDING", self.ps1)

    def test_ps1_blocks_no_go(self):
        self.assertIn("NO-GO", self.ps1)

    def test_ps1_verifies_rc_checksum(self):
        self.assertIn("SHA256", self.ps1)
        self.assertIn("checksum", self.ps1_lower)

    def test_ps1_uses_pscriptroot(self):
        self.assertIn("$PSScriptRoot", self.ps1)

    def test_ps1_references_releases_dir(self):
        self.assertIn("releases", self.ps1_lower)

    def test_ps1_references_final_zip_name(self):
        self.assertIn("AuroraStudio-v0.1.0-windows-portable.zip", self.ps1)

    def test_ps1_does_not_auto_install(self):
        executable = "\n".join(
            ln for ln in self.ps1.splitlines()
            if not ln.lstrip().startswith("#")
            and not ln.lstrip().lower().startswith("write-host")
        ).lower()
        self.assertNotIn("pip install", executable)

    def test_ps1_does_not_rebuild(self):
        self.assertNotIn("PyInstaller", self.ps1)
        self.assertNotIn("build_windows", self.ps1_lower)

    def test_bat_uses_dp0(self):
        self.assertIn("%~dp0", self.bat)

    def test_bat_delegates_to_ps1(self):
        self.assertIn("promote_rc_to_final.ps1", self.bat)

    def test_bat_does_not_auto_install(self):
        executable = "\n".join(
            ln for ln in self.bat.splitlines()
            if not ln.lstrip().startswith("::")
            and not ln.lstrip().lower().startswith("rem ")
            and not ln.lstrip().lower().startswith("echo")
        ).lower()
        self.assertNotIn("pip install", executable)


# ---------------------------------------------------------------------------
# Final ZIP Smoke Scripts
# ---------------------------------------------------------------------------

class TestFinalZipSmokeScriptsExist(unittest.TestCase):

    def test_smoke_ps1_exists(self):
        self.assertTrue(_SMOKE_PS1.is_file(), f"Missing: {_SMOKE_PS1}")

    def test_smoke_bat_exists(self):
        self.assertTrue(_SMOKE_BAT.is_file(), f"Missing: {_SMOKE_BAT}")


class TestFinalZipSmokeScriptContent(unittest.TestCase):

    def setUp(self):
        self.ps1 = _read(_SMOKE_PS1)
        self.bat = _read(_SMOKE_BAT)
        self.ps1_lower = self.ps1.lower()

    def test_ps1_verifies_final_zip(self):
        self.assertIn("AuroraStudio-v0.1.0-windows-portable.zip", self.ps1)

    def test_ps1_verifies_checksum(self):
        self.assertIn("SHA256", self.ps1)

    def test_ps1_extracts_to_controlled_path(self):
        self.assertIn("_smoke", self.ps1)
        self.assertIn("Expand-Archive", self.ps1)

    def test_ps1_uses_pscriptroot(self):
        self.assertIn("$PSScriptRoot", self.ps1)

    def test_ps1_cleans_up_smoke_folder(self):
        self.assertIn("Remove-Item", self.ps1)

    def test_ps1_references_releases_dir(self):
        self.assertIn("releases", self.ps1_lower)

    def test_bat_uses_dp0(self):
        self.assertIn("%~dp0", self.bat)

    def test_bat_delegates_to_ps1(self):
        self.assertIn("smoke_final_portable_zip.ps1", self.bat)


# ---------------------------------------------------------------------------
# .gitignore — releases/
# ---------------------------------------------------------------------------

class TestGitignoreReleasesIgnored(unittest.TestCase):

    def test_gitignore_ignores_releases(self):
        if not _GITIGNORE.is_file():
            self.skipTest(".gitignore not found")
        self.assertIn("releases/", _read(_GITIGNORE))


# ---------------------------------------------------------------------------
# Optional gated promotion test
# ---------------------------------------------------------------------------

class TestOptionalFinalPromotion(unittest.TestCase):

    @unittest.skipUnless(
        os.environ.get("AURORA_RUN_FINAL_PROMOTION") == "1",
        "Set AURORA_RUN_FINAL_PROMOTION=1 to run actual promotion"
    )
    def test_promote_rc_to_final_runs(self):
        import subprocess, sys
        result = subprocess.run(
            ["cmd", "/c", str(_SCRIPTS / "promote_rc_to_final.bat")],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()

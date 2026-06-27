"""
tests/test_v0_1_release_candidate_qa_pack.py

TASK-000049: v0.1 Release Candidate QA Pack
Tests for QA plan, regression checklist, packaging checklist,
go/no-go template, and release notes.

Rules:
- Standard-library unittest only
- No display required
- No PyInstaller required
- No built EXE required
- No ZIP created
- No Windows required
"""

import pathlib
import unittest

_REPO = pathlib.Path(__file__).parent.parent
_QA_DIR = _REPO / "docs" / "qa"

_QA_PLAN      = _QA_DIR / "V0_1_RELEASE_CANDIDATE_QA_PLAN.md"
_REGRESSION   = _QA_DIR / "V0_1_REGRESSION_CHECKLIST.md"
_PKG_CHECKLIST = _QA_DIR / "V0_1_PACKAGING_VALIDATION_CHECKLIST.md"
_GO_NO_GO     = _QA_DIR / "V0_1_GO_NO_GO_REPORT_TEMPLATE.md"
_RC_NOTES     = _REPO / "release-notes" / "AuroraStudio-v0.1.0-rc1.md"


def _read(p: pathlib.Path) -> str:
    return p.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# QA Plan
# ---------------------------------------------------------------------------

class TestQAPlanExists(unittest.TestCase):

    def test_qa_plan_exists(self):
        self.assertTrue(_QA_PLAN.is_file(), f"Missing: {_QA_PLAN}")


class TestQAPlanContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_QA_PLAN)
        self.lower = self.text.lower()

    def test_references_rc1_zip(self):
        self.assertIn("AuroraStudio-v0.1.0-rc1-windows-portable.zip", self.text)

    def test_lists_python_unittest_command(self):
        self.assertIn("python -m unittest", self.text)

    def test_lists_headless_smoke_command(self):
        self.assertIn("--headless-smoke", self.text)

    def test_lists_cli_smoke_command(self):
        self.assertIn("python -m aurora_studio.cli smoke", self.text)

    def test_lists_create_demo_command(self):
        self.assertIn("create-demo", self.text)

    def test_lists_validate_bundle_command(self):
        self.assertIn("validate-bundle", self.text)

    def test_lists_rehydrate_bundle_command(self):
        self.assertIn("rehydrate-bundle", self.text)

    def test_lists_build_bat_command(self):
        self.assertIn("build_windows_onefolder.bat", self.text)

    def test_lists_stage_bat_command(self):
        self.assertIn("stage_windows_portable.bat", self.text)

    def test_lists_smoke_portable_bat_command(self):
        self.assertIn("smoke_portable_folder.bat", self.text)

    def test_lists_create_zip_bat_command(self):
        self.assertIn("create_portable_zip.bat", self.text)

    def test_lists_smoke_zip_bat_command(self):
        self.assertIn("smoke_portable_zip.bat", self.text)

    def test_lists_ps1_equivalents(self):
        self.assertIn("build_windows_onefolder.ps1", self.text)
        self.assertIn("stage_windows_portable.ps1", self.text)

    def test_states_not_final_release(self):
        self.assertIn("not a final release", self.lower)

    def test_states_no_installer(self):
        self.assertIn("no installer", self.lower)

    def test_states_no_database(self):
        self.assertIn("no database", self.lower)

    def test_states_no_provider_integration(self):
        self.assertIn("no provider", self.lower)

    def test_states_no_plugin_execution(self):
        self.assertIn("no plugin", self.lower)

    def test_states_no_production_readiness(self):
        self.assertIn("no production readiness", self.lower)

    def test_has_pass_criteria_section(self):
        self.assertIn("Pass Criteria", self.text)

    def test_has_fail_criteria_section(self):
        self.assertIn("Fail Criteria", self.text)

    def test_has_go_no_go_procedure(self):
        self.assertIn("Go/No-Go", self.text)


# ---------------------------------------------------------------------------
# Regression Checklist
# ---------------------------------------------------------------------------

class TestRegressionChecklistExists(unittest.TestCase):

    def test_regression_checklist_exists(self):
        self.assertTrue(_REGRESSION.is_file(), f"Missing: {_REGRESSION}")


class TestRegressionChecklistContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_REGRESSION)
        self.lower = self.text.lower()

    def test_contains_repository_sanity_group(self):
        self.assertIn("Repository Sanity", self.text)

    def test_contains_unit_tests_group(self):
        self.assertIn("Unit Tests", self.text)

    def test_contains_core_managers_group(self):
        self.assertIn("Core Managers", self.text)

    def test_contains_application_service_group(self):
        self.assertIn("Application Service", self.text)

    def test_contains_persistence_group(self):
        self.assertIn("Persistence", self.text)

    def test_contains_rehydration_group(self):
        self.assertIn("Rehydration", self.text)

    def test_contains_cli_group(self):
        self.assertIn("## CLI", self.text)

    def test_contains_desktop_headless_smoke_group(self):
        self.assertIn("Desktop Headless Smoke", self.text)

    def test_contains_desktop_manual_smoke_group(self):
        self.assertIn("Desktop Manual Smoke", self.text)

    def test_contains_project_workflow_group(self):
        self.assertIn("Project Workflow", self.text)

    def test_contains_scene_workflow_group(self):
        self.assertIn("Scene Workflow", self.text)

    def test_contains_shot_workflow_group(self):
        self.assertIn("Shot Workflow", self.text)

    def test_contains_timeline_workflow_group(self):
        self.assertIn("Timeline Workflow", self.text)

    def test_contains_asset_workflow_group(self):
        self.assertIn("Asset Workflow", self.text)

    def test_contains_character_workflow_group(self):
        self.assertIn("Character Workflow", self.text)

    def test_contains_afl_smoke_workflow_group(self):
        self.assertIn("AFL Smoke", self.text)

    def test_contains_export_smoke_workflow_group(self):
        self.assertIn("Export Smoke", self.text)

    def test_contains_plugin_metadata_smoke_group(self):
        self.assertIn("Plugin Metadata Smoke", self.text)

    def test_contains_portable_zip_smoke_group(self):
        self.assertIn("Portable ZIP Smoke", self.text)

    def test_contains_known_limitations_group(self):
        self.assertIn("Known Limitations", self.text)

    def test_contains_desktop_cli_checks(self):
        self.assertIn("--headless-smoke", self.text)
        self.assertIn("python -m aurora_studio.cli smoke", self.text)

    def test_contains_plugin_no_execution_check(self):
        self.assertIn("does not execute plugin code", self.lower)

    def test_uses_checkbox_format(self):
        self.assertIn("- [ ]", self.text)


# ---------------------------------------------------------------------------
# Packaging Validation Checklist
# ---------------------------------------------------------------------------

class TestPackagingChecklistExists(unittest.TestCase):

    def test_packaging_checklist_exists(self):
        self.assertTrue(_PKG_CHECKLIST.is_file(), f"Missing: {_PKG_CHECKLIST}")


class TestPackagingChecklistContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_PKG_CHECKLIST)
        self.lower = self.text.lower()

    def test_contains_build_prerequisites_group(self):
        self.assertIn("Build Prerequisites", self.text)

    def test_contains_one_folder_build_group(self):
        self.assertIn("One-Folder Build", self.text)

    def test_contains_portable_folder_contents_group(self):
        self.assertIn("Portable Folder Contents", self.text)

    def test_contains_release_candidate_zip_group(self):
        self.assertIn("Release Candidate ZIP", self.text)

    def test_contains_checksum_group(self):
        self.assertIn("Checksum", self.text)

    def test_contains_zip_extraction_smoke_group(self):
        self.assertIn("ZIP Extraction Smoke", self.text)

    def test_contains_artifact_exclusions_group(self):
        self.assertIn("Artifact Exclusions", self.text)

    def test_contains_security_exclusions_group(self):
        self.assertIn("Security-Sensitive Exclusions", self.text)

    def test_checks_app_folder_in_portable(self):
        self.assertIn("app\\", self.text)

    def test_checks_run_desktop_bat_in_portable(self):
        self.assertIn("run_desktop.bat", self.text)

    def test_checks_smoke_desktop_bat_in_portable(self):
        self.assertIn("smoke_desktop.bat", self.text)

    def test_checks_readme_in_portable(self):
        self.assertIn("README.txt", self.text)

    def test_checks_notice_in_portable(self):
        self.assertIn("NOTICE.txt", self.text)

    def test_checks_data_logs_samples_tmp_in_portable(self):
        for folder in ("data", "logs", "samples", "tmp"):
            self.assertIn(folder, self.lower, f"Missing folder check: {folder}")

    def test_checks_no_git_in_zip(self):
        self.assertIn(".git", self.text)

    def test_checks_no_tests_in_zip(self):
        self.assertIn("tests", self.lower)

    def test_checks_no_release_candidates_nested(self):
        self.assertIn("release-candidates", self.lower)
        self.assertIn("nested", self.lower)

    def test_checks_no_provider_keys(self):
        self.assertIn("no provider", self.lower)

    def test_states_no_installer(self):
        self.assertIn("no installer", self.lower)

    def test_states_no_msix(self):
        self.assertIn("no msix", self.lower)

    def test_states_no_code_signing(self):
        self.assertIn("no code signing", self.lower)

    def test_states_no_provider_integration(self):
        self.assertIn("no provider integration", self.lower)

    def test_states_no_plugin_execution(self):
        self.assertIn("no plugin execution", self.lower)

    def test_uses_checkbox_format(self):
        self.assertIn("- [ ]", self.text)


# ---------------------------------------------------------------------------
# Go/No-Go Template
# ---------------------------------------------------------------------------

class TestGoNoGoTemplateExists(unittest.TestCase):

    def test_go_no_go_template_exists(self):
        self.assertTrue(_GO_NO_GO.is_file(), f"Missing: {_GO_NO_GO}")


class TestGoNoGoTemplateContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_GO_NO_GO)
        self.lower = self.text.lower()

    def test_contains_go_decision(self):
        self.assertIn("GO", self.text)

    def test_contains_no_go_decision(self):
        self.assertIn("NO-GO", self.text)

    def test_contains_go_with_known_limitations(self):
        self.assertIn("GO WITH KNOWN LIMITATIONS", self.text)

    def test_contains_blocker_stop_rule(self):
        self.assertIn("blocker", self.lower)
        self.assertIn("no-go", self.lower)

    def test_contains_reviewer_section(self):
        self.assertIn("Reviewer", self.text)

    def test_contains_review_date_section(self):
        self.assertIn("Review Date", self.text)

    def test_contains_artifacts_reviewed_section(self):
        self.assertIn("Artifacts Reviewed", self.text)

    def test_contains_command_results_section(self):
        self.assertIn("Command Results", self.text)

    def test_contains_known_limitations_accepted(self):
        self.assertIn("Known Limitations Accepted", self.text)

    def test_known_limitations_include_no_installer(self):
        self.assertIn("no installer", self.lower)

    def test_known_limitations_include_no_code_signing(self):
        self.assertIn("no code signing", self.lower)

    def test_known_limitations_include_no_database(self):
        self.assertIn("no database", self.lower)

    def test_known_limitations_include_no_provider(self):
        self.assertIn("no provider", self.lower)

    def test_known_limitations_include_no_plugin_execution(self):
        self.assertIn("no plugin execution", self.lower)

    def test_known_limitations_include_not_production_ready(self):
        self.assertIn("not production ready", self.lower)

    def test_contains_open_blockers_section(self):
        self.assertIn("Open Blockers", self.text)

    def test_contains_sign_off_section(self):
        self.assertIn("Sign-Off", self.text)

    def test_states_not_final_release_approval(self):
        self.assertIn("not a final release approval", self.lower)

    def test_contains_evidence_section(self):
        self.assertIn("Evidence", self.text)


# ---------------------------------------------------------------------------
# Release Notes — QA section
# ---------------------------------------------------------------------------

class TestReleaseNotesQASection(unittest.TestCase):

    def setUp(self):
        self.text = _read(_RC_NOTES)
        self.lower = self.text.lower()

    def test_release_notes_exist(self):
        self.assertTrue(_RC_NOTES.is_file(), f"Missing: {_RC_NOTES}")

    def test_release_notes_have_qa_section(self):
        self.assertIn("QA and Validation", self.text)

    def test_release_notes_reference_qa_plan(self):
        self.assertIn("V0_1_RELEASE_CANDIDATE_QA_PLAN.md", self.text)

    def test_release_notes_reference_regression_checklist(self):
        self.assertIn("V0_1_REGRESSION_CHECKLIST.md", self.text)

    def test_release_notes_reference_packaging_checklist(self):
        self.assertIn("V0_1_PACKAGING_VALIDATION_CHECKLIST.md", self.text)

    def test_release_notes_reference_go_no_go_template(self):
        self.assertIn("V0_1_GO_NO_GO_REPORT_TEMPLATE.md", self.text)

    def test_release_notes_do_not_claim_production_readiness(self):
        self.assertIn("no production readiness", self.lower)

    def test_release_notes_do_not_claim_final_release(self):
        self.assertIn("not a final release", self.lower)


if __name__ == "__main__":
    unittest.main()

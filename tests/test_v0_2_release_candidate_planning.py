"""Tests for TASK-000070: v0.2 Release Candidate Planning."""

import unittest
from pathlib import Path

QA_DIR = Path(__file__).parent.parent / "docs" / "qa"
RELEASE_NOTES_DIR = Path(__file__).parent.parent / "release-notes"

RC_PLAN = QA_DIR / "V0_2_RELEASE_CANDIDATE_PLAN.md"
SCOPE_FREEZE = QA_DIR / "V0_2_SCOPE_FREEZE_CHECKLIST.md"
REGRESSION = QA_DIR / "V0_2_REGRESSION_CHECKLIST.md"
GO_NO_GO = QA_DIR / "V0_2_GO_NO_GO_TEMPLATE.md"
RELEASE_NOTES = RELEASE_NOTES_DIR / "AuroraStudio-v0.2.0-rc1.md"


def _read(path):
    return path.read_text(encoding="utf-8")


class TestFilesExist(unittest.TestCase):
    def test_rc_plan_exists(self):
        self.assertTrue(RC_PLAN.exists(), f"Missing: {RC_PLAN}")

    def test_scope_freeze_exists(self):
        self.assertTrue(SCOPE_FREEZE.exists(), f"Missing: {SCOPE_FREEZE}")

    def test_regression_checklist_exists(self):
        self.assertTrue(REGRESSION.exists(), f"Missing: {REGRESSION}")

    def test_go_no_go_template_exists(self):
        self.assertTrue(GO_NO_GO.exists(), f"Missing: {GO_NO_GO}")

    def test_release_notes_exist(self):
        self.assertTrue(RELEASE_NOTES.exists(), f"Missing: {RELEASE_NOTES}")


class TestRCPlanIncludedScope(unittest.TestCase):
    def _content(self):
        return _read(RC_PLAN)

    def test_includes_scene_detail_editor(self):
        self.assertIn("Scene detail editor", self._content())

    def test_includes_shot_detail_editor(self):
        self.assertIn("Shot detail editor", self._content())

    def test_includes_timeline_editor(self):
        self.assertIn("Timeline editor", self._content())

    def test_includes_asset_browser(self):
        self.assertIn("Asset browser", self._content())

    def test_includes_asset_linking(self):
        self.assertIn("Asset linking", self._content())

    def test_includes_character_detail_editor(self):
        self.assertIn("Character detail editor", self._content())

    def test_includes_character_reference_workflow(self):
        self.assertIn("Character reference workflow", self._content())

    def test_includes_afl_validation(self):
        self.assertIn("AFL validation", self._content())

    def test_includes_prompt_template_system(self):
        self.assertIn("Prompt template system", self._content())

    def test_includes_prompt_export_preview(self):
        self.assertIn("Prompt export preview", self._content())

    def test_includes_export_profiles(self):
        self.assertIn("Export profiles", self._content())

    def test_includes_search_filters(self):
        self.assertIn("search", self._content().lower())

    def test_includes_json_hardening(self):
        self.assertIn("JSON", self._content())

    def test_includes_autosave_planning(self):
        self.assertIn("Autosave planning", self._content())

    def test_includes_undo_redo_planning(self):
        self.assertIn("Undo/redo planning", self._content())

    def test_includes_provider_adapter_planning(self):
        self.assertIn("Provider adapter planning", self._content())

    def test_includes_plugin_sandbox_planning(self):
        self.assertIn("Plugin sandbox planning", self._content())


class TestRCPlanExcludedScope(unittest.TestCase):
    def _content(self):
        return _read(RC_PLAN)

    def test_excludes_provider_integration(self):
        c = self._content().lower()
        self.assertIn("no provider integration", c)

    def test_excludes_plugin_execution(self):
        c = self._content().lower()
        self.assertIn("no plugin execution", c)

    def test_excludes_database(self):
        c = self._content().lower()
        self.assertIn("no database", c)

    def test_excludes_autosave_impl(self):
        c = self._content().lower()
        self.assertIn("no autosave implementation", c)

    def test_excludes_undo_redo_impl(self):
        c = self._content().lower()
        self.assertIn("no undo/redo implementation", c)

    def test_excludes_installer(self):
        c = self._content().lower()
        self.assertIn("no installer", c)


class TestScopeFreeze(unittest.TestCase):
    def test_has_editor_scope_group(self):
        self.assertIn("Editor Scope", _read(SCOPE_FREEZE))

    def test_has_prompt_export_scope_group(self):
        self.assertIn("Prompt/Export Scope", _read(SCOPE_FREEZE))

    def test_has_persistence_scope_group(self):
        self.assertIn("Persistence Scope", _read(SCOPE_FREEZE))

    def test_has_planning_scope_group(self):
        self.assertIn("Planning Scope", _read(SCOPE_FREEZE))

    def test_has_explicit_exclusions_group(self):
        self.assertIn("Explicit Exclusions", _read(SCOPE_FREEZE))

    def test_has_regression_readiness_group(self):
        self.assertIn("Regression Readiness", _read(SCOPE_FREEZE))

    def test_has_packaging_readiness_group(self):
        self.assertIn("Packaging Readiness", _read(SCOPE_FREEZE))

    def test_has_known_limitations_group(self):
        self.assertIn("Known Limitations", _read(SCOPE_FREEZE))


class TestRegressionChecklist(unittest.TestCase):
    def test_mentions_automated_tests(self):
        self.assertIn("python -m unittest", _read(REGRESSION))

    def test_mentions_headless_smoke(self):
        self.assertIn("headless-smoke", _read(REGRESSION))

    def test_mentions_cli_smoke(self):
        self.assertIn("smoke", _read(REGRESSION).lower())

    def test_mentions_json_hardening_workflow(self):
        self.assertIn("JSON Hardening", _read(REGRESSION))

    def test_mentions_prompt_template_workflow(self):
        self.assertIn("Prompt Template", _read(REGRESSION))

    def test_mentions_search_filter_workflow(self):
        self.assertIn("Search", _read(REGRESSION))

    def test_mentions_packaging_scripts(self):
        c = _read(REGRESSION).lower()
        self.assertIn("packaging", c)


class TestGoNoGoTemplate(unittest.TestCase):
    def test_has_blocker_rule(self):
        c = _read(GO_NO_GO)
        self.assertIn("any blocker remains open", c.lower())
        self.assertIn("NO-GO", c)

    def test_has_decision_choices(self):
        c = _read(GO_NO_GO)
        self.assertIn("GO", c)
        self.assertIn("NO-GO", c)
        self.assertIn("GO WITH KNOWN LIMITATIONS", c)
        self.assertIn("PENDING", c)

    def test_has_automated_test_evidence_section(self):
        self.assertIn("Automated Test Evidence", _read(GO_NO_GO))

    def test_has_manual_qa_evidence_section(self):
        self.assertIn("Manual QA Evidence", _read(GO_NO_GO))

    def test_has_packaging_evidence_section(self):
        self.assertIn("Packaging Evidence", _read(GO_NO_GO))

    def test_has_open_blockers_section(self):
        self.assertIn("Open Blockers", _read(GO_NO_GO))

    def test_has_sign_off_section(self):
        self.assertIn("Sign-off", _read(GO_NO_GO))


class TestReleaseNotes(unittest.TestCase):
    def test_states_rc1_not_final(self):
        c = _read(RELEASE_NOTES)
        self.assertIn("rc1", c.lower())
        self.assertTrue("NOT a final release" in c or "not a final release" in c.lower())

    def test_does_not_claim_production_readiness(self):
        c = _read(RELEASE_NOTES).lower()
        # Must explicitly deny production readiness claim
        self.assertIn("not claim production readiness", c)

    def test_has_known_limitations_section(self):
        self.assertIn("Known Limitations", _read(RELEASE_NOTES))

    def test_mentions_no_provider_integration(self):
        c = _read(RELEASE_NOTES).lower()
        self.assertIn("no provider integration", c)

    def test_mentions_no_plugin_execution(self):
        c = _read(RELEASE_NOTES).lower()
        self.assertIn("no plugin execution", c)

    def test_mentions_no_database(self):
        c = _read(RELEASE_NOTES).lower()
        self.assertIn("no database", c)

    def test_has_how_to_run_section(self):
        self.assertIn("How to Run", _read(RELEASE_NOTES))

    def test_has_how_to_smoke_test_section(self):
        self.assertIn("How to Smoke Test", _read(RELEASE_NOTES))

    def test_has_not_included_section(self):
        self.assertIn("Not Included", _read(RELEASE_NOTES))

    def test_has_validation_section(self):
        self.assertIn("Validation", _read(RELEASE_NOTES))


if __name__ == "__main__":
    unittest.main()

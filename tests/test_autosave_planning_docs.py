"""Tests for TASK-000066: Autosave Planning Documentation."""

import unittest
from pathlib import Path

PLAN_PATH = Path(__file__).parent.parent / "docs" / "planning" / "AUTOSAVE_PLAN.md"


def _content():
    return PLAN_PATH.read_text(encoding="utf-8")


class TestAutosavePlanExists(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(PLAN_PATH.exists(), f"Missing: {PLAN_PATH}")

    def test_file_not_empty(self):
        self.assertGreater(len(_content().strip()), 0)


class TestRequiredSections(unittest.TestCase):
    def _assert_section(self, heading):
        self.assertIn(heading, _content(), f"Missing section: {heading!r}")

    def test_purpose_section(self):
        self._assert_section("## Purpose")

    def test_current_save_behavior_section(self):
        self._assert_section("## Current Save Behavior")

    def test_non_goals_section(self):
        self._assert_section("## Non-goals")

    def test_autosave_trigger_policy_section(self):
        self._assert_section("## Autosave Trigger Policy")

    def test_manual_save_priority_section(self):
        self._assert_section("## Manual Save Priority")

    def test_backup_location_section(self):
        self._assert_section("## Backup Location")

    def test_recovery_flow_section(self):
        self._assert_section("## Recovery Flow")

    def test_conflict_behavior_section(self):
        self._assert_section("## Conflict Behavior")

    def test_corruption_protection_section(self):
        self._assert_section("## Corruption Protection")

    def test_ui_indicators_section(self):
        self._assert_section("## UI Indicators")

    def test_failure_handling_section(self):
        self._assert_section("## Failure Handling")

    def test_testing_strategy_section(self):
        self._assert_section("## Testing Strategy")

    def test_future_implementation_tasks_section(self):
        self._assert_section("## Future Implementation Tasks")

    def test_risks_section(self):
        self._assert_section("## Risks")

    def test_acceptance_criteria_section(self):
        self._assert_section("## Acceptance Criteria")


class TestRequiredStatements(unittest.TestCase):
    def test_states_not_implemented(self):
        c = _content()
        self.assertTrue(
            "not implemented in TASK-000066" in c or
            "Autosave is not implemented" in c,
            "Must state autosave is not implemented"
        )

    def test_states_no_background_timer(self):
        c = _content().lower()
        self.assertIn("no background timer", c)

    def test_states_no_thread_added(self):
        c = _content().lower()
        self.assertIn("no thread", c)

    def test_states_manual_save_source_of_truth(self):
        c = _content().lower()
        self.assertIn("source of truth", c)

    def test_mentions_recovery_flow(self):
        self.assertIn("Recovery Flow", _content())

    def test_mentions_corruption_protection(self):
        c = _content().lower()
        self.assertTrue(
            "corruption" in c or "corrupt" in c,
            "Must mention corruption protection"
        )

    def test_mentions_autosave_must_not_destroy_data(self):
        c = _content().lower()
        self.assertIn("destroy", c)

    def test_mentions_autosave_uses_backups(self):
        c = _content().lower()
        self.assertTrue("backup" in c or "recovery" in c)

    def test_states_requires_later_task(self):
        c = _content().lower()
        self.assertIn("later task", c)


if __name__ == "__main__":
    unittest.main()

"""Tests for TASK-000067: Undo/Redo Planning Documentation."""

import unittest
from pathlib import Path

PLAN_PATH = Path(__file__).parent.parent / "docs" / "planning" / "UNDO_REDO_PLAN.md"


def _content():
    return PLAN_PATH.read_text(encoding="utf-8")


class TestUndoRedoPlanExists(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(PLAN_PATH.exists(), f"Missing: {PLAN_PATH}")

    def test_file_not_empty(self):
        self.assertGreater(len(_content().strip()), 0)


class TestRequiredSections(unittest.TestCase):
    def _assert_section(self, heading):
        self.assertIn(heading, _content(), f"Missing section: {heading!r}")

    def test_purpose_section(self):
        self._assert_section("## Purpose")

    def test_current_action_behavior_section(self):
        self._assert_section("## Current Action Behavior")

    def test_non_goals_section(self):
        self._assert_section("## Non-goals")

    def test_command_model_section(self):
        self._assert_section("## Command Model")

    def test_undoable_actions_section(self):
        self._assert_section("## Undoable Actions")

    def test_non_undoable_actions_section(self):
        self._assert_section("## Non-undoable Actions")

    def test_transaction_boundaries_section(self):
        self._assert_section("## Transaction Boundaries")

    def test_state_snapshots_section(self):
        self._assert_section("## State Snapshots")

    def test_persistence_interaction_section(self):
        self._assert_section("## Persistence Interaction")

    def test_ui_controls_section(self):
        self._assert_section("## UI Controls")

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
            "not implemented in TASK-000067" in c or
            "Undo/redo is not implemented" in c,
            "Must state undo/redo is not implemented"
        )

    def test_states_no_command_history(self):
        c = _content().lower()
        self.assertIn("no command history", c)

    def test_states_manager_semantics_not_changed(self):
        c = _content().lower()
        self.assertIn("not changed", c)

    def test_mentions_transaction_boundaries(self):
        self.assertIn("Transaction Boundaries", _content())

    def test_mentions_undoable_actions(self):
        self.assertIn("Undoable Actions", _content())

    def test_mentions_non_undoable_actions(self):
        c = _content()
        self.assertIn("Non-undoable", c)

    def test_states_requires_later_task(self):
        c = _content().lower()
        self.assertIn("later", c)

    def test_save_load_not_automatically_undoable(self):
        c = _content().lower()
        self.assertIn("not automatically undoable", c)

    def test_mentions_create_scene_as_undoable_candidate(self):
        c = _content().lower()
        self.assertIn("create scene", c)

    def test_mentions_packaging_not_undoable(self):
        c = _content().lower()
        self.assertIn("packaging", c)


if __name__ == "__main__":
    unittest.main()

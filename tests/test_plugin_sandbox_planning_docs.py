"""Tests for TASK-000069: Plugin Sandbox Planning Documentation."""

import unittest
from pathlib import Path

PLAN_PATH = Path(__file__).parent.parent / "docs" / "planning" / "PLUGIN_SANDBOX_PLAN.md"


def _content():
    return PLAN_PATH.read_text(encoding="utf-8")


class TestPluginSandboxPlanExists(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(PLAN_PATH.exists(), f"Missing: {PLAN_PATH}")

    def test_file_not_empty(self):
        self.assertGreater(len(_content().strip()), 0)


class TestRequiredSections(unittest.TestCase):
    def _assert_section(self, heading):
        self.assertIn(heading, _content(), f"Missing section: {heading!r}")

    def test_purpose_section(self):
        self._assert_section("## Purpose")

    def test_current_behavior_section(self):
        self._assert_section("## Current Plugin Metadata Behavior")

    def test_non_goals_section(self):
        self._assert_section("## Non-goals")

    def test_plugin_manifest_section(self):
        self._assert_section("## Plugin Manifest Concept")

    def test_allowed_capabilities_section(self):
        self._assert_section("## Allowed Capabilities")

    def test_permission_model_section(self):
        self._assert_section("## Permission Model")

    def test_disabled_by_default_section(self):
        self._assert_section("## Disabled by Default Rule")

    def test_no_arbitrary_code_section(self):
        self._assert_section("## No Arbitrary Code Execution Rule")

    def test_sandbox_boundary_section(self):
        self._assert_section("## Sandbox Boundary")

    def test_failure_handling_section(self):
        self._assert_section("## Failure Handling")

    def test_testing_strategy_section(self):
        self._assert_section("## Testing Strategy")

    def test_future_tasks_section(self):
        self._assert_section("## Future Implementation Tasks")

    def test_risks_section(self):
        self._assert_section("## Risks")

    def test_acceptance_criteria_section(self):
        self._assert_section("## Acceptance Criteria")


class TestRequiredStatements(unittest.TestCase):
    def test_states_not_implemented(self):
        c = _content()
        self.assertTrue(
            "not implemented in TASK-000069" in c or
            "Plugin execution is not implemented" in c,
            "Must state plugin execution is not implemented"
        )

    def test_states_no_plugin_modules_loaded(self):
        c = _content().lower()
        self.assertIn("no plugin modules are loaded", c)

    def test_states_no_arbitrary_code(self):
        c = _content().lower()
        self.assertIn("no arbitrary plugin code is executed", c)

    def test_states_plugins_disabled_by_default(self):
        c = _content().lower()
        self.assertTrue("disabled by default" in c)

    def test_mentions_permission_model(self):
        self.assertIn("Permission Model", _content())

    def test_mentions_sandbox_boundary(self):
        self.assertIn("Sandbox Boundary", _content())

    def test_mentions_capability_examples(self):
        c = _content()
        self.assertIn("read_project_metadata", c)
        self.assertIn("write_export_artifact", c)

    def test_states_requires_later_task(self):
        c = _content().lower()
        self.assertIn("later sandbox task", c)

    def test_plugins_remain_metadata_only(self):
        c = _content().lower()
        self.assertIn("metadata-only", c)


if __name__ == "__main__":
    unittest.main()

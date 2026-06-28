"""Tests for TASK-000068: Provider Adapter Planning Documentation."""

import unittest
from pathlib import Path

PLAN_PATH = Path(__file__).parent.parent / "docs" / "planning" / "PROVIDER_ADAPTER_PLAN.md"


def _content():
    return PLAN_PATH.read_text(encoding="utf-8")


class TestProviderAdapterPlanExists(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(PLAN_PATH.exists(), f"Missing: {PLAN_PATH}")

    def test_file_not_empty(self):
        self.assertGreater(len(_content().strip()), 0)


class TestRequiredSections(unittest.TestCase):
    def _assert_section(self, heading):
        self.assertIn(heading, _content(), f"Missing section: {heading!r}")

    def test_purpose_section(self):
        self._assert_section("## Purpose")

    def test_current_local_only_section(self):
        self._assert_section("## Current Local-Only Export Behavior")

    def test_non_goals_section(self):
        self._assert_section("## Non-goals")

    def test_provider_interface_concept_section(self):
        self._assert_section("## Provider Interface Concept")

    def test_local_prompt_only_mode_section(self):
        self._assert_section("## Local Prompt-Only Mode")

    def test_image_provider_section(self):
        self._assert_section("## Image Provider Adapter")

    def test_video_provider_section(self):
        self._assert_section("## Video Provider Adapter")

    def test_text_provider_section(self):
        self._assert_section("## Text Provider Adapter")

    def test_api_key_storage_section(self):
        self._assert_section("## API Key Storage Rules")

    def test_no_bundled_keys_section(self):
        self._assert_section("## No Bundled Keys Rule")

    def test_request_response_logging_section(self):
        self._assert_section("## Request/Response Logging Policy")

    def test_error_handling_section(self):
        self._assert_section("## Error Handling")

    def test_safety_boundaries_section(self):
        self._assert_section("## Safety Boundaries")

    def test_testing_strategy_section(self):
        self._assert_section("## Testing Strategy")

    def test_future_tasks_section(self):
        self._assert_section("## Future Implementation Tasks")

    def test_acceptance_criteria_section(self):
        self._assert_section("## Acceptance Criteria")


class TestRequiredStatements(unittest.TestCase):
    def test_states_not_implemented(self):
        c = _content()
        self.assertTrue(
            "not implemented in TASK-000068" in c or
            "Provider integration is not implemented" in c,
            "Must state provider integration is not implemented"
        )

    def test_states_no_provider_sdk(self):
        c = _content().lower()
        self.assertIn("no provider sdk", c)

    def test_states_no_external_api(self):
        c = _content().lower()
        self.assertIn("no external api", c)

    def test_states_no_keys_bundled(self):
        c = _content().lower()
        self.assertTrue("no provider key is bundled" in c or "no api key is bundled" in c or "no provider key" in c)

    def test_mentions_local_prompt_only_mode(self):
        c = _content().lower()
        self.assertIn("local prompt-only mode", c)

    def test_mentions_keys_user_provided(self):
        c = _content().lower()
        self.assertIn("user-provided", c)

    def test_mentions_keys_never_committed(self):
        c = _content().lower()
        self.assertIn("never committed", c)

    def test_mentions_logs_must_not_contain_secrets(self):
        c = _content().lower()
        self.assertIn("logs must not contain secrets", c)

    def test_states_requires_later_task(self):
        c = _content().lower()
        self.assertIn("later task", c)


if __name__ == "__main__":
    unittest.main()

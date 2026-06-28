"""Tests for TASK-000078: API Key Storage Planning + Config Boundary."""

import unittest
from pathlib import Path

PLANNING = Path(__file__).parent.parent / "docs" / "planning"
V03 = Path(__file__).parent.parent / "docs" / "v0_3"

KEY_PLAN = PLANNING / "API_KEY_STORAGE_PLAN.md"
CONFIG_BOUNDARY = V03 / "LOCAL_PROVIDER_CONFIG_BOUNDARY.md"


def _kp():
    return KEY_PLAN.read_text(encoding="utf-8")


def _cb():
    return CONFIG_BOUNDARY.read_text(encoding="utf-8")


class TestDocumentsExist(unittest.TestCase):
    def test_api_key_storage_plan_exists(self):
        self.assertTrue(KEY_PLAN.exists(), f"Missing: {KEY_PLAN}")

    def test_local_provider_config_boundary_exists(self):
        self.assertTrue(CONFIG_BOUNDARY.exists(), f"Missing: {CONFIG_BOUNDARY}")


class TestKeyStoragePlanSections(unittest.TestCase):
    def _assert(self, heading):
        self.assertIn(heading, _kp(), f"Missing section: {heading!r}")

    def test_purpose_section(self):
        self._assert("## Purpose")

    def test_current_behavior_section(self):
        self._assert("## Current Behavior")

    def test_non_goals_section(self):
        self._assert("## Non-goals")

    def test_future_rules_section(self):
        self._assert("## Future Key Storage Rules")

    def test_revocability_rule_section(self):
        self._assert("## Revocability Rule")

    def test_no_bundled_keys_section(self):
        self._assert("## No Bundled Keys Rule")

    def test_secrets_in_logs_section(self):
        self._assert("## Secrets in Logs Rule")

    def test_secrets_in_zip_section(self):
        self._assert("## Secrets in Portable ZIP Rule")

    def test_future_tasks_section(self):
        self._assert("## Future Implementation Tasks")

    def test_testing_strategy_section(self):
        self._assert("## Testing Strategy")

    def test_acceptance_criteria_section(self):
        self._assert("## Acceptance Criteria")


class TestKeyStoragePlanRequiredStatements(unittest.TestCase):
    def test_not_implemented_in_task(self):
        c = _kp()
        self.assertIn("API key storage is not implemented in TASK-000078", c)

    def test_no_keys_bundled(self):
        c = _kp().lower()
        self.assertIn("no api key is bundled", c)

    def test_keys_must_be_revocable(self):
        c = _kp().lower()
        self.assertIn("revocable", c)

    def test_logs_must_not_contain_secrets(self):
        c = _kp().lower()
        self.assertIn("logs must never contain secrets", c)

    def test_keys_not_in_portable_zip(self):
        c = _kp().lower()
        self.assertIn("portable zip", c)

    def test_keys_user_provided(self):
        c = _kp().lower()
        self.assertIn("user-provided", c)

    def test_keys_never_committed(self):
        c = _kp().lower()
        self.assertIn("source control", c)

    def test_sanitizer_mentioned(self):
        c = _kp().lower()
        self.assertIn("sanitize", c)


class TestConfigBoundarySections(unittest.TestCase):
    def _assert(self, heading):
        self.assertIn(heading, _cb(), f"Missing section: {heading!r}")

    def test_purpose_section(self):
        self._assert("## Purpose")

    def test_may_store_section(self):
        self._assert("## What v0.3 May Store Locally")

    def test_must_not_store_section(self):
        self._assert("## What v0.3 Must Not Store Locally")

    def test_no_credentials_in_pack(self):
        self._assert("## No Real Credential Storage in TASK-000076-080")

    def test_dry_run_config_section(self):
        self._assert("## Dry-Run Config")

    def test_future_escalation_section(self):
        self._assert("## Future Escalation")


class TestConfigBoundaryStatements(unittest.TestCase):
    def test_no_real_credentials_in_pack(self):
        c = _cb()
        self.assertIn("No real credential storage is implemented in TASK-000076 through TASK-000080", c)

    def test_no_api_keys_in_config(self):
        c = _cb().lower()
        self.assertIn("api keys", c)

    def test_dry_run_no_api_key(self):
        c = _cb().lower()
        self.assertIn("requires no api key", c)

    def test_dry_run_no_network(self):
        c = _cb().lower()
        self.assertIn("requires no network access", c)


if __name__ == "__main__":
    unittest.main()

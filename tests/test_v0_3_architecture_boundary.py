"""Tests for TASK-000076: v0.3 Architecture Boundary."""

import unittest
from pathlib import Path

DOCS_V03 = Path(__file__).parent.parent / "docs" / "v0_3"
ARCH_BOUNDARY = DOCS_V03 / "V0_3_ARCHITECTURE_BOUNDARY.md"
SEC_BOUNDARY = DOCS_V03 / "V0_3_PROVIDER_SECURITY_BOUNDARY.md"


def _arch():
    return ARCH_BOUNDARY.read_text(encoding="utf-8")


def _sec():
    return SEC_BOUNDARY.read_text(encoding="utf-8")


class TestArchitectureBoundaryDocExists(unittest.TestCase):
    def test_architecture_boundary_doc_exists(self):
        self.assertTrue(ARCH_BOUNDARY.exists(), f"Missing: {ARCH_BOUNDARY}")

    def test_provider_security_boundary_doc_exists(self):
        self.assertTrue(SEC_BOUNDARY.exists(), f"Missing: {SEC_BOUNDARY}")


class TestArchitectureBoundarySections(unittest.TestCase):
    def _assert(self, heading):
        self.assertIn(heading, _arch(), f"Missing section: {heading!r}")

    def test_purpose_section(self):
        self._assert("## Purpose")

    def test_v03_scope_section(self):
        self._assert("## v0.3 Scope")

    def test_v03_non_goals_section(self):
        self._assert("## v0.3 Non-goals")

    def test_provider_foundation_boundary_section(self):
        self._assert("## Provider Foundation Boundary")

    def test_prompt_execution_boundary_section(self):
        self._assert("## Prompt Execution Boundary")

    def test_plugin_sandbox_boundary_section(self):
        self._assert("## Plugin Sandbox Boundary")

    def test_secret_handling_boundary_section(self):
        self._assert("## Secret Handling Boundary")

    def test_logging_boundary_section(self):
        self._assert("## Logging Boundary")

    def test_desktop_ui_boundary_section(self):
        self._assert("## Desktop UI Boundary")

    def test_persistence_boundary_section(self):
        self._assert("## Persistence Boundary")

    def test_packaging_boundary_section(self):
        self._assert("## Packaging Boundary")

    def test_testing_boundary_section(self):
        self._assert("## Testing Boundary")

    def test_future_escalation_rules_section(self):
        self._assert("## Future Escalation Rules")


class TestArchBoundaryRequiredStatements(unittest.TestCase):
    def test_mentions_no_real_api_calls(self):
        c = _arch().lower()
        self.assertTrue("no real provider api call" in c or "real provider api calls" in c)

    def test_mentions_no_provider_sdks(self):
        c = _arch().lower()
        self.assertIn("no provider sdk", c)

    def test_mentions_no_database(self):
        c = _arch().lower()
        self.assertIn("database", c)

    def test_mentions_no_plugin_execution(self):
        c = _arch().lower()
        self.assertIn("no plugin code", c)

    def test_mentions_dry_run(self):
        c = _arch().lower()
        self.assertIn("dry-run", c)

    def test_scope_includes_provider_registry(self):
        c = _arch().lower()
        self.assertIn("provider registry", c)

    def test_scope_includes_dry_run_provider(self):
        c = _arch().lower()
        self.assertIn("dry-run provider", c)

    def test_non_goals_exclude_real_api_calls(self):
        c = _arch().lower()
        self.assertIn("real provider api calls", c)


class TestSecurityBoundaryStatements(unittest.TestCase):
    def test_no_bundled_secrets(self):
        c = _sec().lower()
        self.assertIn("no bundled secrets", c)

    def test_no_real_api_calls_in_pack(self):
        c = _sec()
        self.assertIn("No Real API Calls in TASK-000076-080", c)

    def test_no_provider_sdks_in_pack(self):
        c = _sec()
        self.assertIn("No Provider SDKs in TASK-000076-080", c)

    def test_no_secrets_in_logs(self):
        c = _sec()
        self.assertIn("No Secrets in Logs", c)

    def test_no_secrets_in_portable_zip(self):
        c = _sec()
        self.assertIn("No Secrets in Portable ZIP", c)

    def test_no_network_execution(self):
        c = _sec()
        self.assertIn("No Network Execution", c)

    def test_dry_run_only_statement(self):
        c = _sec()
        self.assertIn("Dry-Run Only", c)

    def test_future_api_key_must_be_revocable(self):
        c = _sec().lower()
        self.assertIn("revocable", c)


if __name__ == "__main__":
    unittest.main()

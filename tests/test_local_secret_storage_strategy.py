"""Tests for TASK-000103: Local Secret Storage Strategy / OS Keyring Planning.

No network calls. No keyring package. Standard library only.
"""

import unittest
from pathlib import Path

REPO = Path(__file__).parent.parent
DOCS_PLANNING = REPO / "docs" / "planning"
DOCS_V04 = REPO / "docs" / "v0_4"
SRC = REPO / "src"


class TestStrategyDocExists(unittest.TestCase):

    def test_local_secret_storage_strategy_doc_exists(self):
        p = DOCS_PLANNING / "LOCAL_SECRET_STORAGE_STRATEGY.md"
        self.assertTrue(p.exists(), f"Missing: {p}")

    def test_os_keyring_integration_plan_doc_exists(self):
        p = DOCS_V04 / "OS_KEYRING_INTEGRATION_PLAN.md"
        self.assertTrue(p.exists(), f"Missing: {p}")


class TestStrategyDocContent(unittest.TestCase):

    def setUp(self):
        self.doc = (DOCS_PLANNING / "LOCAL_SECRET_STORAGE_STRATEGY.md").read_text()

    def test_strategy_states_no_secrets_in_project_json(self):
        self.assertIn("project JSON", self.doc)
        self.assertIn("must never", self.doc.lower())

    def test_strategy_states_no_secrets_in_autosave(self):
        self.assertIn("autosave", self.doc.lower())

    def test_strategy_states_no_secrets_in_backups(self):
        self.assertIn("backup", self.doc.lower())

    def test_strategy_states_no_secrets_in_logs(self):
        self.assertIn("log", self.doc.lower())

    def test_strategy_states_no_secrets_in_portable_zip(self):
        self.assertIn("portable ZIP", self.doc)

    def test_strategy_states_no_secrets_in_export_artifacts(self):
        self.assertIn("export artifact", self.doc.lower())

    def test_strategy_states_no_secrets_in_run_history(self):
        self.assertIn("run history", self.doc.lower())

    def test_strategy_includes_threat_model_section(self):
        self.assertIn("Threat Model", self.doc)

    def test_strategy_includes_recommended_future_approach(self):
        self.assertIn("Recommended Future Approach", self.doc)

    def test_strategy_includes_user_consent_section(self):
        self.assertIn("consent", self.doc.lower())


class TestKeyringPlanContent(unittest.TestCase):

    def setUp(self):
        self.doc = (DOCS_V04 / "OS_KEYRING_INTEGRATION_PLAN.md").read_text()

    def test_keyring_plan_states_not_implemented(self):
        self.assertIn("does not implement OS keyring integration", self.doc)

    def test_keyring_plan_states_no_keyring_dependency(self):
        self.assertIn("does not add keyring dependency", self.doc)

    def test_keyring_plan_states_no_real_api_keys(self):
        self.assertIn("does not store real API keys", self.doc)

    def test_keyring_plan_includes_windows_section(self):
        self.assertIn("Windows", self.doc)

    def test_keyring_plan_includes_macos_section(self):
        self.assertIn("macOS", self.doc)

    def test_keyring_plan_includes_linux_section(self):
        self.assertIn("Linux", self.doc)

    def test_keyring_plan_includes_fallback_section(self):
        self.assertIn("Fallback", self.doc)

    def test_keyring_plan_includes_portable_mode_section(self):
        self.assertIn("Portable Mode", self.doc)

    def test_keyring_plan_includes_revocation_section(self):
        self.assertIn("Revocation", self.doc)

    def test_keyring_plan_includes_testing_requirements(self):
        self.assertIn("Testing Requirements", self.doc)


class TestSecurityConstants(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))

    def test_secret_field_names_constant_exists(self):
        from aurora_studio.contracts.provider_security import SECRET_FIELD_NAMES
        self.assertIsInstance(SECRET_FIELD_NAMES, frozenset)

    def test_secret_field_names_covers_api_key(self):
        from aurora_studio.contracts.provider_security import SECRET_FIELD_NAMES
        self.assertIn("api_key", SECRET_FIELD_NAMES)

    def test_secret_field_names_covers_token(self):
        from aurora_studio.contracts.provider_security import SECRET_FIELD_NAMES
        self.assertIn("token", SECRET_FIELD_NAMES)

    def test_secret_field_names_covers_password(self):
        from aurora_studio.contracts.provider_security import SECRET_FIELD_NAMES
        self.assertIn("password", SECRET_FIELD_NAMES)

    def test_secret_field_names_covers_bearer(self):
        from aurora_studio.contracts.provider_security import SECRET_FIELD_NAMES
        self.assertIn("bearer", SECRET_FIELD_NAMES)

    def test_secret_field_names_contains_no_real_secrets(self):
        from aurora_studio.contracts.provider_security import SECRET_FIELD_NAMES
        # Constants are field name strings, not real secrets
        for name in SECRET_FIELD_NAMES:
            self.assertLess(len(name), 50, f"Field name too long to be a constant: {name}")
            self.assertFalse(name.startswith("sk-"), "Secret value leaked into constant names")

    def test_prohibited_locations_constant_exists(self):
        from aurora_studio.contracts.provider_security import SECRET_STORAGE_PROHIBITED_LOCATIONS
        self.assertIsInstance(SECRET_STORAGE_PROHIBITED_LOCATIONS, frozenset)

    def test_prohibited_locations_includes_project_json(self):
        from aurora_studio.contracts.provider_security import SECRET_STORAGE_PROHIBITED_LOCATIONS
        self.assertIn("project_json", SECRET_STORAGE_PROHIBITED_LOCATIONS)

    def test_prohibited_locations_includes_autosave(self):
        from aurora_studio.contracts.provider_security import SECRET_STORAGE_PROHIBITED_LOCATIONS
        self.assertIn("autosave_file", SECRET_STORAGE_PROHIBITED_LOCATIONS)

    def test_prohibited_locations_includes_backup(self):
        from aurora_studio.contracts.provider_security import SECRET_STORAGE_PROHIBITED_LOCATIONS
        self.assertIn("backup_file", SECRET_STORAGE_PROHIBITED_LOCATIONS)

    def test_prohibited_locations_includes_portable_zip(self):
        from aurora_studio.contracts.provider_security import SECRET_STORAGE_PROHIBITED_LOCATIONS
        self.assertIn("portable_zip", SECRET_STORAGE_PROHIBITED_LOCATIONS)

    def test_prohibited_locations_includes_logs(self):
        from aurora_studio.contracts.provider_security import SECRET_STORAGE_PROHIBITED_LOCATIONS
        self.assertIn("provider_log", SECRET_STORAGE_PROHIBITED_LOCATIONS)

    def test_no_keyring_package_imported(self):
        import sys
        for mod in list(sys.modules.keys()):
            self.assertNotIn("keyring", mod, "keyring package must not be imported")


if __name__ == "__main__":
    unittest.main()

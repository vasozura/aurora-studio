"""Tests for TASK-000098: v0.3 Portable ZIP RC Pack."""

import os
import unittest

RC_PROCESS_DOC = "docs/packaging/V0_3_PORTABLE_ZIP_RC_PROCESS.md"
RC_NOTES = "release-notes/AuroraStudio-v0.3.0-rc1.md"
SCRIPTS = [
    "scripts/create_v0_3_portable_zip_rc.ps1",
    "scripts/create_v0_3_portable_zip_rc.bat",
    "scripts/smoke_v0_3_portable_zip_rc.ps1",
    "scripts/smoke_v0_3_portable_zip_rc.bat",
]


def _c(path):
    with open(path) as f:
        return f.read()


class TestRCDocsExist(unittest.TestCase):
    def test_rc_process_doc_exists(self):
        self.assertTrue(os.path.exists(RC_PROCESS_DOC))

    def test_rc_notes_exist(self):
        self.assertTrue(os.path.exists(RC_NOTES))


class TestRCScriptsExist(unittest.TestCase):
    def test_create_ps1_exists(self):
        self.assertTrue(os.path.exists("scripts/create_v0_3_portable_zip_rc.ps1"))

    def test_create_bat_exists(self):
        self.assertTrue(os.path.exists("scripts/create_v0_3_portable_zip_rc.bat"))

    def test_smoke_ps1_exists(self):
        self.assertTrue(os.path.exists("scripts/smoke_v0_3_portable_zip_rc.ps1"))

    def test_smoke_bat_exists(self):
        self.assertTrue(os.path.exists("scripts/smoke_v0_3_portable_zip_rc.bat"))


class TestRCProcessDocContent(unittest.TestCase):
    def test_states_release_candidate_only(self):
        self.assertIn("release candidate process only", _c(RC_PROCESS_DOC).lower())

    def test_states_no_final_release_approval(self):
        self.assertIn("PENDING", _c(RC_PROCESS_DOC))

    def test_states_no_code_signing(self):
        self.assertIn("not sign code", _c(RC_PROCESS_DOC).replace("does not sign", "not sign"))

    def test_mentions_sha256(self):
        self.assertIn("sha256", _c(RC_PROCESS_DOC).lower())

    def test_mentions_excluded_files(self):
        c = _c(RC_PROCESS_DOC).lower()
        self.assertIn(".env", c)

    def test_has_no_final_release_rule(self):
        self.assertIn("No-Final-Release Rule", _c(RC_PROCESS_DOC))


class TestRCNotesContent(unittest.TestCase):
    def test_says_rc1_not_final(self):
        self.assertIn("rc1", _c(RC_NOTES).lower())

    def test_decision_status_pending(self):
        self.assertIn("PENDING", _c(RC_NOTES))

    def test_not_included_provider_sdk(self):
        self.assertIn("Provider SDKs", _c(RC_NOTES))

    def test_not_included_plugin_execution(self):
        self.assertIn("Plugin execution", _c(RC_NOTES))

    def test_not_included_database(self):
        self.assertIn("Database", _c(RC_NOTES))

    def test_not_included_media_preview(self):
        self.assertIn("Media preview", _c(RC_NOTES))

    def test_does_not_claim_production_readiness(self):
        self.assertNotIn("production ready", _c(RC_NOTES).lower())


class TestScriptsContent(unittest.TestCase):
    def test_create_script_mentions_sha256(self):
        self.assertIn("SHA256", _c("scripts/create_v0_3_portable_zip_rc.ps1"))

    def test_smoke_script_validates_sha256(self):
        self.assertIn("SHA256", _c("scripts/smoke_v0_3_portable_zip_rc.ps1"))

    def test_create_script_no_secrets(self):
        c = _c("scripts/create_v0_3_portable_zip_rc.ps1").lower()
        self.assertNotIn("api_key", c)
        self.assertNotIn("openai", c)

    def test_smoke_script_checks_run_bat(self):
        self.assertIn("run_desktop.bat", _c("scripts/smoke_v0_3_portable_zip_rc.ps1"))

    def test_smoke_script_checks_readme(self):
        self.assertIn("README.txt", _c("scripts/smoke_v0_3_portable_zip_rc.ps1"))

    def test_smoke_script_checks_notice(self):
        self.assertIn("NOTICE.txt", _c("scripts/smoke_v0_3_portable_zip_rc.ps1"))


if __name__ == "__main__":
    unittest.main()

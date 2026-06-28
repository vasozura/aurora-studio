"""Tests for TASK-000099: v0.3 QA / Go-No-Go Pack."""

import os
import unittest

QA_PLAN = "docs/qa/V0_3_QA_PLAN.md"
REGRESSION = "docs/qa/V0_3_REGRESSION_CHECKLIST.md"
PKG_CHECKLIST = "docs/qa/V0_3_PACKAGING_VALIDATION_CHECKLIST.md"
GO_NO_GO = "docs/qa/V0_3_GO_NO_GO_TEMPLATE.md"


def _c(path):
    with open(path) as f:
        return f.read()


class TestQADocsExist(unittest.TestCase):
    def test_qa_plan_exists(self):
        self.assertTrue(os.path.exists(QA_PLAN))

    def test_regression_checklist_exists(self):
        self.assertTrue(os.path.exists(REGRESSION))

    def test_packaging_validation_checklist_exists(self):
        self.assertTrue(os.path.exists(PKG_CHECKLIST))

    def test_go_no_go_template_exists(self):
        self.assertTrue(os.path.exists(GO_NO_GO))


class TestQAPlanContent(unittest.TestCase):
    def test_qa_plan_lists_provider_area(self):
        self.assertIn("Provider", _c(QA_PLAN))

    def test_qa_plan_lists_plugin_area(self):
        self.assertIn("Plugin", _c(QA_PLAN))

    def test_qa_plan_lists_backup_area(self):
        self.assertIn("backup", _c(QA_PLAN).lower())

    def test_qa_plan_lists_autosave_area(self):
        self.assertIn("autosave", _c(QA_PLAN).lower())

    def test_qa_plan_lists_undo_area(self):
        self.assertIn("undo", _c(QA_PLAN).lower())

    def test_out_of_scope_lists_real_provider_api(self):
        self.assertIn("Real provider API tests", _c(QA_PLAN))

    def test_out_of_scope_lists_plugin_execution(self):
        self.assertIn("Plugin execution tests", _c(QA_PLAN))

    def test_out_of_scope_lists_database(self):
        self.assertIn("Database tests", _c(QA_PLAN))

    def test_out_of_scope_lists_media_preview(self):
        self.assertIn("Media preview tests", _c(QA_PLAN))


class TestGoNoGoContent(unittest.TestCase):
    def test_decision_choices_present(self):
        c = _c(GO_NO_GO)
        self.assertIn("GO", c)
        self.assertIn("NO-GO", c)
        self.assertIn("PENDING", c)
        self.assertIn("GO WITH KNOWN LIMITATIONS", c)

    def test_blocker_rule_present(self):
        c = _c(GO_NO_GO)
        self.assertIn("blocker", c.lower())
        self.assertIn("NO-GO", c)

    def test_security_boundary_evidence_present(self):
        self.assertIn("Security Boundary Evidence", _c(GO_NO_GO))

    def test_security_no_real_provider_calls(self):
        self.assertIn("No real provider API calls", _c(GO_NO_GO))

    def test_security_no_plugin_execution(self):
        self.assertIn("No plugin execution", _c(GO_NO_GO))

    def test_security_no_database(self):
        self.assertIn("No database", _c(GO_NO_GO))

    def test_security_no_media_decoding(self):
        self.assertIn("No media decoding", _c(GO_NO_GO))

    def test_security_no_background_workers(self):
        self.assertIn("No background workers", _c(GO_NO_GO))

    def test_security_no_bundled_secrets(self):
        self.assertIn("No bundled secrets", _c(GO_NO_GO))


class TestPackagingChecklistContent(unittest.TestCase):
    def test_no_secrets_item(self):
        self.assertIn("No secrets", _c(PKG_CHECKLIST))

    def test_no_api_keys_item(self):
        self.assertIn("No API keys", _c(PKG_CHECKLIST))

    def test_sha256_item(self):
        self.assertIn("SHA256", _c(PKG_CHECKLIST))

    def test_run_bat_item(self):
        self.assertIn("run_desktop.bat", _c(PKG_CHECKLIST))

    def test_zip_item(self):
        self.assertIn("ZIP", _c(PKG_CHECKLIST))


if __name__ == "__main__":
    unittest.main()

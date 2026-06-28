"""Tests for TASK-000085: Provider Adapter QA Pack."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

DOCS_V03 = Path(__file__).parent.parent / "docs" / "v0_3"
QA_CHECKLIST = DOCS_V03 / "PROVIDER_FOUNDATION_QA_CHECKLIST.md"
WORKFLOW_QA = DOCS_V03 / "PROMPT_EXECUTION_WORKFLOW_QA.md"


def _qc():
    return QA_CHECKLIST.read_text(encoding="utf-8")


def _wq():
    return WORKFLOW_QA.read_text(encoding="utf-8")


class TestQADocumentsExist(unittest.TestCase):
    def test_qa_checklist_exists(self):
        self.assertTrue(QA_CHECKLIST.exists(), f"Missing: {QA_CHECKLIST}")

    def test_workflow_qa_exists(self):
        self.assertTrue(WORKFLOW_QA.exists(), f"Missing: {WORKFLOW_QA}")


class TestQAChecklistSections(unittest.TestCase):
    def _assert(self, heading):
        self.assertIn(heading, _qc(), f"Missing section: {heading!r}")

    def test_purpose_section(self):
        self._assert("## Purpose")

    def test_scope_section(self):
        self._assert("## Scope")

    def test_non_goals_section(self):
        self._assert("## Non-goals")

    def test_provider_registry_checks(self):
        self._assert("## Provider Registry Checks")

    def test_config_boundary_checks(self):
        self._assert("## Provider Config Boundary Checks")

    def test_dry_run_adapter_checks(self):
        self._assert("## Dry-Run Adapter Checks")

    def test_queue_checks(self):
        self._assert("## Prompt Execution Queue Checks")

    def test_batch_export_checks(self):
        self._assert("## Batch Export Checks")

    def test_run_history_checks(self):
        self._assert("## Run History Checks")

    def test_provider_log_checks(self):
        self._assert("## Provider Log Checks")

    def test_error_handling_checks(self):
        self._assert("## Error Handling Checks")

    def test_secret_handling_checks(self):
        self._assert("## Secret Handling Checks")

    def test_no_network_checks(self):
        self._assert("## No Real Provider API Calls")

    def test_desktop_ui_checks(self):
        self._assert("## Desktop UI Checks")

    def test_cli_checks(self):
        self._assert("## CLI Checks")

    def test_packaging_checks(self):
        self._assert("## Packaging Checks")

    def test_known_limitations(self):
        self._assert("## Known Limitations")


class TestQAChecklistRequiredStatements(unittest.TestCase):
    def test_no_real_api_calls_stated(self):
        c = _qc()
        self.assertIn("No real provider API calls are included", c)

    def test_no_provider_sdks_stated(self):
        c = _qc()
        self.assertIn("No provider SDKs are installed or imported", c)

    def test_no_real_api_keys_stated(self):
        c = _qc()
        self.assertIn("No real API keys are stored", c)

    def test_no_secrets_logged_stated(self):
        c = _qc()
        self.assertIn("No Secrets Logged", c)

    def test_dry_run_local_only_stated(self):
        c = _qc()
        self.assertIn("Dry-Run Provider Is Local Only", c)

    def test_plugin_execution_disabled_stated(self):
        c = _qc()
        self.assertIn("Plugin Execution Remains Disabled", c)


class TestWorkflowQASections(unittest.TestCase):
    def _assert(self, heading):
        self.assertIn(heading, _wq(), f"Missing section: {heading!r}")

    def test_manual_dry_run_section(self):
        self._assert("## Manual Dry-Run Workflow")

    def test_manual_batch_export_section(self):
        self._assert("## Manual Batch Export Workflow")

    def test_manual_history_section(self):
        self._assert("## Manual Run History Workflow")

    def test_manual_error_section(self):
        self._assert("## Manual Error Handling Workflow")

    def test_expected_safe_failures_section(self):
        self._assert("## Expected Safe Failures")

    def test_regression_commands_section(self):
        self._assert("## Regression Commands")

    def test_evidence_checklist_section(self):
        self._assert("## Evidence Checklist")

    def test_go_no_go_section(self):
        self._assert("## Go/No-Go for Future Real Provider Implementation")


class TestWorkflowQARequiredCommands(unittest.TestCase):
    def test_unittest_command_present(self):
        self.assertIn("python -m unittest", _wq())

    def test_headless_smoke_command_present(self):
        self.assertIn("--headless-smoke", _wq())

    def test_cli_smoke_command_present(self):
        self.assertIn("python -m aurora_studio.cli smoke", _wq())


class TestProviderSmokeCLI(unittest.TestCase):
    def test_provider_smoke_outputs_json(self):
        result = subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli", "provider-smoke"],
            capture_output=True, text=True,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
            cwd=str(Path(__file__).parent.parent),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data.get("ok"), data)

    def test_provider_smoke_has_providers(self):
        result = subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli", "provider-smoke"],
            capture_output=True, text=True,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
            cwd=str(Path(__file__).parent.parent),
        )
        data = json.loads(result.stdout)
        self.assertIn("providers", data)
        self.assertGreater(len(data["providers"]), 0)

    def test_provider_smoke_dry_run_status(self):
        result = subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli", "provider-smoke"],
            capture_output=True, text=True,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
            cwd=str(Path(__file__).parent.parent),
        )
        data = json.loads(result.stdout)
        self.assertEqual(data["dry_run"]["status"], "dry_run")

    def test_provider_smoke_no_sdk_imported(self):
        """provider-smoke must not import any provider SDK."""
        result = subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.path.insert(0,'src'); "
             "from aurora_studio.cli.main import _cmd_provider_smoke; "
             "import argparse; _cmd_provider_smoke(argparse.Namespace()); "
             "assert 'openai' not in sys.modules; "
             "assert 'anthropic' not in sys.modules"],
            capture_output=True, text=True,
            cwd=str(Path(__file__).parent.parent),
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()

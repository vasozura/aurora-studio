"""
tests/test_windows_portable_exe_planning.py

TASK-000045: Windows Portable EXE Planning Pack
Tests for packaging planning documents.

Rules:
- Standard-library unittest only
- No display required
- No EXE build
- No PyInstaller
- No Windows required
"""

import pathlib
import unittest

_REPO = pathlib.Path(__file__).parent.parent
_DOCS_PKG = _REPO / "docs" / "packaging"
_EXE_PLAN = _DOCS_PKG / "WINDOWS_PORTABLE_EXE_PLAN.md"
_FOLDER_LAYOUT = _DOCS_PKG / "PORTABLE_FOLDER_LAYOUT.md"
_RISK_REGISTER = _DOCS_PKG / "PACKAGING_RISK_REGISTER.md"
_FUTURE_BOUNDARY = _DOCS_PKG / "PYINSTALLER_FUTURE_BUILD_BOUNDARY.md"
_PYPROJECT = _REPO / "pyproject.toml"


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPackagingDocsExist(unittest.TestCase):
    """All four planning documents must exist."""

    def test_docs_packaging_dir_exists(self):
        self.assertTrue(_DOCS_PKG.is_dir(), f"Missing dir: {_DOCS_PKG}")

    def test_exe_plan_exists(self):
        self.assertTrue(_EXE_PLAN.is_file(), f"Missing: {_EXE_PLAN}")

    def test_folder_layout_exists(self):
        self.assertTrue(_FOLDER_LAYOUT.is_file(), f"Missing: {_FOLDER_LAYOUT}")

    def test_risk_register_exists(self):
        self.assertTrue(_RISK_REGISTER.is_file(), f"Missing: {_RISK_REGISTER}")

    def test_future_boundary_exists(self):
        self.assertTrue(_FUTURE_BOUNDARY.is_file(), f"Missing: {_FUTURE_BOUNDARY}")


class TestExePlanContent(unittest.TestCase):
    """WINDOWS_PORTABLE_EXE_PLAN.md must mention all required entry points."""

    def setUp(self):
        self.text = _read(_EXE_PLAN)

    def test_mentions_desktop_shell_entry(self):
        self.assertIn("aurora_studio.ui.desktop_shell", self.text)

    def test_mentions_headless_smoke_entry(self):
        self.assertIn("--headless-smoke", self.text)

    def test_mentions_cli_smoke_entry(self):
        self.assertIn("aurora_studio.cli smoke", self.text)

    def test_mentions_create_demo_entry(self):
        self.assertIn("create-demo", self.text)

    def test_mentions_validate_bundle_entry(self):
        self.assertIn("validate-bundle", self.text)

    def test_mentions_rehydrate_bundle_entry(self):
        self.assertIn("rehydrate-bundle", self.text)

    def test_states_no_exe_build_in_this_task(self):
        text_lower = self.text.lower()
        self.assertIn("no exe build in this task", text_lower)

    def test_states_pyinstaller_is_future_only(self):
        text_lower = self.text.lower()
        self.assertIn("pyinstaller is planned for a later task", text_lower)

    def test_states_no_pyinstaller_in_task_000045(self):
        self.assertIn("TASK-000045", self.text)

    def test_mentions_pyinstaller_as_candidate(self):
        self.assertIn("PyInstaller", self.text)

    def test_mentions_no_provider_integration(self):
        text_lower = self.text.lower()
        self.assertIn("no provider", text_lower)

    def test_mentions_no_plugin_execution(self):
        text_lower = self.text.lower()
        self.assertIn("no plugin", text_lower)

    def test_mentions_no_database(self):
        text_lower = self.text.lower()
        self.assertIn("no database", text_lower)

    def test_mentions_windows_10(self):
        self.assertIn("Windows 10", self.text)

    def test_mentions_python_version(self):
        self.assertIn("Python 3.11", self.text)

    def test_has_smoke_tests_section(self):
        self.assertIn("Smoke Tests", self.text)

    def test_has_release_checklist_section(self):
        self.assertIn("Release Checklist", self.text)


class TestFolderLayoutContent(unittest.TestCase):
    """PORTABLE_FOLDER_LAYOUT.md must define the correct versioned layout."""

    def setUp(self):
        self.text = _read(_FOLDER_LAYOUT)

    def test_contains_versioned_folder_name(self):
        self.assertIn("AuroraStudio-v0.1.0-windows-portable", self.text)

    def test_mentions_aurora_studio_exe(self):
        self.assertIn("AuroraStudio.exe", self.text)

    def test_mentions_run_desktop_bat(self):
        self.assertIn("run_desktop.bat", self.text)

    def test_mentions_readme_txt(self):
        self.assertIn("README.txt", self.text)

    def test_mentions_data_dir(self):
        self.assertIn("data/", self.text)

    def test_mentions_logs_dir(self):
        self.assertIn("logs/", self.text)

    def test_mentions_tmp_dir(self):
        self.assertIn("tmp/", self.text)

    def test_separates_user_data_from_app_bundle(self):
        text_lower = self.text.lower()
        self.assertIn("user data", text_lower)

    def test_states_user_project_folders_are_external(self):
        text_lower = self.text.lower()
        self.assertIn("external", text_lower)

    def test_states_no_provider_keys_bundled(self):
        text_lower = self.text.lower()
        self.assertIn("no provider", text_lower)

    def test_states_no_plugin_execution(self):
        text_lower = self.text.lower()
        self.assertIn("no plugin", text_lower)

    def test_states_no_database(self):
        text_lower = self.text.lower()
        self.assertIn("no database", text_lower)

    def test_task_must_not_create_folder(self):
        text_lower = self.text.lower()
        # Document must say this folder must not be created by this task
        self.assertIn("must not be created", text_lower)

    def test_mentions_versioning_convention(self):
        self.assertIn("Versioning", self.text)


class TestRiskRegisterContent(unittest.TestCase):
    """PACKAGING_RISK_REGISTER.md must contain all required risk areas."""

    def setUp(self):
        self.text = _read(_RISK_REGISTER)
        self.text_lower = self.text.lower()

    def test_risk_tkinter_availability(self):
        self.assertIn("tkinter", self.text_lower)

    def test_risk_windows_path_handling(self):
        self.assertIn("windows path", self.text_lower)

    def test_risk_current_working_directory(self):
        self.assertIn("current working directory", self.text_lower)

    def test_risk_pythonpath_differences(self):
        self.assertIn("pythonpath", self.text_lower)

    def test_risk_hidden_imports(self):
        self.assertIn("hidden import", self.text_lower)

    def test_risk_cli_module_entry_points(self):
        self.assertIn("cli", self.text_lower)
        self.assertIn("entry point", self.text_lower)

    def test_risk_temporary_project_cleanup(self):
        self.assertIn("temporary", self.text_lower)

    def test_risk_antivirus_false_positives(self):
        self.assertIn("antivirus", self.text_lower)

    def test_risk_unsigned_exe_warnings(self):
        self.assertIn("unsigned", self.text_lower)

    def test_risk_large_binary_size(self):
        self.assertIn("size", self.text_lower)
        self.assertIn("binary", self.text_lower)

    def test_risk_user_data_vs_app_bundle(self):
        self.assertIn("user data", self.text_lower)

    def test_risk_no_provider_keys_bundled(self):
        self.assertIn("no provider", self.text_lower)

    def test_risk_no_plugin_execution(self):
        self.assertIn("no plugin", self.text_lower)

    def test_risk_headless_smoke_reliability(self):
        self.assertIn("headless smoke", self.text_lower)

    def test_each_risk_has_impact(self):
        self.assertIn("Impact", self.text)

    def test_each_risk_has_mitigation(self):
        self.assertIn("Mitigation", self.text)

    def test_each_risk_has_future_validation(self):
        self.assertIn("Future validation", self.text)


class TestFutureBoundaryContent(unittest.TestCase):
    """PYINSTALLER_FUTURE_BUILD_BOUNDARY.md must reference TASK-000046."""

    def setUp(self):
        self.text = _read(_FUTURE_BOUNDARY)
        self.text_lower = self.text.lower()

    def test_references_task_000046(self):
        self.assertIn("TASK-000046", self.text)

    def test_names_future_task(self):
        self.assertIn("PyInstaller Build Smoke Pack", self.text)

    def test_has_allowed_future_actions_section(self):
        self.assertIn("Allowed Future Actions", self.text)

    def test_has_forbidden_future_actions_section(self):
        self.assertIn("Forbidden Future Actions", self.text)

    def test_forbids_provider_keys(self):
        self.assertIn("No provider", self.text)

    def test_forbids_plugin_execution(self):
        self.assertIn("No plugin execution", self.text)

    def test_forbids_database(self):
        self.assertIn("No database", self.text)

    def test_forbids_web_server(self):
        self.assertIn("No web server", self.text)

    def test_forbids_installer_without_separate_task(self):
        self.assertIn("No installer", self.text)

    def test_forbids_code_signing_without_separate_task(self):
        self.assertIn("No code signing", self.text)

    def test_forbids_auto_update_without_separate_task(self):
        self.assertIn("No auto-update", self.text)

    def test_has_expected_build_commands_section(self):
        self.assertIn("Expected Build Commands", self.text)

    def test_has_expected_smoke_commands_section(self):
        self.assertIn("Expected Smoke Commands", self.text)

    def test_has_expected_artifacts_section(self):
        self.assertIn("Expected Artifacts", self.text)

    def test_has_rollback_plan_section(self):
        self.assertIn("Rollback Plan", self.text)

    def test_has_acceptance_criteria_section(self):
        self.assertIn("Acceptance Criteria", self.text)

    def test_mentions_pyinstaller_onedir(self):
        self.assertIn("onedir", self.text_lower)


class TestPyprojectNotModified(unittest.TestCase):
    """pyproject.toml must not have been modified for PyInstaller."""

    def setUp(self):
        self.text = _read(_PYPROJECT)
        self.text_lower = self.text.lower()

    def test_no_pyinstaller_in_pyproject(self):
        self.assertNotIn("pyinstaller", self.text_lower)

    def test_no_pyinstaller_dependency(self):
        self.assertNotIn("PyInstaller", self.text)


class TestNoSpecFileExists(unittest.TestCase):
    """No PyInstaller spec file must exist in TASK-000045."""

    def test_no_spec_file_at_root(self):
        spec_files = list(_REPO.glob("*.spec"))
        self.assertEqual(
            spec_files,
            [],
            f"Unexpected .spec files found: {spec_files}",
        )

    def test_no_aurora_studio_spec(self):
        self.assertFalse(
            (_REPO / "aurora_studio.spec").exists(),
            "aurora_studio.spec must not be created by TASK-000045",
        )


class TestNoExeFileExists(unittest.TestCase):
    """No EXE file must exist in the repository from this task."""

    def test_no_exe_in_repo_root(self):
        exe_files = list(_REPO.glob("*.exe"))
        self.assertEqual(
            exe_files,
            [],
            f"Unexpected .exe files found: {exe_files}",
        )

    def test_no_dist_folder(self):
        dist_dir = _REPO / "dist"
        if dist_dir.exists():
            exe_files = list(dist_dir.rglob("*.exe"))
            self.assertEqual(
                exe_files,
                [],
                f"Unexpected .exe files found in dist/: {exe_files}",
            )

    def test_no_build_folder_exe(self):
        build_dir = _REPO / "build"
        if build_dir.exists():
            exe_files = list(build_dir.rglob("*.exe"))
            self.assertEqual(
                exe_files,
                [],
                f"Unexpected .exe files found in build/: {exe_files}",
            )


class TestNoBuildScriptsCreated(unittest.TestCase):
    """TASK-000045 must not create build scripts."""

    def test_no_build_windows_ps1(self):
        self.assertFalse(
            (_REPO / "scripts" / "build_windows.ps1").exists(),
            "build_windows.ps1 must not be created by TASK-000045",
        )

    def test_no_build_windows_bat(self):
        self.assertFalse(
            (_REPO / "scripts" / "build_windows.bat").exists(),
            "build_windows.bat must not be created by TASK-000045",
        )


class TestPlanningDocumentsAreReadable(unittest.TestCase):
    """All planning documents must be non-empty and UTF-8 readable."""

    def _assert_nonempty(self, path: pathlib.Path):
        text = _read(path)
        self.assertGreater(len(text.strip()), 100, f"Document too short: {path}")

    def test_exe_plan_nonempty(self):
        self._assert_nonempty(_EXE_PLAN)

    def test_folder_layout_nonempty(self):
        self._assert_nonempty(_FOLDER_LAYOUT)

    def test_risk_register_nonempty(self):
        self._assert_nonempty(_RISK_REGISTER)

    def test_future_boundary_nonempty(self):
        self._assert_nonempty(_FUTURE_BOUNDARY)


if __name__ == "__main__":
    unittest.main()

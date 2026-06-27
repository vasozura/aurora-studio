"""
tests/test_windows_portable_folder_pack.py

TASK-000047: Windows Portable Folder Pack
Tests for staging scripts, smoke scripts, templates, and documentation.

Rules:
- Standard-library unittest only
- No display required
- No PyInstaller required
- No built EXE required
- No ZIP files created
- No Windows required
- Actual staging only runs when AURORA_RUN_PORTABLE_STAGING=1
"""

import os
import pathlib
import unittest

_REPO = pathlib.Path(__file__).parent.parent
_SCRIPTS = _REPO / "scripts"
_DOCS_PKG = _REPO / "docs" / "packaging"
_TEMPLATES = _REPO / "packaging" / "portable"
_GITIGNORE = _REPO / ".gitignore"

_PS1_STAGE  = _SCRIPTS / "stage_windows_portable.ps1"
_BAT_STAGE  = _SCRIPTS / "stage_windows_portable.bat"
_PS1_SMOKE  = _SCRIPTS / "smoke_portable_folder.ps1"
_BAT_SMOKE  = _SCRIPTS / "smoke_portable_folder.bat"
_README_TPL = _TEMPLATES / "README.txt.template"
_NOTICE_TPL = _TEMPLATES / "NOTICE.txt.template"
_STAGING_DOC = _DOCS_PKG / "WINDOWS_PORTABLE_FOLDER_STAGING.md"

_VERSION      = "0.1.0"
_FOLDER_NAME  = f"AuroraStudio-v{_VERSION}-windows-portable"
_STAGED_PATH  = f"dist-portable/{_FOLDER_NAME}"
_STAGED_EXE   = f"{_STAGED_PATH}/app/AuroraStudio/AuroraStudio.exe"


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Stage scripts exist
# ---------------------------------------------------------------------------

class TestStageScriptsExist(unittest.TestCase):

    def test_ps1_stage_script_exists(self):
        self.assertTrue(_PS1_STAGE.is_file(), f"Missing: {_PS1_STAGE}")

    def test_bat_stage_script_exists(self):
        self.assertTrue(_BAT_STAGE.is_file(), f"Missing: {_BAT_STAGE}")


class TestStageScriptContent(unittest.TestCase):

    def test_ps1_references_dist_aurora_studio(self):
        text = _read(_PS1_STAGE)
        self.assertIn("dist\\AuroraStudio", text)

    def test_bat_references_dist_aurora_studio(self):
        text = _read(_BAT_STAGE)
        self.assertIn("dist\\AuroraStudio", text)

    def test_ps1_references_dist_portable_folder(self):
        text = _read(_PS1_STAGE)
        self.assertIn("dist-portable", text)
        # Scripts compose the folder name from variables; check component parts
        self.assertIn("windows-portable", text)

    def test_bat_references_dist_portable_folder(self):
        text = _read(_BAT_STAGE)
        self.assertIn("dist-portable", text)
        # Scripts compose the folder name from variables; check component parts
        self.assertIn("windows-portable", text)

    def test_ps1_does_not_create_zip(self):
        text = _read(_PS1_STAGE).lower()
        self.assertNotIn("compress-archive", text)
        self.assertNotIn(".zip", text)

    def test_bat_does_not_create_zip(self):
        text = _read(_BAT_STAGE).lower()
        self.assertNotIn(".zip", text)

    def test_ps1_does_not_auto_install(self):
        executable = "\n".join(
            ln for ln in _read(_PS1_STAGE).splitlines()
            if not ln.lstrip().startswith("#")
            and not ln.lstrip().lower().startswith("write-host")
        ).lower()
        self.assertNotIn("pip install", executable)

    def test_bat_does_not_auto_install(self):
        executable = "\n".join(
            ln for ln in _read(_BAT_STAGE).splitlines()
            if not ln.lstrip().startswith("::")
            and not ln.lstrip().lower().startswith("rem ")
            and not ln.lstrip().lower().startswith("echo")
        ).lower()
        self.assertNotIn("pip install", executable)

    def test_ps1_exits_nonzero_if_built_exe_missing(self):
        text = _read(_PS1_STAGE)
        self.assertIn("exit 1", text)

    def test_bat_exits_nonzero_if_built_exe_missing(self):
        text = _read(_BAT_STAGE)
        self.assertIn("exit /b 1", text)

    def test_ps1_uses_pscriptroot(self):
        text = _read(_PS1_STAGE)
        self.assertIn("PSScriptRoot", text)

    def test_bat_uses_dp0(self):
        text = _read(_BAT_STAGE)
        self.assertIn("%~dp0", text)

    def test_ps1_creates_data_logs_samples_tmp(self):
        text = _read(_PS1_STAGE)
        for folder in ("data", "logs", "samples", "tmp"):
            self.assertIn(folder, text, f"Missing folder '{folder}' in PS1 stage script")

    def test_bat_creates_data_logs_samples_tmp(self):
        text = _read(_BAT_STAGE)
        for folder in ("data", "logs", "samples", "tmp"):
            self.assertIn(folder, text, f"Missing folder '{folder}' in bat stage script")

    def test_ps1_copies_readme_and_notice(self):
        text = _read(_PS1_STAGE)
        self.assertIn("README", text)
        self.assertIn("NOTICE", text)

    def test_bat_copies_readme_and_notice(self):
        text = _read(_BAT_STAGE)
        self.assertIn("README", text)
        self.assertIn("NOTICE", text)

    def test_ps1_creates_run_desktop_bat(self):
        text = _read(_PS1_STAGE)
        self.assertIn("run_desktop.bat", text)

    def test_bat_creates_run_desktop_bat(self):
        text = _read(_BAT_STAGE)
        self.assertIn("run_desktop.bat", text)

    def test_ps1_creates_smoke_desktop_bat(self):
        text = _read(_PS1_STAGE)
        self.assertIn("smoke_desktop.bat", text)

    def test_bat_creates_smoke_desktop_bat(self):
        text = _read(_BAT_STAGE)
        self.assertIn("smoke_desktop.bat", text)


# ---------------------------------------------------------------------------
# Portable smoke scripts exist
# ---------------------------------------------------------------------------

class TestPortableSmokeScriptsExist(unittest.TestCase):

    def test_ps1_smoke_portable_exists(self):
        self.assertTrue(_PS1_SMOKE.is_file(), f"Missing: {_PS1_SMOKE}")

    def test_bat_smoke_portable_exists(self):
        self.assertTrue(_BAT_SMOKE.is_file(), f"Missing: {_BAT_SMOKE}")


class TestPortableSmokeScriptContent(unittest.TestCase):

    def test_ps1_references_staged_exe(self):
        text = _read(_PS1_SMOKE)
        self.assertIn("dist-portable", text)
        # Scripts compose the folder name from variables; check component parts
        self.assertIn("windows-portable", text)
        self.assertIn("AuroraStudio.exe", text)

    def test_bat_references_staged_exe(self):
        text = _read(_BAT_SMOKE)
        self.assertIn("dist-portable", text)
        # Scripts compose the folder name from variables; check component parts
        self.assertIn("windows-portable", text)
        self.assertIn("AuroraStudio.exe", text)

    def test_ps1_references_smoke_desktop_bat(self):
        text = _read(_PS1_SMOKE)
        self.assertIn("smoke_desktop.bat", text)

    def test_bat_references_smoke_desktop_bat(self):
        text = _read(_BAT_SMOKE)
        self.assertIn("smoke_desktop.bat", text)

    def test_ps1_exits_nonzero_if_staged_missing(self):
        text = _read(_PS1_SMOKE)
        self.assertIn("exit 1", text)

    def test_bat_exits_nonzero_if_staged_missing(self):
        text = _read(_BAT_SMOKE)
        self.assertIn("exit /b 1", text)

    def test_ps1_does_not_auto_install(self):
        executable = "\n".join(
            ln for ln in _read(_PS1_SMOKE).splitlines()
            if not ln.lstrip().startswith("#")
            and not ln.lstrip().lower().startswith("write-host")
        ).lower()
        self.assertNotIn("pip install", executable)

    def test_bat_does_not_auto_install(self):
        executable = "\n".join(
            ln for ln in _read(_BAT_SMOKE).splitlines()
            if not ln.lstrip().startswith("::")
            and not ln.lstrip().lower().startswith("rem ")
            and not ln.lstrip().lower().startswith("echo")
        ).lower()
        self.assertNotIn("pip install", executable)


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

class TestTemplatesExist(unittest.TestCase):

    def test_readme_template_exists(self):
        self.assertTrue(_README_TPL.is_file(), f"Missing: {_README_TPL}")

    def test_notice_template_exists(self):
        self.assertTrue(_NOTICE_TPL.is_file(), f"Missing: {_NOTICE_TPL}")


class TestReadmeTemplateContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_README_TPL)
        self.text_lower = self.text.lower()

    def test_mentions_aurora_studio(self):
        self.assertIn("Aurora Studio", self.text)

    def test_mentions_version(self):
        self.assertIn(_VERSION, self.text)

    def test_mentions_run_desktop_bat(self):
        self.assertIn("run_desktop.bat", self.text)

    def test_mentions_smoke_desktop_bat(self):
        self.assertIn("smoke_desktop.bat", self.text)

    def test_states_no_database(self):
        self.assertIn("no database", self.text_lower)

    def test_states_no_provider_integration(self):
        self.assertIn("no provider", self.text_lower)

    def test_states_no_plugin_execution(self):
        self.assertIn("no plugin", self.text_lower)

    def test_states_no_installer(self):
        self.assertIn("no installer", self.text_lower)

    def test_states_user_data_storage_advice(self):
        self.assertIn("outside", self.text_lower)

    def test_mentions_data_logs_samples_tmp(self):
        for folder in ("data", "logs", "samples", "tmp"):
            self.assertIn(folder, self.text_lower)


class TestNoticeTemplateContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_NOTICE_TPL)
        self.text_lower = self.text.lower()

    def test_mentions_aurora_studio(self):
        self.assertIn("Aurora Studio", self.text)

    def test_states_no_provider_keys(self):
        self.assertIn("no provider", self.text_lower)

    def test_states_no_plugin_execution(self):
        self.assertIn("no plugin", self.text_lower)

    def test_states_no_database(self):
        self.assertIn("no database", self.text_lower)

    def test_mentions_portable_build(self):
        self.assertIn("portable", self.text_lower)

    def test_has_no_warranty_notice(self):
        self.assertIn("no warranty", self.text_lower)

    def test_mentions_python_license(self):
        self.assertIn("python", self.text_lower)


# ---------------------------------------------------------------------------
# Documentation
# ---------------------------------------------------------------------------

class TestStagingDocExists(unittest.TestCase):

    def test_staging_doc_exists(self):
        self.assertTrue(_STAGING_DOC.is_file(), f"Missing: {_STAGING_DOC}")


class TestStagingDocContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_STAGING_DOC)
        self.text_lower = self.text.lower()

    def test_states_no_final_zip(self):
        self.assertIn("no final zip", self.text_lower)

    def test_states_no_installer(self):
        self.assertIn("no installer", self.text_lower)

    def test_states_no_provider_integration(self):
        self.assertIn("no provider", self.text_lower)

    def test_states_no_plugin_execution(self):
        self.assertIn("no plugin", self.text_lower)

    def test_states_staging_is_disposable(self):
        self.assertIn("disposable", self.text_lower)

    def test_mentions_stage_bat_command(self):
        self.assertIn("stage_windows_portable.bat", self.text)

    def test_mentions_stage_ps1_command(self):
        self.assertIn("stage_windows_portable.ps1", self.text)

    def test_mentions_smoke_bat_command(self):
        self.assertIn("smoke_portable_folder.bat", self.text)

    def test_mentions_smoke_ps1_command(self):
        self.assertIn("smoke_portable_folder.ps1", self.text)

    def test_mentions_build_bat_command(self):
        self.assertIn("build_windows_onefolder.bat", self.text)

    def test_mentions_expected_folder_layout(self):
        self.assertIn(_FOLDER_NAME, self.text)

    def test_has_prerequisites_section(self):
        self.assertIn("Prerequisites", self.text)

    def test_has_troubleshooting_section(self):
        self.assertIn("Troubleshooting", self.text)

    def test_has_future_zip_task_section(self):
        self.assertIn("Future", self.text)
        self.assertIn("ZIP", self.text)


# ---------------------------------------------------------------------------
# .gitignore covers dist-portable
# ---------------------------------------------------------------------------

class TestGitignoreCoversDistPortable(unittest.TestCase):

    def test_gitignore_ignores_dist_portable(self):
        if not _GITIGNORE.is_file():
            self.skipTest(".gitignore not found")
        text = _read(_GITIGNORE)
        self.assertIn("dist-portable", text,
                      ".gitignore must include dist-portable/")


# ---------------------------------------------------------------------------
# No ZIP artifacts created
# ---------------------------------------------------------------------------

class TestNoZipArtifacts(unittest.TestCase):

    def test_no_zip_at_repo_root(self):
        zips = list(_REPO.glob("*.zip"))
        self.assertEqual(zips, [], f"Unexpected ZIP files: {zips}")

    def test_no_zip_in_dist_portable(self):
        dist_portable = _REPO / "dist-portable"
        if dist_portable.exists():
            zips = list(dist_portable.rglob("*.zip"))
            self.assertEqual(zips, [], f"Unexpected ZIP files in dist-portable: {zips}")


# ---------------------------------------------------------------------------
# Optional gated staging test
# ---------------------------------------------------------------------------

@unittest.skipUnless(
    os.environ.get("AURORA_RUN_PORTABLE_STAGING") == "1",
    "Set AURORA_RUN_PORTABLE_STAGING=1 to run the actual staging",
)
class TestOptionalActualStaging(unittest.TestCase):
    """Runs actual staging. Skipped by default."""

    def test_staging_script_runs_successfully(self):
        import subprocess
        bat = _REPO / "scripts" / "stage_windows_portable.bat"
        if not bat.exists():
            self.skipTest("stage_windows_portable.bat not found")
        result = subprocess.run(
            [str(bat)],
            cwd=str(_REPO),
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode, 0,
            f"Staging failed:\n{result.stdout}\n{result.stderr}",
        )

    def test_staged_folder_exists_after_staging(self):
        staged = _REPO / "dist-portable" / _FOLDER_NAME
        self.assertTrue(staged.is_dir(), f"Staged folder not found: {staged}")

    def test_staged_exe_exists_after_staging(self):
        exe = _REPO / "dist-portable" / _FOLDER_NAME / "app" / "AuroraStudio" / "AuroraStudio.exe"
        self.assertTrue(exe.is_file(), f"Staged EXE not found: {exe}")

    def test_staged_readme_exists(self):
        readme = _REPO / "dist-portable" / _FOLDER_NAME / "README.txt"
        self.assertTrue(readme.is_file(), f"README.txt not found in staged folder")

    def test_staged_notice_exists(self):
        notice = _REPO / "dist-portable" / _FOLDER_NAME / "NOTICE.txt"
        self.assertTrue(notice.is_file(), f"NOTICE.txt not found in staged folder")

    def test_staged_data_logs_samples_tmp_exist(self):
        base = _REPO / "dist-portable" / _FOLDER_NAME
        for folder in ("data", "logs", "samples", "tmp"):
            self.assertTrue(
                (base / folder).is_dir(),
                f"Missing folder '{folder}' in staged portable",
            )

    def test_no_zip_created_by_staging(self):
        dist_portable = _REPO / "dist-portable"
        if dist_portable.exists():
            zips = list(dist_portable.rglob("*.zip"))
            self.assertEqual(zips, [], f"ZIP files must not be created: {zips}")


if __name__ == "__main__":
    unittest.main()

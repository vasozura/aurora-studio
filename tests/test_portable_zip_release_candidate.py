"""
tests/test_portable_zip_release_candidate.py

TASK-000048: Portable ZIP Release Candidate Pack
Tests for ZIP scripts, ZIP smoke scripts, documentation, and release notes.

Rules:
- Standard-library unittest only
- No display required
- No PyInstaller required
- No built EXE required
- No ZIP created by default
- No Windows required
- Actual ZIP creation only runs when AURORA_RUN_PORTABLE_ZIP=1
"""

import os
import pathlib
import unittest

_REPO = pathlib.Path(__file__).parent.parent
_SCRIPTS = _REPO / "scripts"
_DOCS_PKG = _REPO / "docs" / "packaging"
_RELEASE_NOTES = _REPO / "release-notes"
_GITIGNORE = _REPO / ".gitignore"

_PS1_ZIP       = _SCRIPTS / "create_portable_zip.ps1"
_BAT_ZIP       = _SCRIPTS / "create_portable_zip.bat"
_PS1_SMOKE_ZIP = _SCRIPTS / "smoke_portable_zip.ps1"
_BAT_SMOKE_ZIP = _SCRIPTS / "smoke_portable_zip.bat"
_ZIP_DOC       = _DOCS_PKG / "PORTABLE_ZIP_RELEASE_CANDIDATE.md"
_RC_NOTES      = _RELEASE_NOTES / "AuroraStudio-v0.1.0-rc1.md"

_VERSION       = "0.1.0"
_RC_TAG        = "rc1"
_FOLDER_NAME   = f"AuroraStudio-v{_VERSION}-windows-portable"
_ZIP_BASENAME  = f"AuroraStudio-v{_VERSION}-{_RC_TAG}-windows-portable"
_ZIP_NAME      = f"{_ZIP_BASENAME}.zip"
_SHA256_NAME   = f"{_ZIP_BASENAME}.sha256"


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# ZIP creation scripts exist
# ---------------------------------------------------------------------------

class TestZipScriptsExist(unittest.TestCase):

    def test_ps1_create_zip_exists(self):
        self.assertTrue(_PS1_ZIP.is_file(), f"Missing: {_PS1_ZIP}")

    def test_bat_create_zip_exists(self):
        self.assertTrue(_BAT_ZIP.is_file(), f"Missing: {_BAT_ZIP}")


class TestZipScriptContent(unittest.TestCase):

    def test_ps1_references_release_candidates_dir(self):
        self.assertIn("release-candidates", _read(_PS1_ZIP))

    def test_bat_references_release_candidates_dir(self):
        self.assertIn("release-candidates", _read(_BAT_ZIP))

    def test_ps1_references_zip_filename(self):
        text = _read(_PS1_ZIP)
        # PS1 composes the name from variables; check component parts
        self.assertIn("rc1", text)
        self.assertIn("windows-portable", text)
        self.assertIn(".zip", text)

    def test_bat_references_zip_filename(self):
        text = _read(_BAT_ZIP)
        # Bat uses variable composition; check component parts
        self.assertIn("rc1", text)
        self.assertIn("windows-portable", text)
        self.assertIn(".zip", text)

    def test_ps1_creates_checksum(self):
        text = _read(_PS1_ZIP).lower()
        self.assertIn("sha256", text)

    def test_bat_creates_checksum(self):
        text = _read(_BAT_ZIP).lower()
        self.assertIn("sha256", text)

    def test_ps1_uses_compress_archive(self):
        self.assertIn("Compress-Archive", _read(_PS1_ZIP))

    def test_bat_uses_powershell_for_zip(self):
        text = _read(_BAT_ZIP).lower()
        self.assertIn("powershell", text)

    def test_ps1_exits_nonzero_if_staged_missing(self):
        self.assertIn("exit 1", _read(_PS1_ZIP))

    def test_bat_exits_nonzero_if_staged_missing(self):
        self.assertIn("exit /b 1", _read(_BAT_ZIP))

    def test_ps1_does_not_auto_install(self):
        active = "\n".join(
            ln for ln in _read(_PS1_ZIP).splitlines()
            if not ln.lstrip().startswith("#")
            and not ln.lstrip().lower().startswith("write-host")
        ).lower()
        self.assertNotIn("pip install", active)

    def test_bat_does_not_auto_install(self):
        active = "\n".join(
            ln for ln in _read(_BAT_ZIP).splitlines()
            if not ln.lstrip().startswith("::")
            and not ln.lstrip().lower().startswith("rem ")
            and not ln.lstrip().lower().startswith("echo")
        ).lower()
        self.assertNotIn("pip install", active)

    def test_ps1_does_not_create_installer(self):
        text = _read(_PS1_ZIP).lower()
        self.assertNotIn("nsis", text)
        self.assertNotIn("wix", text)
        self.assertNotIn("msiexec", text)

    def test_ps1_uses_pscriptroot(self):
        self.assertIn("PSScriptRoot", _read(_PS1_ZIP))

    def test_bat_uses_dp0(self):
        self.assertIn("%~dp0", _read(_BAT_ZIP))


# ---------------------------------------------------------------------------
# ZIP smoke scripts exist
# ---------------------------------------------------------------------------

class TestZipSmokeScriptsExist(unittest.TestCase):

    def test_ps1_smoke_zip_exists(self):
        self.assertTrue(_PS1_SMOKE_ZIP.is_file(), f"Missing: {_PS1_SMOKE_ZIP}")

    def test_bat_smoke_zip_exists(self):
        self.assertTrue(_BAT_SMOKE_ZIP.is_file(), f"Missing: {_BAT_SMOKE_ZIP}")


class TestZipSmokeScriptContent(unittest.TestCase):

    def test_ps1_verifies_checksum(self):
        text = _read(_PS1_SMOKE_ZIP).lower()
        self.assertIn("sha256", text)
        self.assertIn("hash", text)

    def test_bat_verifies_checksum(self):
        text = _read(_BAT_SMOKE_ZIP).lower()
        self.assertIn("sha256", text)

    def test_ps1_extracts_to_smoke_folder(self):
        text = _read(_PS1_SMOKE_ZIP)
        self.assertIn("_smoke", text)
        self.assertIn("Expand-Archive", text)

    def test_bat_extracts_to_smoke_folder(self):
        text = _read(_BAT_SMOKE_ZIP)
        self.assertIn("_smoke", text)

    def test_ps1_verifies_layout(self):
        text = _read(_PS1_SMOKE_ZIP)
        for item in ("run_desktop.bat", "smoke_desktop.bat", "README.txt", "NOTICE.txt"):
            self.assertIn(item, text, f"Missing layout check for '{item}'")

    def test_bat_verifies_layout(self):
        text = _read(_BAT_SMOKE_ZIP)
        for item in ("run_desktop.bat", "smoke_desktop.bat", "README.txt", "NOTICE.txt"):
            self.assertIn(item, text, f"Missing layout check for '{item}'")

    def test_ps1_does_not_open_gui_directly(self):
        # Smoke script must not call the EXE directly without --headless-smoke
        # It delegates to smoke_desktop.bat which contains --headless-smoke
        text = _read(_PS1_SMOKE_ZIP)
        self.assertIn("smoke_desktop.bat", text)

    def test_bat_does_not_open_gui_directly(self):
        text = _read(_BAT_SMOKE_ZIP)
        self.assertIn("smoke_desktop.bat", text)

    def test_ps1_cleans_smoke_folder(self):
        text = _read(_PS1_SMOKE_ZIP).lower()
        self.assertIn("remove-item", text)

    def test_bat_cleans_smoke_folder(self):
        text = _read(_BAT_SMOKE_ZIP).lower()
        self.assertIn("rmdir", text)

    def test_ps1_exits_nonzero_on_failure(self):
        self.assertIn("exit 1", _read(_PS1_SMOKE_ZIP))

    def test_bat_exits_nonzero_on_failure(self):
        self.assertIn("exit /b 1", _read(_BAT_SMOKE_ZIP))

    def test_ps1_references_zip_in_release_candidates(self):
        text = _read(_PS1_SMOKE_ZIP)
        self.assertIn("release-candidates", text)

    def test_bat_references_zip_in_release_candidates(self):
        text = _read(_BAT_SMOKE_ZIP)
        self.assertIn("release-candidates", text)


# ---------------------------------------------------------------------------
# Documentation
# ---------------------------------------------------------------------------

class TestZipDocExists(unittest.TestCase):

    def test_zip_doc_exists(self):
        self.assertTrue(_ZIP_DOC.is_file(), f"Missing: {_ZIP_DOC}")


class TestZipDocContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_ZIP_DOC)
        self.text_lower = self.text.lower()

    def test_states_release_candidate_not_final(self):
        self.assertIn("release candidate", self.text_lower)
        self.assertIn("not a final release", self.text_lower)

    def test_states_no_installer(self):
        self.assertIn("no installer", self.text_lower)

    def test_states_no_provider_integration(self):
        self.assertIn("no provider", self.text_lower)

    def test_states_no_plugin_execution(self):
        self.assertIn("no plugin", self.text_lower)

    def test_states_zip_is_disposable(self):
        self.assertIn("disposable", self.text_lower)

    def test_mentions_create_zip_bat(self):
        self.assertIn("create_portable_zip.bat", self.text)

    def test_mentions_create_zip_ps1(self):
        self.assertIn("create_portable_zip.ps1", self.text)

    def test_mentions_smoke_zip_bat(self):
        self.assertIn("smoke_portable_zip.bat", self.text)

    def test_mentions_smoke_zip_ps1(self):
        self.assertIn("smoke_portable_zip.ps1", self.text)

    def test_mentions_stage_bat(self):
        self.assertIn("stage_windows_portable.bat", self.text)

    def test_mentions_build_bat(self):
        self.assertIn("build_windows_onefolder.bat", self.text)

    def test_has_prerequisites_section(self):
        self.assertIn("Prerequisites", self.text)

    def test_has_troubleshooting_section(self):
        self.assertIn("Troubleshooting", self.text)

    def test_has_future_release_section(self):
        self.assertIn("Future", self.text)

    def test_mentions_sha256(self):
        self.assertIn("sha256", self.text_lower)

    def test_mentions_expected_zip_name(self):
        # Version and rc tag are in the doc
        self.assertIn(_VERSION, self.text)
        self.assertIn(_RC_TAG, self.text)


# ---------------------------------------------------------------------------
# Release notes
# ---------------------------------------------------------------------------

class TestReleaseNotesExist(unittest.TestCase):

    def test_rc1_release_notes_exist(self):
        self.assertTrue(_RC_NOTES.is_file(), f"Missing: {_RC_NOTES}")


class TestReleaseNotesContent(unittest.TestCase):

    def setUp(self):
        self.text = _read(_RC_NOTES)
        self.text_lower = self.text.lower()

    def test_states_no_production_readiness(self):
        self.assertIn("no production readiness", self.text_lower)

    def test_states_no_final_release(self):
        self.assertIn("not a final release", self.text_lower)

    def test_mentions_local_desktop_shell(self):
        self.assertIn("desktop shell", self.text_lower)

    def test_mentions_project_create_open(self):
        self.assertIn("project", self.text_lower)

    def test_mentions_scene_shot(self):
        self.assertIn("scene", self.text_lower)
        self.assertIn("shot", self.text_lower)

    def test_mentions_timeline_asset_character(self):
        self.assertIn("timeline", self.text_lower)
        self.assertIn("asset", self.text_lower)
        self.assertIn("character", self.text_lower)

    def test_mentions_afl_export_plugin(self):
        self.assertIn("afl", self.text_lower)
        self.assertIn("export", self.text_lower)
        self.assertIn("plugin", self.text_lower)

    def test_mentions_bundle_rehydration(self):
        self.assertIn("rehydrat", self.text_lower)

    def test_mentions_cli_smoke(self):
        self.assertIn("cli", self.text_lower)

    def test_mentions_windows_portable(self):
        self.assertIn("windows portable", self.text_lower)

    def test_states_no_installer(self):
        self.assertIn("no installer", self.text_lower)

    def test_states_no_database(self):
        self.assertIn("no database", self.text_lower)

    def test_states_no_provider_integration(self):
        self.assertIn("no provider", self.text_lower)

    def test_states_no_plugin_execution(self):
        self.assertIn("no plugin", self.text_lower)

    def test_states_no_afl_semantic_validation(self):
        self.assertIn("no real afl", self.text_lower)

    def test_has_validation_checklist(self):
        self.assertIn("Validation Checklist", self.text)

    def test_has_known_limitations(self):
        self.assertIn("Known Limitations", self.text)


# ---------------------------------------------------------------------------
# .gitignore covers release-candidates
# ---------------------------------------------------------------------------

class TestGitignoreCoversReleaseCandidates(unittest.TestCase):

    def test_gitignore_ignores_release_candidates(self):
        if not _GITIGNORE.is_file():
            self.skipTest(".gitignore not found")
        text = _read(_GITIGNORE)
        self.assertIn("release-candidates", text)


# ---------------------------------------------------------------------------
# No ZIP at repo root / no installer
# ---------------------------------------------------------------------------

class TestNoZipAtRoot(unittest.TestCase):

    def test_no_zip_at_repo_root(self):
        zips = list(_REPO.glob("*.zip"))
        self.assertEqual(zips, [], f"Unexpected ZIP at root: {zips}")


# ---------------------------------------------------------------------------
# Optional gated ZIP creation test
# ---------------------------------------------------------------------------

@unittest.skipUnless(
    os.environ.get("AURORA_RUN_PORTABLE_ZIP") == "1",
    "Set AURORA_RUN_PORTABLE_ZIP=1 to run the actual ZIP creation",
)
class TestOptionalActualZipCreation(unittest.TestCase):
    """Runs actual ZIP creation and smoke. Skipped by default."""

    def test_create_zip_script_runs(self):
        import subprocess
        bat = _REPO / "scripts" / "create_portable_zip.bat"
        if not bat.exists():
            self.skipTest("create_portable_zip.bat not found")
        result = subprocess.run([str(bat)], cwd=str(_REPO), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0,
                         f"ZIP creation failed:\n{result.stdout}\n{result.stderr}")

    def test_zip_artifact_exists_after_creation(self):
        zip_path = _REPO / "release-candidates" / _ZIP_NAME
        self.assertTrue(zip_path.is_file(), f"ZIP not found: {zip_path}")

    def test_sha256_artifact_exists_after_creation(self):
        sha_path = _REPO / "release-candidates" / _SHA256_NAME
        self.assertTrue(sha_path.is_file(), f"SHA256 not found: {sha_path}")

    def test_smoke_zip_script_runs(self):
        import subprocess
        bat = _REPO / "scripts" / "smoke_portable_zip.bat"
        if not bat.exists():
            self.skipTest("smoke_portable_zip.bat not found")
        result = subprocess.run([str(bat)], cwd=str(_REPO), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0,
                         f"ZIP smoke failed:\n{result.stdout}\n{result.stderr}")


if __name__ == "__main__":
    unittest.main()

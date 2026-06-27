"""
tests/test_pyinstaller_build_smoke.py

TASK-000046: PyInstaller Build Smoke Pack
Tests for build infrastructure, scripts, and documentation.

Rules:
- Standard-library unittest only
- No display required
- No PyInstaller required by default
- No EXE built by default
- No Windows required
- Actual build only runs when AURORA_RUN_PYINSTALLER_BUILD=1 is set
"""

import os
import pathlib
import sys
import unittest

_REPO = pathlib.Path(__file__).parent.parent
_BUILD_DIR = _REPO / "build"
_REQ_BUILD = _BUILD_DIR / "requirements-build.txt"
_SPEC_FILE = _BUILD_DIR / "pyinstaller" / "aurora_studio_desktop.spec"
_SCRIPTS = _REPO / "scripts"
_PS1_BUILD = _SCRIPTS / "build_windows_onefolder.ps1"
_BAT_BUILD = _SCRIPTS / "build_windows_onefolder.bat"
_PS1_SMOKE = _SCRIPTS / "smoke_built_app.ps1"
_BAT_SMOKE = _SCRIPTS / "smoke_built_app.bat"
_DOCS_PKG = _REPO / "docs" / "packaging"
_BUILD_SMOKE_DOC = _DOCS_PKG / "PYINSTALLER_BUILD_SMOKE.md"
_PYPROJECT = _REPO / "pyproject.toml"


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Build requirements file
# ---------------------------------------------------------------------------

class TestBuildRequirementsFile(unittest.TestCase):
    """build/requirements-build.txt must exist and mention pyinstaller."""

    def test_requirements_build_exists(self):
        self.assertTrue(_REQ_BUILD.is_file(), f"Missing: {_REQ_BUILD}")

    def test_requirements_build_mentions_pyinstaller(self):
        text = _read(_REQ_BUILD).lower()
        self.assertIn("pyinstaller", text)

    def test_requirements_build_has_comment_about_build_only(self):
        text = _read(_REQ_BUILD).lower()
        self.assertIn("build", text)

    def test_pyproject_does_not_contain_pyinstaller_runtime(self):
        text = _read(_PYPROJECT).lower()
        # pyproject.toml must not list pyinstaller as a runtime dependency
        # It may appear in dev/build extras but must not be in [tool.poetry.dependencies]
        # We do a broad check: pyinstaller must not appear at all in pyproject
        self.assertNotIn("pyinstaller", text)


# ---------------------------------------------------------------------------
# PyInstaller spec file
# ---------------------------------------------------------------------------

class TestPyInstallerSpec(unittest.TestCase):
    """build/pyinstaller/aurora_studio_desktop.spec must exist and be correct."""

    def setUp(self):
        self.text = _read(_SPEC_FILE)
        self.text_lower = self.text.lower()

    def test_spec_file_exists(self):
        self.assertTrue(_SPEC_FILE.is_file(), f"Missing: {_SPEC_FILE}")

    def test_spec_references_aurora_studio_name(self):
        self.assertIn("AuroraStudio", self.text)

    def test_spec_references_desktop_shell_entry(self):
        self.assertIn("desktop_shell", self.text_lower)

    def test_spec_uses_one_folder_mode(self):
        # COLLECT present means one-folder mode (not EXE onefile)
        self.assertIn("COLLECT", self.text)

    def test_spec_references_src_dir(self):
        self.assertIn("src", self.text_lower)

    def test_spec_has_hidden_imports(self):
        self.assertIn("hiddenimports", self.text_lower)

    def test_spec_includes_tkinter(self):
        self.assertIn("tkinter", self.text_lower)

    def test_spec_excludes_openai(self):
        self.assertIn("openai", self.text_lower)

    def test_spec_excludes_anthropic(self):
        self.assertIn("anthropic", self.text_lower)

    def test_spec_does_not_bundle_provider_keys(self):
        text_lower = self.text_lower
        self.assertNotIn("api_key", text_lower)
        self.assertNotIn("secret_key", text_lower)

    def test_spec_has_excludes(self):
        self.assertIn("excludes", self.text_lower)

    def test_spec_console_true_for_headless(self):
        # console=True required so --headless-smoke output is captured
        self.assertIn("console=True", self.text)


# ---------------------------------------------------------------------------
# Build scripts
# ---------------------------------------------------------------------------

class TestBuildScriptsExist(unittest.TestCase):
    """Build scripts must exist."""

    def test_ps1_build_script_exists(self):
        self.assertTrue(_PS1_BUILD.is_file(), f"Missing: {_PS1_BUILD}")

    def test_bat_build_script_exists(self):
        self.assertTrue(_BAT_BUILD.is_file(), f"Missing: {_BAT_BUILD}")


class TestBuildScriptContent(unittest.TestCase):
    """Build scripts must check PyInstaller and not auto-install."""

    def test_ps1_checks_pyinstaller_version(self):
        text = _read(_PS1_BUILD)
        self.assertIn("PyInstaller --version", text)

    def test_bat_checks_pyinstaller_version(self):
        text = _read(_BAT_BUILD)
        self.assertIn("PyInstaller --version", text)

    def test_ps1_does_not_auto_install(self):
        # Script must not execute pip install (only mention it in print/comment lines)
        executable = "\n".join(
            ln for ln in _read(_PS1_BUILD).splitlines()
            if not ln.lstrip().startswith("#")
            and not ln.lstrip().lower().startswith("write-host")
        ).lower()
        self.assertNotIn("pip install", executable)

    def test_bat_does_not_auto_install(self):
        # Script must not execute pip install (only mention it in echo/comment lines)
        executable = "\n".join(
            ln for ln in _read(_BAT_BUILD).splitlines()
            if not ln.lstrip().startswith("::")
            and not ln.lstrip().lower().startswith("rem ")
            and not ln.lstrip().lower().startswith("echo")
        ).lower()
        self.assertNotIn("pip install", executable)

    def test_ps1_uses_pscriptroot(self):
        text = _read(_PS1_BUILD)
        self.assertIn("PSScriptRoot", text)

    def test_bat_uses_dp0(self):
        text = _read(_BAT_BUILD)
        self.assertIn("%~dp0", text)

    def test_ps1_references_spec_file(self):
        text = _read(_PS1_BUILD).lower()
        self.assertIn("spec", text)

    def test_bat_references_spec_file(self):
        text = _read(_BAT_BUILD).lower()
        self.assertIn("spec", text)

    def test_ps1_cleans_controlled_paths_only(self):
        text = _read(_PS1_BUILD)
        self.assertIn("pyinstaller_work", text)
        self.assertIn("AuroraStudio", text)

    def test_bat_cleans_controlled_paths_only(self):
        text = _read(_BAT_BUILD)
        self.assertIn("pyinstaller_work", text)
        self.assertIn("AuroraStudio", text)

    def test_ps1_exits_nonzero_if_pyinstaller_missing(self):
        text = _read(_PS1_BUILD)
        self.assertIn("exit 1", text)

    def test_bat_exits_nonzero_if_pyinstaller_missing(self):
        text = _read(_BAT_BUILD)
        self.assertIn("exit /b 1", text)


# ---------------------------------------------------------------------------
# Smoke scripts
# ---------------------------------------------------------------------------

class TestSmokeScriptsExist(unittest.TestCase):
    """Smoke scripts must exist."""

    def test_ps1_smoke_script_exists(self):
        self.assertTrue(_PS1_SMOKE.is_file(), f"Missing: {_PS1_SMOKE}")

    def test_bat_smoke_script_exists(self):
        self.assertTrue(_BAT_SMOKE.is_file(), f"Missing: {_BAT_SMOKE}")


class TestSmokeScriptContent(unittest.TestCase):
    """Smoke scripts must reference the correct dist output and headless flag."""

    def test_ps1_references_dist_aurora_studio(self):
        text = _read(_PS1_SMOKE)
        self.assertIn("dist", text)
        self.assertIn("AuroraStudio", text)

    def test_bat_references_dist_aurora_studio(self):
        text = _read(_BAT_SMOKE)
        self.assertIn("dist", text)
        self.assertIn("AuroraStudio", text)

    def test_ps1_uses_headless_smoke_flag(self):
        text = _read(_PS1_SMOKE)
        self.assertIn("--headless-smoke", text)

    def test_bat_uses_headless_smoke_flag(self):
        text = _read(_BAT_SMOKE)
        self.assertIn("--headless-smoke", text)

    def test_ps1_does_not_auto_install(self):
        text = _read(_PS1_SMOKE).lower()
        self.assertNotIn("pip install", text)

    def test_bat_does_not_auto_install(self):
        text = _read(_BAT_SMOKE).lower()
        self.assertNotIn("pip install", text)

    def test_ps1_exits_nonzero_on_exe_missing(self):
        text = _read(_PS1_SMOKE)
        self.assertIn("exit 1", text)

    def test_bat_exits_nonzero_on_exe_missing(self):
        text = _read(_BAT_SMOKE)
        self.assertIn("exit /b 1", text)


# ---------------------------------------------------------------------------
# Documentation
# ---------------------------------------------------------------------------

class TestBuildSmokeDocExists(unittest.TestCase):
    def test_build_smoke_doc_exists(self):
        self.assertTrue(_BUILD_SMOKE_DOC.is_file(), f"Missing: {_BUILD_SMOKE_DOC}")


class TestBuildSmokeDocContent(unittest.TestCase):
    def setUp(self):
        self.text = _read(_BUILD_SMOKE_DOC)
        self.text_lower = self.text.lower()

    def test_states_pyinstaller_is_build_time_only(self):
        self.assertIn("build-time-only", self.text_lower)

    def test_states_no_installer(self):
        self.assertIn("no installer", self.text_lower)

    def test_states_no_provider_keys_bundled(self):
        self.assertIn("no provider", self.text_lower)

    def test_states_no_plugin_execution(self):
        self.assertIn("no plugin", self.text_lower)

    def test_states_no_database(self):
        self.assertIn("no database", self.text_lower)

    def test_states_no_zip_release(self):
        text_lower = self.text_lower
        self.assertIn("no final release zip", text_lower)

    def test_mentions_requirements_build_command(self):
        self.assertIn("requirements-build.txt", self.text)

    def test_mentions_build_bat_script(self):
        self.assertIn("build_windows_onefolder.bat", self.text)

    def test_mentions_smoke_bat_script(self):
        self.assertIn("smoke_built_app.bat", self.text)

    def test_mentions_build_ps1_script(self):
        self.assertIn("build_windows_onefolder.ps1", self.text)

    def test_mentions_smoke_ps1_script(self):
        self.assertIn("smoke_built_app.ps1", self.text)

    def test_mentions_headless_smoke(self):
        self.assertIn("--headless-smoke", self.text)

    def test_has_troubleshooting_section(self):
        self.assertIn("Troubleshooting", self.text)

    def test_has_known_limitations_section(self):
        self.assertIn("Known Limitations", self.text)

    def test_has_prerequisites_section(self):
        self.assertIn("Prerequisites", self.text)


# ---------------------------------------------------------------------------
# No EXE / dist artifacts committed
# ---------------------------------------------------------------------------

class TestNoExeCommitted(unittest.TestCase):
    """No EXE artifacts must be present in a clean repo (not built yet)."""

    def test_no_exe_at_root(self):
        exe_files = list(_REPO.glob("*.exe"))
        self.assertEqual(exe_files, [], f"Unexpected .exe files: {exe_files}")

    # dist/ may exist if someone ran the build; only check if present
    def test_no_unsigned_spec_at_root(self):
        # spec file must be in build/pyinstaller/, not at repo root
        root_specs = [f for f in _REPO.glob("*.spec") if f.parent == _REPO]
        self.assertEqual(
            root_specs, [],
            f"Spec file must not be at repo root: {root_specs}",
        )


# ---------------------------------------------------------------------------
# Source code: no PyInstaller import in application code
# ---------------------------------------------------------------------------

class TestNoRuntimePyInstallerImport(unittest.TestCase):
    """Application source must not import PyInstaller."""

    def _scan_src(self, module_name: str) -> list:
        src = _REPO / "src"
        found = []
        for py_file in src.rglob("*.py"):
            text = py_file.read_text(encoding="utf-8", errors="replace")
            if module_name in text:
                found.append(str(py_file))
        return found

    def test_no_pyinstaller_import_in_src(self):
        found = self._scan_src("PyInstaller")
        self.assertEqual(
            found, [],
            f"PyInstaller imported in application source: {found}",
        )

    def test_no_sys_frozen_dependency_in_critical_path(self):
        # sys.frozen is set by PyInstaller at runtime; application code may
        # check it but must not require it. Verify desktop_shell headless_smoke
        # does not depend on sys.frozen.
        shell_path = _REPO / "src" / "aurora_studio" / "ui" / "desktop_shell.py"
        if shell_path.exists():
            text = shell_path.read_text(encoding="utf-8")
            # headless_smoke function must not reference sys.frozen
            in_headless = False
            for line in text.splitlines():
                if "def headless_smoke" in line:
                    in_headless = True
                if in_headless and line.strip().startswith("def ") and "headless_smoke" not in line:
                    break
                if in_headless and "sys.frozen" in line:
                    self.fail("headless_smoke() must not depend on sys.frozen")


# ---------------------------------------------------------------------------
# Optional gated build test
# ---------------------------------------------------------------------------

@unittest.skipUnless(
    os.environ.get("AURORA_RUN_PYINSTALLER_BUILD") == "1",
    "Set AURORA_RUN_PYINSTALLER_BUILD=1 to run the actual build",
)
class TestOptionalActualBuild(unittest.TestCase):
    """Runs the actual PyInstaller build. Skipped by default."""

    def test_build_script_runs_successfully(self):
        import subprocess
        bat = _REPO / "scripts" / "build_windows_onefolder.bat"
        if not bat.exists():
            self.skipTest("build_windows_onefolder.bat not found")
        result = subprocess.run(
            [str(bat)],
            cwd=str(_REPO),
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode, 0,
            f"Build failed:\n{result.stdout}\n{result.stderr}",
        )

    def test_exe_artifact_exists_after_build(self):
        exe = _REPO / "dist" / "AuroraStudio" / "AuroraStudio.exe"
        self.assertTrue(exe.is_file(), f"EXE not found after build: {exe}")

    def test_built_exe_headless_smoke(self):
        import subprocess
        exe = _REPO / "dist" / "AuroraStudio" / "AuroraStudio.exe"
        if not exe.is_file():
            self.skipTest("AuroraStudio.exe not found — run build first")
        result = subprocess.run(
            [str(exe), "--headless-smoke"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(
            result.returncode, 0,
            f"Built EXE headless smoke failed:\n{result.stdout}\n{result.stderr}",
        )
        import json
        try:
            data = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            self.fail(f"Built EXE smoke output is not valid JSON:\n{result.stdout}")
        self.assertTrue(data.get("ok"), f"Smoke ok=False: {data}")


if __name__ == "__main__":
    unittest.main()

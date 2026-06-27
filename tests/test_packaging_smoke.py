"""Tests for TASK-000044: Packaging Smoke.

Verifies that scripts exist, contain expected content, README is complete,
and headless Python commands work via subprocess.

No display required. No Windows required. No PowerShell required.
"""

import json
import os
import pathlib
import subprocess
import sys
import unittest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO = pathlib.Path(__file__).parent.parent
_SCRIPTS = _REPO / "scripts"
_README = _REPO / "README.md"
_SRC = str(_REPO / "src")

_ENV = {**os.environ, "PYTHONPATH": _SRC}


# ---------------------------------------------------------------------------
# 1. Script files exist
# ---------------------------------------------------------------------------

class TestScriptFilesExist(unittest.TestCase):

    def _exists(self, name: str) -> None:
        p = _SCRIPTS / name
        self.assertTrue(p.exists(), f"Missing: scripts/{name}")

    def test_run_desktop_ps1(self) -> None:
        self._exists("run_desktop.ps1")

    def test_run_desktop_bat(self) -> None:
        self._exists("run_desktop.bat")

    def test_run_tests_ps1(self) -> None:
        self._exists("run_tests.ps1")

    def test_run_tests_bat(self) -> None:
        self._exists("run_tests.bat")

    def test_smoke_desktop_ps1(self) -> None:
        self._exists("smoke_desktop.ps1")

    def test_smoke_desktop_bat(self) -> None:
        self._exists("smoke_desktop.bat")


# ---------------------------------------------------------------------------
# 2. PowerShell script content
# ---------------------------------------------------------------------------

class TestPowerShellScriptContent(unittest.TestCase):

    def _read(self, name: str) -> str:
        return (_SCRIPTS / name).read_text(encoding="utf-8")

    def test_run_desktop_ps1_has_module(self) -> None:
        content = self._read("run_desktop.ps1")
        self.assertIn("aurora_studio.ui.desktop_shell", content)

    def test_run_desktop_ps1_sets_pythonpath(self) -> None:
        content = self._read("run_desktop.ps1")
        self.assertIn("PYTHONPATH", content)

    def test_run_desktop_ps1_uses_psscrootroot(self) -> None:
        content = self._read("run_desktop.ps1")
        self.assertIn("PSScriptRoot", content)

    def test_run_desktop_ps1_no_pip(self) -> None:
        self.assertNotIn("pip install", self._read("run_desktop.ps1"))

    def test_run_tests_ps1_has_unittest(self) -> None:
        content = self._read("run_tests.ps1")
        self.assertIn("unittest", content)

    def test_run_tests_ps1_sets_pythonpath(self) -> None:
        self.assertIn("PYTHONPATH", self._read("run_tests.ps1"))

    def test_run_tests_ps1_no_pip(self) -> None:
        self.assertNotIn("pip install", self._read("run_tests.ps1"))

    def test_smoke_ps1_has_headless_smoke(self) -> None:
        content = self._read("smoke_desktop.ps1")
        self.assertIn("headless-smoke", content)

    def test_smoke_ps1_has_create_demo(self) -> None:
        content = self._read("smoke_desktop.ps1")
        self.assertIn("create-demo", content)

    def test_smoke_ps1_has_validate_bundle(self) -> None:
        content = self._read("smoke_desktop.ps1")
        self.assertIn("validate-bundle", content)

    def test_smoke_ps1_has_rehydrate_bundle(self) -> None:
        content = self._read("smoke_desktop.ps1")
        self.assertIn("rehydrate-bundle", content)

    def test_smoke_ps1_cleans_demo_project(self) -> None:
        content = self._read("smoke_desktop.ps1")
        self.assertIn("tmp-demo-project", content)
        self.assertIn("Remove-Item", content)

    def test_smoke_ps1_no_pip(self) -> None:
        self.assertNotIn("pip install", self._read("smoke_desktop.ps1"))


# ---------------------------------------------------------------------------
# 3. Batch script content
# ---------------------------------------------------------------------------

class TestBatchScriptContent(unittest.TestCase):

    def _read(self, name: str) -> str:
        return (_SCRIPTS / name).read_text(encoding="utf-8")

    def test_run_desktop_bat_has_module(self) -> None:
        self.assertIn("aurora_studio.ui.desktop_shell", self._read("run_desktop.bat"))

    def test_run_desktop_bat_sets_pythonpath(self) -> None:
        self.assertIn("PYTHONPATH", self._read("run_desktop.bat"))

    def test_run_desktop_bat_uses_dp0(self) -> None:
        content = self._read("run_desktop.bat")
        self.assertIn("%~dp0", content)

    def test_run_desktop_bat_no_pip(self) -> None:
        self.assertNotIn("pip install", self._read("run_desktop.bat"))

    def test_run_tests_bat_has_unittest(self) -> None:
        self.assertIn("unittest", self._read("run_tests.bat"))

    def test_run_tests_bat_sets_pythonpath(self) -> None:
        self.assertIn("PYTHONPATH", self._read("run_tests.bat"))

    def test_run_tests_bat_no_pip(self) -> None:
        self.assertNotIn("pip install", self._read("run_tests.bat"))

    def test_smoke_bat_has_headless_smoke(self) -> None:
        self.assertIn("headless-smoke", self._read("smoke_desktop.bat"))

    def test_smoke_bat_has_create_demo(self) -> None:
        self.assertIn("create-demo", self._read("smoke_desktop.bat"))

    def test_smoke_bat_has_validate_bundle(self) -> None:
        self.assertIn("validate-bundle", self._read("smoke_desktop.bat"))

    def test_smoke_bat_has_rehydrate_bundle(self) -> None:
        self.assertIn("rehydrate-bundle", self._read("smoke_desktop.bat"))

    def test_smoke_bat_cleans_demo_project(self) -> None:
        content = self._read("smoke_desktop.bat")
        self.assertIn("tmp-demo-project", content)
        self.assertIn("rmdir", content)

    def test_smoke_bat_no_pip(self) -> None:
        self.assertNotIn("pip install", self._read("smoke_desktop.bat"))


# ---------------------------------------------------------------------------
# 4. README content
# ---------------------------------------------------------------------------

class TestREADMEContent(unittest.TestCase):

    def setUp(self) -> None:
        self._content = _README.read_text(encoding="utf-8")

    def test_readme_exists(self) -> None:
        self.assertTrue(_README.exists())

    def test_readme_has_run_tests_command(self) -> None:
        self.assertIn("python -m unittest", self._content)

    def test_readme_has_headless_smoke_command(self) -> None:
        self.assertIn("--headless-smoke", self._content)

    def test_readme_has_desktop_shell_command(self) -> None:
        self.assertIn("aurora_studio.ui.desktop_shell", self._content)

    def test_readme_has_cli_smoke_command(self) -> None:
        self.assertIn("aurora_studio.cli", self._content)
        self.assertIn("smoke", self._content)

    def test_readme_has_create_demo(self) -> None:
        self.assertIn("create-demo", self._content)

    def test_readme_has_validate_bundle(self) -> None:
        self.assertIn("validate-bundle", self._content)

    def test_readme_has_rehydrate_bundle(self) -> None:
        self.assertIn("rehydrate-bundle", self._content)

    def test_readme_mentions_run_tests_bat(self) -> None:
        self.assertIn("run_tests.bat", self._content)

    def test_readme_mentions_run_desktop_bat(self) -> None:
        self.assertIn("run_desktop.bat", self._content)

    def test_readme_mentions_smoke_desktop_bat(self) -> None:
        self.assertIn("smoke_desktop.bat", self._content)

    def test_readme_mentions_run_tests_ps1(self) -> None:
        self.assertIn("run_tests.ps1", self._content)

    def test_readme_mentions_run_desktop_ps1(self) -> None:
        self.assertIn("run_desktop.ps1", self._content)

    def test_readme_mentions_smoke_desktop_ps1(self) -> None:
        self.assertIn("smoke_desktop.ps1", self._content)

    def test_readme_states_no_external_dependencies(self) -> None:
        lower = self._content.lower()
        self.assertTrue(
            "no external" in lower or "standard library only" in lower,
            "README must state no external dependencies")

    def test_readme_states_no_database(self) -> None:
        lower = self._content.lower()
        self.assertTrue(
            "no database" in lower or "not yet" in lower,
            "README must mention database limitation")

    def test_readme_states_no_provider(self) -> None:
        lower = self._content.lower()
        self.assertIn("provider", lower)

    def test_readme_states_no_plugin_execution(self) -> None:
        lower = self._content.lower()
        self.assertIn("plugin", lower)

    def test_readme_mentions_tkinter(self) -> None:
        self.assertIn("tkinter", self._content)

    def test_readme_not_production_ready(self) -> None:
        lower = self._content.lower()
        self.assertTrue(
            "not production" in lower or "not a final" in lower or "not production-ready" in lower,
            "README must disclaim production readiness")


# ---------------------------------------------------------------------------
# 5. Subprocess smoke — headless desktop
# ---------------------------------------------------------------------------

class TestSubprocessHeadlessSmoke(unittest.TestCase):

    def _run(self, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_ENV,
            cwd=str(_REPO),
        )

    def test_headless_smoke_exit_zero(self) -> None:
        result = self._run("-m", "aurora_studio.ui.desktop_shell", "--headless-smoke")
        self.assertEqual(result.returncode, 0,
                         f"Non-zero exit.\nstdout: {result.stdout}\nstderr: {result.stderr}")

    def test_headless_smoke_outputs_json(self) -> None:
        result = self._run("-m", "aurora_studio.ui.desktop_shell", "--headless-smoke")
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(f"Output is not valid JSON:\n{result.stdout}")
        self.assertIsInstance(data, dict)

    def test_headless_smoke_ok_true(self) -> None:
        result = self._run("-m", "aurora_studio.ui.desktop_shell", "--headless-smoke")
        data = json.loads(result.stdout)
        self.assertTrue(data.get("ok"))

    def test_headless_smoke_has_shortcuts(self) -> None:
        result = self._run("-m", "aurora_studio.ui.desktop_shell", "--headless-smoke")
        data = json.loads(result.stdout)
        self.assertIn("shortcuts", data)

    def test_headless_smoke_no_stdout_spam(self) -> None:
        result = self._run("-m", "aurora_studio.ui.desktop_shell", "--headless-smoke")
        # stdout should be valid JSON only (no extra prints)
        stripped = result.stdout.strip()
        self.assertTrue(stripped.startswith("{"),
                        f"Unexpected stdout prefix:\n{stripped[:200]}")


# ---------------------------------------------------------------------------
# 6. Subprocess smoke — CLI
# ---------------------------------------------------------------------------

class TestSubprocessCLISmoke(unittest.TestCase):

    def _run(self, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_ENV,
            cwd=str(_REPO),
        )

    def test_cli_smoke_exit_zero(self) -> None:
        result = self._run("-m", "aurora_studio.cli", "smoke")
        self.assertEqual(result.returncode, 0,
                         f"stdout: {result.stdout}\nstderr: {result.stderr}")

    def test_cli_smoke_outputs_json(self) -> None:
        result = self._run("-m", "aurora_studio.cli", "smoke")
        data = json.loads(result.stdout)
        self.assertTrue(data.get("ok"))

    def test_cli_create_demo_exit_zero(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory(prefix="aurora_pkg_") as d:
            result = self._run(
                "-m", "aurora_studio.cli", "create-demo",
                "--path", d, "--title", "Pkg Demo")
            self.assertEqual(result.returncode, 0,
                             f"stdout: {result.stdout}\nstderr: {result.stderr}")

    def test_cli_create_demo_outputs_json(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory(prefix="aurora_pkg2_") as d:
            result = self._run(
                "-m", "aurora_studio.cli", "create-demo",
                "--path", d, "--title", "Pkg Demo 2")
            data = json.loads(result.stdout)
            self.assertIn("project_id", data)


# ---------------------------------------------------------------------------
# 7. Scripts do not contain pip install
# ---------------------------------------------------------------------------

class TestScriptsNoPipInstall(unittest.TestCase):

    # Build scripts (TASK-000046+) intentionally mention pip install as an
    # instructional message for developers, but must not auto-execute it.
    _BUILD_SCRIPTS = {"build_windows_onefolder.ps1", "build_windows_onefolder.bat"}

    def test_no_pip_in_any_script(self) -> None:
        for script in _SCRIPTS.iterdir():
            if script.name in self._BUILD_SCRIPTS:
                # Build scripts may print pip install instructions — skip broad check
                continue
            content = script.read_text(encoding="utf-8")
            self.assertNotIn("pip install", content,
                             f"Found 'pip install' in {script.name}")


if __name__ == "__main__":
    unittest.main()

"""Tests for DesktopShell and build_desktop_shell — TASK-000038.

All tests run headless. No display required.
Tests verify import safety, callable presence, headless smoke,
and UISession action compatibility needed by DesktopShell.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"


def _run_shell(*args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": str(SRC), "PYTHONPYCACHEPREFIX": "/tmp/pycache"}
    return subprocess.run(
        [sys.executable, "-m", "aurora_studio.ui.desktop_shell", *args],
        cwd=str(ROOT), env=env, capture_output=True, text=True,
    )


# ---------------------------------------------------------------------------
# Import safety
# ---------------------------------------------------------------------------

class TestDesktopShellImports(unittest.TestCase):

    def test_module_imports_without_window(self):
        from aurora_studio.ui import desktop_shell  # noqa: F401

    def test_headless_smoke_importable(self):
        from aurora_studio.ui.desktop_shell import headless_smoke

    def test_build_desktop_shell_importable(self):
        from aurora_studio.ui.desktop_shell import build_desktop_shell

    def test_desktop_shell_class_importable(self):
        from aurora_studio.ui.desktop_shell import DesktopShell

    def test_main_importable(self):
        from aurora_studio.ui.desktop_shell import main


# ---------------------------------------------------------------------------
# DesktopShell class API surface (no display needed)
# ---------------------------------------------------------------------------

class TestDesktopShellAPISurface(unittest.TestCase):
    """Verify required public methods exist on the class without instantiating."""

    REQUIRED_METHODS = [
        "refresh", "create_project", "open_project",
        "create_scene", "create_shot",
        "save_bundle", "load_bundle",
        "set_status", "get_state_snapshot", "run",
    ]

    def test_required_methods_exist(self):
        from aurora_studio.ui.desktop_shell import DesktopShell
        for method in self.REQUIRED_METHODS:
            self.assertTrue(
                callable(getattr(DesktopShell, method, None)),
                f"DesktopShell.{method} is not callable",
            )

    def test_build_desktop_shell_is_callable(self):
        from aurora_studio.ui.desktop_shell import build_desktop_shell
        self.assertTrue(callable(build_desktop_shell))


# ---------------------------------------------------------------------------
# headless_smoke()
# ---------------------------------------------------------------------------

class TestHeadlessSmoke(unittest.TestCase):

    def test_returns_dict(self):
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertIsInstance(result, dict)

    def test_ok_true(self):
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertTrue(result["ok"])

    def test_required_keys(self):
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        for key in ("ok", "application", "ui", "mode"):
            self.assertIn(key, result)

    def test_application_value(self):
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertEqual(result["application"], "aurora-studio")

    def test_ui_value(self):
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertEqual(result["ui"], "desktop-shell")

    def test_mode_value(self):
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertEqual(result["mode"], "headless-smoke")

    def test_json_serializable(self):
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        json.dumps(result)  # must not raise


# ---------------------------------------------------------------------------
# CLI --headless-smoke
# ---------------------------------------------------------------------------

class TestCLIHeadlessSmoke(unittest.TestCase):

    def test_exits_zero(self):
        r = _run_shell("--headless-smoke")
        self.assertEqual(r.returncode, 0)

    def test_outputs_valid_json(self):
        r = _run_shell("--headless-smoke")
        d = json.loads(r.stdout)
        self.assertIsInstance(d, dict)

    def test_ok_true(self):
        r = _run_shell("--headless-smoke")
        d = json.loads(r.stdout)
        self.assertTrue(d["ok"])

    def test_required_json_keys(self):
        r = _run_shell("--headless-smoke")
        d = json.loads(r.stdout)
        for key in ("ok", "application", "ui", "mode"):
            self.assertIn(key, d)

    def test_no_window_opened(self):
        """Headless smoke must produce no tkinter errors."""
        r = _run_shell("--headless-smoke")
        self.assertNotIn("TclError", r.stderr)
        self.assertNotIn("display", r.stderr.lower())


# ---------------------------------------------------------------------------
# UISession actions needed by DesktopShell
# ---------------------------------------------------------------------------

class TestUISessionForDesktopShell(unittest.TestCase):
    """Verify UISession has all actions DesktopShell needs."""

    REQUIRED_METHODS = [
        "create_project", "open_project",
        "create_scene", "create_shot",
        "save_bundle", "load_and_rehydrate_bundle",
        "get_app_state",
    ]

    def test_required_methods_exist(self):
        from aurora_studio.ui.actions import UISession
        session = UISession()
        for method in self.REQUIRED_METHODS:
            self.assertTrue(
                callable(getattr(session, method, None)),
                f"UISession.{method} is not callable",
            )

    def test_create_project_ok(self):
        from aurora_studio.ui.actions import UISession
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            r = session.create_project(tmp, "Window Test")
            self.assertTrue(r.ok)
            self.assertIn("project_id", r.payload)

    def test_create_scene_after_project_ok(self):
        from aurora_studio.ui.actions import UISession
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Film")
            r = session.create_scene("Scene")
            self.assertTrue(r.ok)
            self.assertIn("scene_id", r.payload)

    def test_create_shot_after_project_ok(self):
        from aurora_studio.ui.actions import UISession
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Film")
            sr = session.create_scene("Scene")
            r = session.create_shot(sr.payload["scene_id"], "Shot")
            self.assertTrue(r.ok)
            self.assertIn("shot_id", r.payload)

    def test_save_and_load_bundle_ok(self):
        from aurora_studio.ui.actions import UISession
        with tempfile.TemporaryDirectory() as tmp:
            s1 = UISession()
            s1.create_project(tmp, "Film")
            s1.create_scene("S")
            r_save = s1.save_bundle(tmp)
            self.assertTrue(r_save.ok)

            s2 = UISession()
            r_load = s2.load_and_rehydrate_bundle(tmp)
            self.assertTrue(r_load.ok)
            self.assertTrue(r_load.payload["rehydrated"])

    def test_get_app_state_json_serializable(self):
        from aurora_studio.ui.actions import UISession
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Film")
            session.create_scene("S")
            r = session.get_app_state()
            self.assertTrue(r.ok)
            json.dumps(r.payload)  # must not raise

    def test_open_project_ok(self):
        from aurora_studio.ui.actions import UISession
        with tempfile.TemporaryDirectory() as tmp:
            s1 = UISession()
            s1.create_project(tmp, "Film")
            s2 = UISession()
            r = s2.open_project(tmp)
            self.assertTrue(r.ok)
            self.assertIn("project_id", r.payload)

    def test_validation_error_returns_not_ok(self):
        from aurora_studio.ui.actions import UISession
        session = UISession()
        r = session.create_project("", "")
        self.assertFalse(r.ok)
        self.assertIsNone(r.payload)


if __name__ == "__main__":
    unittest.main()

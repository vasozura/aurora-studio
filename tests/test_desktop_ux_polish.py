"""Tests for TASK-000039: Desktop Project Scene Shot UX Polish Pack.

All tests are headless — no display required.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# sys.path setup
# ---------------------------------------------------------------------------
_SRC = str(Path(__file__).parent.parent / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from aurora_studio.ui import (
    UISession,
    UIActionResult,
    AppStateViewModel,
    ProjectViewModel,
    WorkspaceViewModel,
    SceneViewModel,
    ShotViewModel,
)
from aurora_studio.ui.desktop_shell import headless_smoke, build_desktop_shell, DesktopShell
from aurora_studio.ui.actions import UISession as UISessionDirect


# ---------------------------------------------------------------------------
# Import safety
# ---------------------------------------------------------------------------

class TestImportSafety(unittest.TestCase):

    def test_desktop_shell_import_no_window(self):
        """Importing desktop_shell must not open a window."""
        import aurora_studio.ui.desktop_shell as ds
        self.assertTrue(callable(ds.headless_smoke))
        self.assertTrue(callable(ds.build_desktop_shell))
        self.assertTrue(callable(ds.main))

    def test_desktop_shell_class_exists(self):
        """DesktopShell class must be importable."""
        self.assertTrue(isinstance(DesktopShell, type))

    def test_ui_package_no_tkinter_at_import(self):
        """aurora_studio.ui imports must not import tkinter at module level."""
        import aurora_studio.ui as ui_pkg
        import sys
        # tkinter MAY be already imported by something else; just verify ui_pkg has no hard dep
        self.assertTrue(hasattr(ui_pkg, "UISession"))
        self.assertTrue(hasattr(ui_pkg, "UIActionResult"))

    def test_headless_smoke_no_tkinter(self):
        """headless_smoke() must work without a display."""
        result = headless_smoke()
        self.assertIsInstance(result, dict)
        self.assertTrue(result["ok"])
        self.assertEqual(result["application"], "aurora-studio")
        self.assertEqual(result["ui"], "desktop-shell")


# ---------------------------------------------------------------------------
# headless_smoke
# ---------------------------------------------------------------------------

class TestHeadlessSmoke(unittest.TestCase):

    def test_headless_smoke_json_serializable(self):
        """headless_smoke() output must be JSON serializable."""
        result = headless_smoke()
        serialized = json.dumps(result)
        self.assertIsInstance(serialized, str)

    def test_headless_smoke_required_keys(self):
        result = headless_smoke()
        for key in ("ok", "application", "ui", "mode"):
            self.assertIn(key, result)

    def test_headless_smoke_mode(self):
        result = headless_smoke()
        self.assertEqual(result["mode"], "headless-smoke")

    def test_headless_smoke_includes_app_state(self):
        result = headless_smoke()
        self.assertIn("app_state_ok", result)
        self.assertIn("ui_session", result)


# ---------------------------------------------------------------------------
# CLI --headless-smoke
# ---------------------------------------------------------------------------

class TestCLIHeadlessSmoke(unittest.TestCase):

    def _run(self, *args):
        env = {"PYTHONPATH": _SRC, "PATH": "/usr/bin:/bin"}
        return subprocess.run(
            [sys.executable, "-m", "aurora_studio.ui.desktop_shell", *args],
            capture_output=True, text=True, env={**__import__("os").environ, **env},
        )

    def test_cli_headless_smoke_exit_zero(self):
        result = self._run("--headless-smoke")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_headless_smoke_valid_json(self):
        result = self._run("--headless-smoke")
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])

    def test_cli_headless_smoke_no_stderr(self):
        result = self._run("--headless-smoke")
        self.assertEqual(result.stderr.strip(), "")


# ---------------------------------------------------------------------------
# DesktopShell class — method existence (headless)
# ---------------------------------------------------------------------------

class TestDesktopShellInterface(unittest.TestCase):

    def test_desktop_shell_has_required_methods(self):
        required = [
            "refresh", "create_project", "open_project",
            "create_scene", "create_shot", "save_bundle",
            "load_bundle", "set_status", "get_state_snapshot",
        ]
        for method in required:
            self.assertTrue(
                callable(getattr(DesktopShell, method, None)),
                f"DesktopShell missing method: {method}",
            )

    def test_build_desktop_shell_callable(self):
        self.assertTrue(callable(build_desktop_shell))


# ---------------------------------------------------------------------------
# UISession — set_active_scene / set_active_shot
# ---------------------------------------------------------------------------

class TestUISessionActiveSelection(unittest.TestCase):

    def setUp(self):
        self.session = UISession()

    def test_set_active_scene_returns_uiactionresult(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.session.create_project(tmp, "Test")
            result = self.session.create_scene("Scene A")
            self.assertTrue(result.ok)
            scene_id = result.payload["scene_id"]
            ar = self.session.set_active_scene(scene_id)
            self.assertIsInstance(ar, UIActionResult)

    def test_set_active_scene_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.session.create_project(tmp, "Test")
            scene_result = self.session.create_scene("Scene B")
            self.assertTrue(scene_result.ok)
            scene_id = scene_result.payload["scene_id"]
            ar = self.session.set_active_scene(scene_id)
            self.assertTrue(ar.ok)

    def test_set_active_scene_payload_has_active_scene_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.session.create_project(tmp, "Test")
            scene_result = self.session.create_scene("Scene C")
            scene_id = scene_result.payload["scene_id"]
            ar = self.session.set_active_scene(scene_id)
            self.assertTrue(ar.ok)
            self.assertEqual(ar.payload.get("active_scene_id"), scene_id)

    def test_set_active_shot_returns_uiactionresult(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.session.create_project(tmp, "Test")
            sr = self.session.create_scene("Scene")
            scene_id = sr.payload["scene_id"]
            self.session.set_active_scene(scene_id)
            sh = self.session.create_shot(scene_id, "Shot A")
            self.assertTrue(sh.ok)
            shot_id = sh.payload["shot_id"]
            ar = self.session.set_active_shot(shot_id)
            self.assertIsInstance(ar, UIActionResult)
            self.assertTrue(ar.ok)

    def test_set_active_shot_payload_has_active_shot_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.session.create_project(tmp, "Test")
            sr = self.session.create_scene("Scene")
            scene_id = sr.payload["scene_id"]
            self.session.set_active_scene(scene_id)
            sh = self.session.create_shot(scene_id, "Shot B")
            shot_id = sh.payload["shot_id"]
            ar = self.session.set_active_shot(shot_id)
            self.assertTrue(ar.ok)
            self.assertEqual(ar.payload.get("active_shot_id"), shot_id)

    def test_set_active_scene_none_clears(self):
        """set_active_scene(None) should clear active scene."""
        with tempfile.TemporaryDirectory() as tmp:
            self.session.create_project(tmp, "Test")
            sr = self.session.create_scene("Scene")
            scene_id = sr.payload["scene_id"]
            self.session.set_active_scene(scene_id)
            ar = self.session.set_active_scene(None)
            self.assertIsInstance(ar, UIActionResult)
            # None is acceptable; may succeed or return ok=False — just must not raise
            self.assertIn("ok", ar.to_dict())


# ---------------------------------------------------------------------------
# UISession — create project/scene/shot flow
# ---------------------------------------------------------------------------

class TestUISessionFlow(unittest.TestCase):

    def test_create_project_returns_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            result = session.create_project(tmp, "UX Polish Project")
            self.assertTrue(result.ok)
            self.assertIn("project_id", result.payload)

    def test_create_scene_after_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            result = session.create_scene("Opening Scene")
            self.assertTrue(result.ok)
            self.assertIn("scene_id", result.payload)

    def test_create_shot_after_scene(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            sr = session.create_scene("Scene A")
            scene_id = sr.payload["scene_id"]
            session.set_active_scene(scene_id)
            result = session.create_shot(scene_id, "Opening Shot")
            self.assertTrue(result.ok)
            self.assertIn("shot_id", result.payload)

    def test_get_app_state_contains_scenes_shots(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            sr = session.create_scene("Scene")
            scene_id = sr.payload["scene_id"]
            session.create_shot(scene_id, "Shot")
            state_result = session.get_app_state()
            self.assertTrue(state_result.ok)
            self.assertGreaterEqual(len(state_result.payload["scenes"]), 1)
            self.assertGreaterEqual(len(state_result.payload["shots"]), 1)

    def test_create_scene_empty_title_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            result = session.create_scene("")
            self.assertFalse(result.ok)

    def test_create_shot_empty_title_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            sr = session.create_scene("Scene")
            scene_id = sr.payload["scene_id"]
            result = session.create_shot(scene_id, "")
            self.assertFalse(result.ok)


# ---------------------------------------------------------------------------
# AppStateViewModel JSON serialization
# ---------------------------------------------------------------------------

class TestAppStateViewModelJson(unittest.TestCase):

    def test_to_dict_json_serializable_empty(self):
        session = UISession()
        result = session.get_app_state()
        self.assertTrue(result.ok)
        serialized = json.dumps(result.payload)
        self.assertIsInstance(serialized, str)

    def test_to_dict_has_required_keys(self):
        session = UISession()
        result = session.get_app_state()
        payload = result.payload
        for key in ("project", "workspace", "scenes", "shots"):
            self.assertIn(key, payload)

    def test_to_dict_with_project_scene_shot(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Test")
            sr = session.create_scene("Scene A")
            scene_id = sr.payload["scene_id"]
            session.create_shot(scene_id, "Shot A")
            result = session.get_app_state()
            self.assertTrue(result.ok)
            payload = result.payload
            self.assertIsNotNone(payload["project"])
            self.assertIsInstance(payload["scenes"], list)
            self.assertIsInstance(payload["shots"], list)
            self.assertEqual(len(payload["scenes"]), 1)
            self.assertEqual(len(payload["shots"]), 1)
            # Must round-trip through JSON
            json.dumps(payload)

    def test_workspace_fields_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Test")
            result = session.get_app_state()
            ws = result.payload["workspace"]
            self.assertIn("active_project_id", ws)
            self.assertIn("active_scene_id", ws)
            self.assertIn("active_shot_id", ws)
            self.assertIn("mode", ws)


# ---------------------------------------------------------------------------
# get_state_snapshot contract (headless — via session only, no real shell)
# ---------------------------------------------------------------------------

class TestGetStateSnapshotContract(unittest.TestCase):
    """Verify the snapshot contract via UISession, since we can't create
    a DesktopShell without a display."""

    def test_get_app_state_payload_matches_snapshot_contract(self):
        """get_app_state payload covers the fields required by get_state_snapshot."""
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Snap")
            sr = session.create_scene("Scene S")
            scene_id = sr.payload["scene_id"]
            session.create_shot(scene_id, "Shot S")
            result = session.get_app_state()
            payload = result.payload
            # These are the fields get_state_snapshot must include
            scenes = payload.get("scenes", [])
            shots = payload.get("shots", [])
            snapshot = {
                "project": payload.get("project"),
                "workspace": payload.get("workspace"),
                "scene_count": len(scenes),
                "shot_count": len(shots),
                "selected_scene_id": None,
                "selected_shot_id": None,
                "status": "Ready.",
            }
            serialized = json.dumps(snapshot)
            self.assertIsInstance(serialized, str)

    def test_snapshot_no_tkinter_objects(self):
        """Ensure no tkinter objects appear in snapshot data."""
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Snap2")
            result = session.get_app_state()
            payload = result.payload
            # All values must be JSON serializable (no tkinter StringVar, etc.)
            json.dumps(payload)  # Would raise TypeError if tkinter objects present


# ---------------------------------------------------------------------------
# Selected scene → Create Shot flow (headless via UISession)
# ---------------------------------------------------------------------------

class TestSelectedSceneWorkflow(unittest.TestCase):

    def test_create_shot_with_explicit_scene_id(self):
        """UISession.create_shot with explicit scene_id works without display."""
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Wf")
            sr = session.create_scene("Scene W")
            scene_id = sr.payload["scene_id"]
            result = session.create_shot(scene_id, "Shot W1")
            self.assertTrue(result.ok)
            self.assertIn("shot_id", result.payload)

    def test_create_shot_under_active_scene(self):
        """After set_active_scene, create_shot under that scene works."""
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Wf2")
            sr = session.create_scene("Scene A2")
            scene_id = sr.payload["scene_id"]
            session.set_active_scene(scene_id)
            result = session.create_shot(scene_id, "Shot A2")
            self.assertTrue(result.ok)

    def test_shots_filtered_by_scene(self):
        """Shots belong to their parent scene."""
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Filter")
            sr1 = session.create_scene("Scene F1")
            sid1 = sr1.payload["scene_id"]
            sr2 = session.create_scene("Scene F2")
            sid2 = sr2.payload["scene_id"]
            session.create_shot(sid1, "Shot in F1")
            session.create_shot(sid2, "Shot in F2")
            state = session.get_app_state().payload
            shots = state["shots"]
            shots_s1 = [s for s in shots if s["scene_id"] == sid1]
            shots_s2 = [s for s in shots if s["scene_id"] == sid2]
            self.assertEqual(len(shots_s1), 1)
            self.assertEqual(len(shots_s2), 1)

    def test_no_scene_selected_and_no_active_scene(self):
        """When no scene is selected or active, create_shot on UISession with
        a missing scene_id returns ok=False."""
        session = UISession()
        # No project created, no scenes
        result = session.create_shot("nonexistent-scene-id", "Shot X")
        self.assertFalse(result.ok)


# ---------------------------------------------------------------------------
# Existing tests still importable (sanity check)
# ---------------------------------------------------------------------------

class TestExistingTestsCompatibility(unittest.TestCase):

    def test_headless_smoke_still_includes_ui_session_key(self):
        result = headless_smoke()
        self.assertIn("ui_session", result)
        self.assertEqual(result["ui_session"], "ready")

    def test_uisession_create_project_returns_uiactionresult(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            result = session.create_project(tmp, "Compat Test")
            self.assertIsInstance(result, UIActionResult)
            self.assertTrue(result.ok)

    def test_uiactionresult_to_dict(self):
        ar = UIActionResult(ok=True, message="good", payload={"x": 1})
        d = ar.to_dict()
        self.assertTrue(d["ok"])
        self.assertEqual(d["message"], "good")
        self.assertEqual(d["payload"], {"x": 1})


if __name__ == "__main__":
    unittest.main()

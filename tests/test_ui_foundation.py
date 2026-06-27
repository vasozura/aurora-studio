"""Tests for aurora_studio.ui — TASK-000037.

All tests run headless. No display required.
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


def _cli_shell(*args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": str(SRC), "PYTHONPYCACHEPREFIX": "/tmp/pycache"}
    return subprocess.run(
        [sys.executable, "-m", "aurora_studio.ui.desktop_shell", *args],
        cwd=str(ROOT), env=env, capture_output=True, text=True,
    )


# ---------------------------------------------------------------------------
# Import safety
# ---------------------------------------------------------------------------

class TestUIImports(unittest.TestCase):

    def test_ui_package_imports_without_window(self):
        from aurora_studio.ui import (
            UISession, UIActionResult,
            ProjectViewModel, WorkspaceViewModel,
            SceneViewModel, ShotViewModel, AppStateViewModel,
        )

    def test_desktop_shell_imports_without_window(self):
        from aurora_studio.ui.desktop_shell import headless_smoke, main, DesktopShell


# ---------------------------------------------------------------------------
# View models
# ---------------------------------------------------------------------------

class TestProjectViewModel(unittest.TestCase):

    def test_from_metadata(self):
        from aurora_studio.ui.view_models import ProjectViewModel
        from aurora_studio.contracts.project import ProjectMetadata
        meta = ProjectMetadata(project_id="p1", title="Film", version="0.1.0",
                               created_at="", modified_at="")
        vm = ProjectViewModel.from_metadata(meta)
        self.assertEqual(vm.project_id, "p1")
        self.assertEqual(vm.title, "Film")

    def test_to_dict(self):
        from aurora_studio.ui.view_models import ProjectViewModel
        from aurora_studio.contracts.project import ProjectMetadata
        meta = ProjectMetadata(project_id="p1", title="Film", version="0.1.0",
                               created_at="", modified_at="")
        d = ProjectViewModel.from_metadata(meta).to_dict()
        self.assertIn("project_id", d)
        self.assertIn("title", d)
        self.assertIn("version", d)


class TestWorkspaceViewModel(unittest.TestCase):

    def test_from_state(self):
        from aurora_studio.ui.view_models import WorkspaceViewModel
        from aurora_studio.contracts.workspace import WorkspaceState
        state = WorkspaceState(active_project_id="p1", active_scene_id="s1")
        vm = WorkspaceViewModel.from_state(state)
        self.assertEqual(vm.active_project_id, "p1")
        self.assertEqual(vm.active_scene_id, "s1")

    def test_to_dict(self):
        from aurora_studio.ui.view_models import WorkspaceViewModel
        from aurora_studio.contracts.workspace import WorkspaceState
        state = WorkspaceState(active_project_id="p1")
        d = WorkspaceViewModel.from_state(state).to_dict()
        self.assertIn("active_project_id", d)
        self.assertIn("mode", d)


class TestSceneViewModel(unittest.TestCase):

    def test_from_record(self):
        from aurora_studio.ui.view_models import SceneViewModel
        from aurora_studio.contracts.scene import SceneRecord
        rec = SceneRecord(scene_id="s1", project_id="p1", title="Opening")
        vm = SceneViewModel.from_record(rec)
        self.assertEqual(vm.scene_id, "s1")
        self.assertEqual(vm.title, "Opening")

    def test_to_dict(self):
        from aurora_studio.ui.view_models import SceneViewModel
        from aurora_studio.contracts.scene import SceneRecord
        rec = SceneRecord(scene_id="s1", project_id="p1", title="Opening")
        d = SceneViewModel.from_record(rec).to_dict()
        self.assertIn("scene_id", d)
        self.assertIn("project_id", d)
        self.assertIn("title", d)
        self.assertIn("state", d)


class TestShotViewModel(unittest.TestCase):

    def test_from_record(self):
        from aurora_studio.ui.view_models import ShotViewModel
        from aurora_studio.contracts.shot import ShotRecord
        rec = ShotRecord(shot_id="sh1", scene_id="s1", title="Wide", order_index=0)
        vm = ShotViewModel.from_record(rec)
        self.assertEqual(vm.shot_id, "sh1")
        self.assertEqual(vm.order_index, 0)

    def test_to_dict(self):
        from aurora_studio.ui.view_models import ShotViewModel
        from aurora_studio.contracts.shot import ShotRecord
        rec = ShotRecord(shot_id="sh1", scene_id="s1", title="Wide", order_index=1)
        d = ShotViewModel.from_record(rec).to_dict()
        self.assertIn("shot_id", d)
        self.assertIn("scene_id", d)
        self.assertIn("order_index", d)
        self.assertIn("state", d)


class TestAppStateViewModel(unittest.TestCase):

    def test_to_dict_json_serializable(self):
        from aurora_studio.ui.view_models import (
            AppStateViewModel, WorkspaceViewModel, SceneViewModel, ShotViewModel,
        )
        from aurora_studio.contracts.workspace import WorkspaceState
        ws = WorkspaceViewModel.from_state(WorkspaceState())
        app = AppStateViewModel(project=None, workspace=ws, scenes=(), shots=())
        d = app.to_dict()
        json.dumps(d)  # must not raise
        self.assertIsNone(d["project"])
        self.assertIn("workspace", d)
        self.assertEqual(d["scenes"], [])
        self.assertEqual(d["shots"], [])

    def test_to_dict_with_scenes_and_shots(self):
        from aurora_studio.ui.view_models import (
            AppStateViewModel, WorkspaceViewModel, SceneViewModel, ShotViewModel,
        )
        from aurora_studio.contracts.workspace import WorkspaceState
        from aurora_studio.contracts.scene import SceneRecord
        from aurora_studio.contracts.shot import ShotRecord
        ws = WorkspaceViewModel.from_state(WorkspaceState(active_project_id="p1"))
        scene_vm = SceneViewModel.from_record(
            SceneRecord(scene_id="s1", project_id="p1", title="S"))
        shot_vm = ShotViewModel.from_record(
            ShotRecord(shot_id="sh1", scene_id="s1", title="T", order_index=0))
        app = AppStateViewModel(project=None, workspace=ws,
                                scenes=(scene_vm,), shots=(shot_vm,))
        d = app.to_dict()
        self.assertEqual(len(d["scenes"]), 1)
        self.assertEqual(len(d["shots"]), 1)


# ---------------------------------------------------------------------------
# UISession
# ---------------------------------------------------------------------------

class TestUISessionInit(unittest.TestCase):

    def test_initializes_with_default_service(self):
        from aurora_studio.ui import UISession
        from aurora_studio.services import ApplicationService
        session = UISession()
        self.assertIsInstance(session.service, ApplicationService)

    def test_accepts_custom_service(self):
        from aurora_studio.ui import UISession
        from aurora_studio.services import ApplicationService
        svc = ApplicationService()
        session = UISession(service=svc)
        self.assertIs(session.service, svc)


class TestUISessionActions(unittest.TestCase):

    def test_create_project_returns_ok(self):
        from aurora_studio.ui import UISession
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            result = session.create_project(tmp, "Test Film")
            self.assertTrue(result.ok)
            self.assertIsNotNone(result.payload)
            self.assertIn("project_id", result.payload)

    def test_create_project_empty_title_returns_not_ok(self):
        from aurora_studio.ui import UISession
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            result = session.create_project(tmp, "")
            self.assertFalse(result.ok)
            self.assertIsNone(result.payload)
            self.assertIsInstance(result.message, str)

    def test_create_scene_after_project_returns_ok(self):
        from aurora_studio.ui import UISession
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Film")
            result = session.create_scene("Opening Scene")
            self.assertTrue(result.ok)
            self.assertIn("scene_id", result.payload)

    def test_create_scene_without_project_returns_not_ok(self):
        from aurora_studio.ui import UISession
        session = UISession()
        result = session.create_scene("Scene")
        self.assertFalse(result.ok)

    def test_create_shot_after_scene_returns_ok(self):
        from aurora_studio.ui import UISession
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Film")
            scene_result = session.create_scene("Scene")
            scene_id = scene_result.payload["scene_id"]
            result = session.create_shot(scene_id, "Opening Shot")
            self.assertTrue(result.ok)
            self.assertIn("shot_id", result.payload)

    def test_create_shot_without_project_returns_not_ok(self):
        from aurora_studio.ui import UISession
        session = UISession()
        result = session.create_shot("scene-x", "Shot")
        self.assertFalse(result.ok)

    def test_save_bundle_returns_ok(self):
        from aurora_studio.ui import UISession
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Film")
            result = session.save_bundle(tmp)
            self.assertTrue(result.ok)
            self.assertIn("bundle_path", result.payload)

    def test_load_and_rehydrate_bundle_returns_ok(self):
        from aurora_studio.ui import UISession
        with tempfile.TemporaryDirectory() as tmp:
            s1 = UISession()
            s1.create_project(tmp, "Film")
            s1.create_scene("Scene")
            s1.save_bundle(tmp)

            s2 = UISession()
            result = s2.load_and_rehydrate_bundle(tmp)
            self.assertTrue(result.ok)
            self.assertTrue(result.payload["rehydrated"])

    def test_get_app_state_returns_ok_and_json_serializable(self):
        from aurora_studio.ui import UISession
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Film")
            session.create_scene("Scene A")
            result = session.get_app_state()
            self.assertTrue(result.ok)
            d = result.payload
            json.dumps(d)  # must not raise
            self.assertIn("project", d)
            self.assertIn("workspace", d)
            self.assertIn("scenes", d)
            self.assertIn("shots", d)
            self.assertEqual(len(d["scenes"]), 1)

    def test_get_app_state_empty_session_is_ok(self):
        from aurora_studio.ui import UISession
        session = UISession()
        result = session.get_app_state()
        self.assertTrue(result.ok)
        self.assertIsNone(result.payload["project"])

    def test_ui_action_result_to_dict(self):
        from aurora_studio.ui import UIActionResult
        r = UIActionResult(ok=True, message="done", payload={"x": 1})
        d = r.to_dict()
        self.assertTrue(d["ok"])
        self.assertEqual(d["message"], "done")
        self.assertEqual(d["payload"], {"x": 1})


# ---------------------------------------------------------------------------
# Desktop shell headless
# ---------------------------------------------------------------------------

class TestDesktopShellHeadless(unittest.TestCase):

    def test_headless_smoke_returns_dict(self):
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        self.assertIsInstance(result, dict)
        self.assertTrue(result["ok"])

    def test_headless_smoke_json_serializable(self):
        from aurora_studio.ui.desktop_shell import headless_smoke
        result = headless_smoke()
        json.dumps(result)  # must not raise

    def test_headless_smoke_cli_exits_zero(self):
        r = _cli_shell("--headless-smoke")
        self.assertEqual(r.returncode, 0)

    def test_headless_smoke_cli_outputs_valid_json(self):
        r = _cli_shell("--headless-smoke")
        d = json.loads(r.stdout)
        self.assertTrue(d["ok"])
        self.assertEqual(d["mode"], "headless-smoke")


if __name__ == "__main__":
    unittest.main()

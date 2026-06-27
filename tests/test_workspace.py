"""Tests for the first minimal Workspace implementation."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.contracts.workspace import DEFAULT_WORKSPACE_MODE, WorkspaceState
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.readiness import Readiness
from aurora_studio.modules.workspace import Workspace


class WorkspaceImplementationTests(unittest.TestCase):
    def test_workspace_initial_state(self) -> None:
        workspace = Workspace()

        state = workspace.get_state()

        self.assertIsInstance(state, WorkspaceState)
        self.assertIsNone(state.active_project_id)
        self.assertIsNone(state.active_scene_id)
        self.assertIsNone(state.active_shot_id)
        self.assertEqual(state.mode, DEFAULT_WORKSPACE_MODE)

    def test_activate_sets_active_project(self) -> None:
        workspace = Workspace()

        state = workspace.activate("project-123")

        self.assertEqual(state.active_project_id, "project-123")
        self.assertIsNone(state.active_scene_id)
        self.assertIsNone(state.active_shot_id)

    def test_activate_rejects_empty_project_id(self) -> None:
        workspace = Workspace()

        with self.assertRaises(ValidationError):
            workspace.activate("   ")

    def test_set_mode_updates_mode(self) -> None:
        workspace = Workspace()
        workspace.activate("project-123")

        state = workspace.set_mode("planning")

        self.assertEqual(state.mode, "planning")
        self.assertEqual(state.active_project_id, "project-123")

    def test_set_mode_rejects_empty_mode(self) -> None:
        workspace = Workspace()

        with self.assertRaises(ValidationError):
            workspace.set_mode("   ")

    def test_set_active_scene_and_shot_references(self) -> None:
        workspace = Workspace()
        workspace.activate("project-123")

        scene_state = workspace.set_active_scene("scene-1")
        shot_state = workspace.set_active_shot("shot-1")

        self.assertEqual(scene_state.active_scene_id, "scene-1")
        self.assertEqual(shot_state.active_scene_id, "scene-1")
        self.assertEqual(shot_state.active_shot_id, "shot-1")

    def test_optional_refs_can_be_cleared_with_none(self) -> None:
        workspace = Workspace()
        workspace.activate("project-123")
        workspace.set_active_scene("scene-1")
        workspace.set_active_shot("shot-1")

        workspace.set_active_scene(None)
        workspace.set_active_shot(None)
        state = workspace.get_state()

        self.assertIsNone(state.active_scene_id)
        self.assertIsNone(state.active_shot_id)

    def test_optional_refs_reject_blank_values(self) -> None:
        workspace = Workspace()

        with self.assertRaises(ValidationError):
            workspace.set_active_scene("   ")

        with self.assertRaises(ValidationError):
            workspace.set_active_shot("   ")

    def test_selection_and_timeline_can_be_set_and_cleared(self) -> None:
        workspace = Workspace()
        workspace.activate("project-123")

        workspace.set_active_timeline("timeline-1")
        workspace.set_selection("scene-1")
        populated = workspace.get_state()

        self.assertEqual(populated.active_timeline_id, "timeline-1")
        self.assertEqual(populated.selected_ref, "scene-1")

        cleared = workspace.clear_selection()

        self.assertEqual(cleared.active_project_id, "project-123")
        self.assertIsNone(cleared.active_scene_id)
        self.assertIsNone(cleared.active_shot_id)
        self.assertIsNone(cleared.active_timeline_id)
        self.assertIsNone(cleared.selected_ref)

    def test_workspace_state_serializes_to_dict(self) -> None:
        state = WorkspaceState(
            active_project_id="project-123",
            active_scene_id="scene-1",
            active_shot_id="shot-1",
            selected_ref="shot-1",
            mode="planning",
        )

        data = state.to_dict()

        self.assertEqual(data["active_project_id"], "project-123")
        self.assertEqual(data["active_scene_id"], "scene-1")
        self.assertEqual(data["active_shot_id"], "shot-1")
        self.assertEqual(data["selected_ref"], "shot-1")
        self.assertEqual(data["mode"], "planning")

    def test_workspace_still_reports_not_ready(self) -> None:
        workspace = Workspace()

        self.assertEqual(workspace.get_readiness(), Readiness.NOT_READY)
        self.assertIn("not ready", workspace.describe().lower())


if __name__ == "__main__":
    unittest.main()

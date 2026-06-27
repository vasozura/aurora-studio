"""Project health smoke tests — TASK-000036.

Compact cross-cutting checks: imports, manager instantiation,
readiness, serialization round-trips, bundle flow, CLI JSON output.
Does not duplicate detailed unit tests already in other test files.
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


def _cli(*args: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": str(SRC), "PYTHONPYCACHEPREFIX": "/tmp/pycache"}
    return subprocess.run(
        [sys.executable, "-m", "aurora_studio.cli", *args],
        cwd=str(ROOT), env=env, capture_output=True, text=True,
    )


# ---------------------------------------------------------------------------
# Package imports
# ---------------------------------------------------------------------------

class TestPackageImports(unittest.TestCase):

    def test_contracts_package_imports(self):
        from aurora_studio.contracts import (
            ProjectMetadata, WorkspaceState,
            SceneRecord, SceneRef, ShotRecord, ShotRef,
            TimelineRecord, TimelineRef, TimelineItem,
            AssetRecord, AssetRef, CharacterRecord, CharacterRef,
            AFLValidationReport, AFLValidationIssue,
            ExportArtifactRecord, ExportArtifactRef,
            PluginMetadata, ProjectBundle,
        )

    def test_modules_package_imports(self):
        from aurora_studio.modules import (
            ProjectManager, Workspace, SceneManager, ShotManager,
            TimelineManager, AssetManager, CharacterManager,
            AFLEngine, PromptExportManager, PluginManager,
        )

    def test_persistence_package_imports(self):
        from aurora_studio.persistence import LocalProjectStore, BundleRehydrator

    def test_services_package_imports(self):
        from aurora_studio.services import ApplicationService

    def test_cli_package_imports(self):
        from aurora_studio.cli.main import main


# ---------------------------------------------------------------------------
# Manager health
# ---------------------------------------------------------------------------

class TestManagerHealth(unittest.TestCase):

    def _check_manager(self, cls):
        from aurora_studio.core.readiness import Readiness
        inst = cls()
        self.assertTrue(hasattr(inst, "module_name"), f"{cls.__name__} missing module_name")
        self.assertTrue(hasattr(inst, "get_readiness"), f"{cls.__name__} missing get_readiness")
        self.assertTrue(hasattr(inst, "describe"), f"{cls.__name__} missing describe")
        self.assertEqual(inst.get_readiness(), Readiness.NOT_READY,
                         f"{cls.__name__} readiness should be NOT_READY")

    def test_all_managers_instantiate_and_not_ready(self):
        from aurora_studio.modules import (
            ProjectManager, Workspace, SceneManager, ShotManager,
            TimelineManager, AssetManager, CharacterManager,
            AFLEngine, PromptExportManager, PluginManager,
        )
        for cls in (SceneManager, ShotManager, TimelineManager, AssetManager,
                    CharacterManager, AFLEngine, PromptExportManager, PluginManager):
            with self.subTest(cls=cls.__name__):
                self._check_manager(cls)


# ---------------------------------------------------------------------------
# Serialization round-trips
# ---------------------------------------------------------------------------

class TestSerializationRoundTrips(unittest.TestCase):

    def test_scene_record_round_trip(self):
        from aurora_studio.contracts.scene import SceneRecord
        r = SceneRecord(scene_id="s1", project_id="p1", title="T")
        self.assertEqual(SceneRecord.from_dict(r.to_dict()).scene_id, "s1")

    def test_shot_record_round_trip(self):
        from aurora_studio.contracts.shot import ShotRecord
        r = ShotRecord(shot_id="sh1", scene_id="s1", title="T")
        self.assertEqual(ShotRecord.from_dict(r.to_dict()).shot_id, "sh1")

    def test_timeline_record_with_items_round_trip(self):
        from aurora_studio.contracts.timeline import TimelineRecord, TimelineItem
        ti = TimelineItem(item_id="i1", item_type="scene", target_id="s1")
        r = TimelineRecord(timeline_id="tl1", project_id="p1", title="T", items=(ti,))
        r2 = TimelineRecord.from_dict(r.to_dict())
        self.assertEqual(len(r2.items), 1)
        self.assertIsInstance(r2.items, tuple)
        self.assertEqual(r2.items[0].item_id, "i1")

    def test_character_reference_asset_ids_round_trip(self):
        from aurora_studio.contracts.character import CharacterRecord
        r = CharacterRecord(character_id="c1", project_id="p1",
                            display_name="N", reference_asset_ids=("a1", "a2"))
        r2 = CharacterRecord.from_dict(r.to_dict())
        self.assertIsInstance(r2.reference_asset_ids, tuple)
        self.assertEqual(r2.reference_asset_ids, ("a1", "a2"))

    def test_plugin_metadata_capabilities_round_trip(self):
        from aurora_studio.contracts.plugin import PluginMetadata
        r = PluginMetadata(plugin_id="p1", name="N", version="1.0",
                           capabilities=("gen",), permissions=("read",))
        r2 = PluginMetadata.from_dict(r.to_dict())
        self.assertEqual(r2.capabilities, ("gen",))
        self.assertEqual(r2.permissions, ("read",))

    def test_workspace_state_round_trip(self):
        from aurora_studio.contracts.workspace import WorkspaceState
        ws = WorkspaceState(active_project_id="p1", active_scene_id="s1")
        ws2 = WorkspaceState.from_dict(ws.to_dict())
        self.assertEqual(ws2.active_project_id, "p1")
        self.assertEqual(ws2.active_scene_id, "s1")

    def test_project_bundle_empty_round_trip(self):
        from aurora_studio.contracts.project_bundle import ProjectBundle, CURRENT_BUNDLE_VERSION
        meta = {"project_id": "p1", "title": "T", "version": "0.1.0",
                "created_at": "", "modified_at": ""}
        b = ProjectBundle.empty(meta)
        b2 = ProjectBundle.from_dict(b.to_dict())
        self.assertEqual(b2.schema_version, CURRENT_BUNDLE_VERSION)
        self.assertIsInstance(b2.scenes, tuple)
        self.assertIsInstance(b2.shots, tuple)


# ---------------------------------------------------------------------------
# Bundle save/load/rehydrate flow
# ---------------------------------------------------------------------------

class TestBundleFlow(unittest.TestCase):

    def test_full_save_load_rehydrate_flow(self):
        from aurora_studio.services import ApplicationService

        with tempfile.TemporaryDirectory() as tmp:
            svc_a = ApplicationService()
            meta = svc_a.create_project(tmp, "Health Test")
            scene = svc_a.create_scene("Scene One")
            svc_a.create_shot(scene.scene_id, "Shot One")
            svc_a.save_bundle(tmp)

            # load_bundle is non-rehydrating
            svc_b = ApplicationService()
            svc_b.load_bundle(tmp)
            self.assertEqual(svc_b.scene_manager.list_scenes(), [])

            # load_and_rehydrate_bundle restores state
            svc_c = ApplicationService()
            result = svc_c.load_and_rehydrate_bundle(tmp)
            self.assertEqual(result["summary"]["scenes"], 1)
            self.assertEqual(result["summary"]["shots"], 1)
            self.assertTrue(result["summary"]["workspace_restored"])
            state = svc_c.get_workspace_state()
            self.assertEqual(state.active_project_id, meta.project_id)

    def test_load_bundle_non_rehydrating(self):
        from aurora_studio.services import ApplicationService
        with tempfile.TemporaryDirectory() as tmp:
            svc_a = ApplicationService()
            svc_a.create_project(tmp, "NR Test")
            svc_a.create_scene("S")
            svc_a.save_bundle(tmp)

            svc_b = ApplicationService()
            svc_b.load_bundle(tmp)
            self.assertEqual(svc_b.scene_manager.list_scenes(), [])


# ---------------------------------------------------------------------------
# CLI JSON output health
# ---------------------------------------------------------------------------

class TestCLIHealth(unittest.TestCase):

    def test_smoke_is_valid_json(self):
        r = _cli("smoke")
        self.assertEqual(r.returncode, 0)
        d = json.loads(r.stdout)
        self.assertTrue(d["ok"])

    def test_all_commands_output_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _cli("create-demo", "--path", tmp, "--title", "H")
            self.assertEqual(r.returncode, 0)
            json.loads(r.stdout)

            for cmd in ("inspect-bundle", "validate-bundle", "rehydrate-bundle"):
                with self.subTest(cmd=cmd):
                    r = _cli(cmd, "--path", tmp)
                    self.assertEqual(r.returncode, 0)
                    json.loads(r.stdout)

    def test_error_output_is_json_to_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = str(Path(tmp) / "no_such_path")
            r = _cli("inspect-bundle", "--path", bad)
            self.assertNotEqual(r.returncode, 0)
            err = json.loads(r.stderr)
            self.assertFalse(err["ok"])
            self.assertIn("error", err)

    def test_no_traceback_on_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = str(Path(tmp) / "no_such_path")
            r = _cli("inspect-bundle", "--path", bad)
            self.assertNotIn("Traceback", r.stderr)

    def test_validate_bundle_does_not_rehydrate(self):
        """validate-bundle must leave managers empty — tested indirectly via CLI output."""
        with tempfile.TemporaryDirectory() as tmp:
            _cli("create-demo", "--path", tmp, "--title", "VB")
            r = _cli("validate-bundle", "--path", tmp)
            d = json.loads(r.stdout)
            # validate-bundle only reads; it must not output rehydrated key
            self.assertNotIn("rehydrated", d)

    def test_rehydrate_bundle_workspace_restored(self):
        with tempfile.TemporaryDirectory() as tmp:
            _cli("create-demo", "--path", tmp, "--title", "RB")
            r = _cli("rehydrate-bundle", "--path", tmp)
            d = json.loads(r.stdout)
            self.assertTrue(d["workspace_restored"])
            self.assertIsNotNone(d["active_project_id"])


if __name__ == "__main__":
    unittest.main()

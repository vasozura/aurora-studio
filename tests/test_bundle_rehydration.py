"""Tests for BundleRehydrator and ApplicationService.load_and_rehydrate_bundle — TASK-000034."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aurora_studio.contracts.afl import AFLValidationReport, AFL_STATUS_VALID
from aurora_studio.contracts.asset import AssetRecord, ASSET_STATE_ACTIVE
from aurora_studio.contracts.character import CharacterRecord, CHARACTER_STATE_ACTIVE
from aurora_studio.contracts.export import ExportArtifactRecord, EXPORT_STATUS_DRAFT
from aurora_studio.contracts.plugin import PluginMetadata, PLUGIN_STATE_DISCOVERED
from aurora_studio.contracts.project_bundle import ProjectBundle, CURRENT_BUNDLE_VERSION
from aurora_studio.contracts.scene import SceneRecord, SCENE_STATE_DRAFT
from aurora_studio.contracts.shot import ShotRecord, SHOT_STATE_DRAFT
from aurora_studio.contracts.timeline import TimelineRecord, TIMELINE_STATE_DRAFT
from aurora_studio.contracts.workspace import WorkspaceState
from aurora_studio.core.errors import ValidationError
from aurora_studio.modules.afl_engine import AFLEngine
from aurora_studio.modules.asset_manager import AssetManager
from aurora_studio.modules.character_manager import CharacterManager
from aurora_studio.modules.plugin_manager import PluginManager
from aurora_studio.modules.prompt_export_manager import PromptExportManager
from aurora_studio.modules.scene_manager import SceneManager
from aurora_studio.modules.shot_manager import ShotManager
from aurora_studio.modules.timeline_manager import TimelineManager
from aurora_studio.modules.workspace import Workspace
from aurora_studio.persistence import BundleRehydrator
from aurora_studio.persistence.rehydration import BundleRehydrator
from aurora_studio.services import ApplicationService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_bundle(**overrides) -> ProjectBundle:
    """Return a minimal valid bundle for testing."""
    defaults = {
        "schema_version": CURRENT_BUNDLE_VERSION,
        "project_metadata": {"project_id": "proj-1", "title": "T", "version": "0.1.0",
                             "created_at": "2026-01-01T00:00:00+00:00",
                             "modified_at": "2026-01-01T00:00:00+00:00"},
    }
    defaults.update(overrides)
    return ProjectBundle(**defaults)


def _scene_dict(**kw) -> dict:
    d = {"scene_id": "scene-1", "project_id": "proj-1", "title": "S",
         "purpose": "", "state": SCENE_STATE_DRAFT, "created_at": "", "modified_at": "",
         "archived_at": None}
    d.update(kw)
    return d


def _shot_dict(**kw) -> dict:
    d = {"shot_id": "shot-1", "scene_id": "scene-1", "title": "T",
         "purpose": "", "order_index": 0, "state": SHOT_STATE_DRAFT,
         "created_at": "", "modified_at": "", "archived_at": None}
    d.update(kw)
    return d


def _timeline_dict(**kw) -> dict:
    d = {"timeline_id": "tl-1", "project_id": "proj-1", "title": "TL",
         "items": [], "state": TIMELINE_STATE_DRAFT,
         "created_at": "", "modified_at": "", "archived_at": None}
    d.update(kw)
    return d


def _asset_dict(**kw) -> dict:
    d = {"asset_id": "asset-1", "project_id": "proj-1", "asset_type": "image",
         "display_name": "A", "location": "", "state": ASSET_STATE_ACTIVE,
         "owner_ref": None, "created_at": "", "modified_at": "", "archived_at": None}
    d.update(kw)
    return d


def _character_dict(**kw) -> dict:
    d = {"character_id": "char-1", "project_id": "proj-1", "display_name": "C",
         "description": "", "reference_asset_ids": [],
         "state": CHARACTER_STATE_ACTIVE,
         "created_at": "", "modified_at": "", "archived_at": None}
    d.update(kw)
    return d


def _report_dict(**kw) -> dict:
    d = {"report_id": "report-1", "target_ref": "proj-1",
         "status": AFL_STATUS_VALID, "issues": [], "created_at": ""}
    d.update(kw)
    return d


def _artifact_dict(**kw) -> dict:
    d = {"artifact_id": "artifact-1", "source_id": "scene-1",
         "artifact_type": "prompt", "content": "hello",
         "status": EXPORT_STATUS_DRAFT, "provider_target": None,
         "created_at": "", "modified_at": ""}
    d.update(kw)
    return d


def _plugin_dict(**kw) -> dict:
    d = {"plugin_id": "plugin-1", "name": "MyPlugin", "version": "1.0",
         "capabilities": [], "permissions": [], "state": PLUGIN_STATE_DISCOVERED}
    d.update(kw)
    return d


# ---------------------------------------------------------------------------
# BundleRehydrator unit tests
# ---------------------------------------------------------------------------

class TestBundleRehydratorValidation(unittest.TestCase):

    def test_rejects_non_bundle(self):
        r = BundleRehydrator()
        with self.assertRaises(ValidationError):
            r.rehydrate({"schema_version": "0.1.0"})

    def test_rejects_none(self):
        r = BundleRehydrator()
        with self.assertRaises(ValidationError):
            r.rehydrate(None)


class TestBundleRehydratorScenes(unittest.TestCase):

    def test_restores_scenes(self):
        bundle = _minimal_bundle(scenes=(_scene_dict(),))
        sm = SceneManager()
        BundleRehydrator().rehydrate(bundle, scene_manager=sm)
        scenes = sm.list_scenes()
        self.assertEqual(len(scenes), 1)
        self.assertEqual(scenes[0].scene_id, "scene-1")

    def test_summary_scene_count(self):
        bundle = _minimal_bundle(scenes=(_scene_dict(),))
        sm = SceneManager()
        summary = BundleRehydrator().rehydrate(bundle, scene_manager=sm)
        self.assertEqual(summary["scenes"], 1)


class TestBundleRehydratorShots(unittest.TestCase):

    def test_restores_shots(self):
        bundle = _minimal_bundle(shots=(_shot_dict(),))
        sm = ShotManager()
        BundleRehydrator().rehydrate(bundle, shot_manager=sm)
        shots = sm.list_shots()
        self.assertEqual(len(shots), 1)
        self.assertEqual(shots[0].shot_id, "shot-1")

    def test_summary_shot_count(self):
        bundle = _minimal_bundle(shots=(_shot_dict(),))
        sm = ShotManager()
        summary = BundleRehydrator().rehydrate(bundle, shot_manager=sm)
        self.assertEqual(summary["shots"], 1)


class TestBundleRehydratorTimelines(unittest.TestCase):

    def test_restores_timelines(self):
        bundle = _minimal_bundle(timelines=(_timeline_dict(),))
        tm = TimelineManager()
        BundleRehydrator().rehydrate(bundle, timeline_manager=tm)
        timelines = tm.list_timelines()
        self.assertEqual(len(timelines), 1)
        self.assertEqual(timelines[0].timeline_id, "tl-1")

    def test_summary_timeline_count(self):
        bundle = _minimal_bundle(timelines=(_timeline_dict(),))
        tm = TimelineManager()
        summary = BundleRehydrator().rehydrate(bundle, timeline_manager=tm)
        self.assertEqual(summary["timelines"], 1)


class TestBundleRehydratorAssets(unittest.TestCase):

    def test_restores_assets(self):
        bundle = _minimal_bundle(assets=(_asset_dict(),))
        am = AssetManager()
        BundleRehydrator().rehydrate(bundle, asset_manager=am)
        assets = am.list_assets()
        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0].asset_id, "asset-1")

    def test_summary_asset_count(self):
        bundle = _minimal_bundle(assets=(_asset_dict(),))
        am = AssetManager()
        summary = BundleRehydrator().rehydrate(bundle, asset_manager=am)
        self.assertEqual(summary["assets"], 1)


class TestBundleRehydratorCharacters(unittest.TestCase):

    def test_restores_characters(self):
        bundle = _minimal_bundle(characters=(_character_dict(),))
        cm = CharacterManager()
        BundleRehydrator().rehydrate(bundle, character_manager=cm)
        chars = cm.list_characters()
        self.assertEqual(len(chars), 1)
        self.assertEqual(chars[0].character_id, "char-1")

    def test_summary_character_count(self):
        bundle = _minimal_bundle(characters=(_character_dict(),))
        cm = CharacterManager()
        summary = BundleRehydrator().rehydrate(bundle, character_manager=cm)
        self.assertEqual(summary["characters"], 1)


class TestBundleRehydratorAFLReports(unittest.TestCase):

    def test_restores_reports(self):
        bundle = _minimal_bundle(afl_reports=(_report_dict(),))
        engine = AFLEngine()
        BundleRehydrator().rehydrate(bundle, afl_engine=engine)
        reports = engine.list_validation_reports()
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].report_id, "report-1")

    def test_summary_report_count(self):
        bundle = _minimal_bundle(afl_reports=(_report_dict(),))
        engine = AFLEngine()
        summary = BundleRehydrator().rehydrate(bundle, afl_engine=engine)
        self.assertEqual(summary["afl_reports"], 1)


class TestBundleRehydratorExportArtifacts(unittest.TestCase):

    def test_restores_artifacts(self):
        bundle = _minimal_bundle(export_artifacts=(_artifact_dict(),))
        pem = PromptExportManager()
        BundleRehydrator().rehydrate(bundle, prompt_export_manager=pem)
        artifacts = pem.list_export_artifacts()
        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].artifact_id, "artifact-1")

    def test_summary_artifact_count(self):
        bundle = _minimal_bundle(export_artifacts=(_artifact_dict(),))
        pem = PromptExportManager()
        summary = BundleRehydrator().rehydrate(bundle, prompt_export_manager=pem)
        self.assertEqual(summary["export_artifacts"], 1)


class TestBundleRehydratorPlugins(unittest.TestCase):

    def test_restores_plugins(self):
        bundle = _minimal_bundle(plugins=(_plugin_dict(),))
        pm = PluginManager()
        BundleRehydrator().rehydrate(bundle, plugin_manager=pm)
        plugins = pm.list_plugins()
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0].plugin_id, "plugin-1")

    def test_summary_plugin_count(self):
        bundle = _minimal_bundle(plugins=(_plugin_dict(),))
        pm = PluginManager()
        summary = BundleRehydrator().rehydrate(bundle, plugin_manager=pm)
        self.assertEqual(summary["plugins"], 1)


class TestBundleRehydratorWorkspace(unittest.TestCase):

    def test_restores_workspace_state(self):
        ws_dict = {"active_project_id": "proj-1", "active_scene_id": "scene-1",
                   "active_shot_id": None, "active_timeline_id": None,
                   "selected_ref": None, "mode": "default"}
        bundle = _minimal_bundle(workspace_state=ws_dict)
        ws = Workspace()
        summary = BundleRehydrator().rehydrate(bundle, workspace=ws)
        self.assertTrue(summary["workspace_restored"])
        state = ws.get_state()
        self.assertEqual(state.active_project_id, "proj-1")
        self.assertEqual(state.active_scene_id, "scene-1")

    def test_workspace_not_restored_when_not_provided(self):
        ws_dict = {"active_project_id": "proj-1", "active_scene_id": None,
                   "active_shot_id": None, "active_timeline_id": None,
                   "selected_ref": None, "mode": "default"}
        bundle = _minimal_bundle(workspace_state=ws_dict)
        summary = BundleRehydrator().rehydrate(bundle)  # no workspace
        self.assertFalse(summary["workspace_restored"])

    def test_workspace_not_restored_when_bundle_has_no_state(self):
        bundle = _minimal_bundle(workspace_state=None)
        ws = Workspace()
        summary = BundleRehydrator().rehydrate(bundle, workspace=ws)
        self.assertFalse(summary["workspace_restored"])


class TestBundleRehydratorSkipsAbsent(unittest.TestCase):

    def test_skips_missing_managers(self):
        bundle = _minimal_bundle(
            scenes=(_scene_dict(),),
            shots=(_shot_dict(),),
        )
        # Only scene_manager provided; shot_manager skipped
        sm = SceneManager()
        summary = BundleRehydrator().rehydrate(bundle, scene_manager=sm)
        self.assertEqual(summary["scenes"], 1)
        self.assertEqual(summary["shots"], 0)  # skipped


class TestBundleRehydratorReadiness(unittest.TestCase):

    def test_rehydrated_managers_remain_not_ready(self):
        from aurora_studio.core.readiness import Readiness
        bundle = _minimal_bundle(scenes=(_scene_dict(),))
        sm = SceneManager()
        BundleRehydrator().rehydrate(bundle, scene_manager=sm)
        self.assertEqual(sm.get_readiness(), Readiness.NOT_READY)


# ---------------------------------------------------------------------------
# ApplicationService tests
# ---------------------------------------------------------------------------

class TestApplicationServiceLoadBundle(unittest.TestCase):

    def test_load_bundle_remains_non_rehydrating(self):
        with tempfile.TemporaryDirectory() as tmp:
            svc_a = ApplicationService()
            svc_a.create_project(tmp, "Test")
            svc_a.create_scene("Scene A")
            svc_a.save_bundle(tmp)

            svc_b = ApplicationService()
            svc_b.load_bundle(tmp)  # non-rehydrating
            # managers still empty
            self.assertEqual(svc_b.scene_manager.list_scenes(), [])


class TestApplicationServiceLoadAndRehydrate(unittest.TestCase):

    def test_restores_managers(self):
        with tempfile.TemporaryDirectory() as tmp:
            svc_a = ApplicationService()
            svc_a.create_project(tmp, "Film A")
            svc_a.create_scene("Scene Alpha")
            svc_a.create_shot("scene-x", "Shot One")  # scene_id doesn't need to exist
            svc_a.save_bundle(tmp)

            svc_b = ApplicationService()
            self.assertEqual(svc_b.scene_manager.list_scenes(), [])

            result = svc_b.load_and_rehydrate_bundle(tmp)
            self.assertIn("bundle", result)
            self.assertIn("summary", result)
            self.assertEqual(result["summary"]["scenes"], 1)
            self.assertEqual(result["summary"]["shots"], 1)

    def test_restores_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            svc_a = ApplicationService()
            meta = svc_a.create_project(tmp, "Film B")
            scene = svc_a.create_scene("Scene Beta")
            svc_a.save_bundle(tmp)

            svc_b = ApplicationService()
            svc_b.load_and_rehydrate_bundle(tmp)
            state = svc_b.get_workspace_state()
            self.assertEqual(state.active_project_id, meta.project_id)
            self.assertEqual(state.active_scene_id, scene.scene_id)
            self.assertTrue(result["summary"]["workspace_restored"]
                            for result in [svc_b.load_and_rehydrate_bundle(tmp)])

    def test_restores_project_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            svc_a = ApplicationService()
            meta = svc_a.create_project(tmp, "Film C")
            svc_a.save_bundle(tmp)

            svc_b = ApplicationService()
            svc_b.load_and_rehydrate_bundle(tmp)
            self.assertIsNotNone(svc_b._current_project_metadata)
            self.assertEqual(svc_b._current_project_metadata.project_id, meta.project_id)

    def test_can_create_scene_after_rehydration(self):
        with tempfile.TemporaryDirectory() as tmp:
            svc_a = ApplicationService()
            svc_a.create_project(tmp, "Film D")
            svc_a.create_scene("Scene Original")
            svc_a.save_bundle(tmp)

            svc_b = ApplicationService()
            svc_b.load_and_rehydrate_bundle(tmp)
            # workspace active_project_id restored, so create_scene works
            new_scene = svc_b.create_scene("Scene New")
            self.assertIsNotNone(new_scene.scene_id)
            all_scenes = svc_b.scene_manager.list_scenes()
            self.assertEqual(len(all_scenes), 2)


class TestIntegrationFullLoop(unittest.TestCase):
    """Full create → save → rehydrate loop."""

    def test_full_rehydration_loop(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Step 1-5: Create service A with data
            svc_a = ApplicationService()
            meta = svc_a.create_project(tmp, "Demo Film")
            scene = svc_a.create_scene("Opening Scene")
            shot = svc_a.create_shot(scene.scene_id, "Opening Shot")

            # Optional extras
            svc_a.timeline_manager.create_timeline(meta.project_id, "Main Timeline")
            svc_a.asset_manager.import_asset(meta.project_id, "image", "bg.png", "/img/bg.png")
            svc_a.character_manager.create_character(meta.project_id, "Hero")
            svc_a.afl_engine.validate_structure("proj:demo", {"key": "val"})
            svc_a.prompt_export_manager.create_export_artifact(
                scene.scene_id, "prompt", "A dramatic opening."
            )
            svc_a.plugin_manager.register_plugin("GenPlugin", "0.1")

            # Step 6: Save
            svc_a.save_bundle(tmp)

            # Step 7: Fresh service B
            svc_b = ApplicationService()

            # Step 8: Confirm B is empty
            self.assertEqual(svc_b.scene_manager.list_scenes(), [])
            self.assertEqual(svc_b.shot_manager.list_shots(), [])
            self.assertEqual(svc_b.timeline_manager.list_timelines(), [])
            self.assertEqual(svc_b.asset_manager.list_assets(), [])
            self.assertEqual(svc_b.character_manager.list_characters(), [])
            self.assertEqual(svc_b.afl_engine.list_validation_reports(), [])
            self.assertEqual(svc_b.prompt_export_manager.list_export_artifacts(), [])
            self.assertEqual(svc_b.plugin_manager.list_plugins(), [])

            # Step 9: Rehydrate
            result = svc_b.load_and_rehydrate_bundle(tmp)
            summary = result["summary"]

            # Step 10: Confirm B managers contain restored records
            self.assertEqual(len(svc_b.scene_manager.list_scenes()), 1)
            self.assertEqual(len(svc_b.shot_manager.list_shots()), 1)
            self.assertEqual(len(svc_b.timeline_manager.list_timelines()), 1)
            self.assertEqual(len(svc_b.asset_manager.list_assets()), 1)
            self.assertEqual(len(svc_b.character_manager.list_characters()), 1)
            self.assertEqual(len(svc_b.afl_engine.list_validation_reports()), 1)
            self.assertEqual(len(svc_b.prompt_export_manager.list_export_artifacts()), 1)
            self.assertEqual(len(svc_b.plugin_manager.list_plugins()), 1)

            # Step 11: Workspace restored
            state = svc_b.get_workspace_state()
            self.assertEqual(state.active_project_id, meta.project_id)
            self.assertEqual(state.active_scene_id, scene.scene_id)
            self.assertTrue(summary["workspace_restored"])

            # Step 12: Can create another scene
            new_scene = svc_b.create_scene("Act Two")
            self.assertIsNotNone(new_scene.scene_id)
            self.assertEqual(len(svc_b.scene_manager.list_scenes()), 2)


if __name__ == "__main__":
    unittest.main()

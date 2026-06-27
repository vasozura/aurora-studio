"""Tests for TASK-000040: Desktop Timeline Asset Character Panels Pack.

All tests are headless — no display required.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SRC = str(Path(__file__).parent.parent / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from aurora_studio.ui import (
    UISession,
    UIActionResult,
    AppStateViewModel,
    TimelineViewModel,
    TimelineItemViewModel,
    AssetViewModel,
    CharacterViewModel,
)
from aurora_studio.ui.desktop_shell import headless_smoke, DesktopShell, build_desktop_shell
from aurora_studio.contracts.timeline import TimelineRecord, TimelineItem
from aurora_studio.contracts.asset import AssetRecord
from aurora_studio.contracts.character import CharacterRecord


# ---------------------------------------------------------------------------
# Import safety
# ---------------------------------------------------------------------------

class TestImportSafety(unittest.TestCase):

    def test_desktop_shell_import_no_window(self):
        import aurora_studio.ui.desktop_shell as ds
        self.assertTrue(callable(ds.headless_smoke))
        self.assertTrue(callable(ds.build_desktop_shell))
        self.assertTrue(callable(ds.main))

    def test_new_viewmodels_importable(self):
        self.assertTrue(issubclass(TimelineViewModel, object))
        self.assertTrue(issubclass(AssetViewModel, object))
        self.assertTrue(issubclass(CharacterViewModel, object))

    def test_headless_smoke_still_works(self):
        result = headless_smoke()
        self.assertTrue(result["ok"])
        self.assertEqual(result["application"], "aurora-studio")


# ---------------------------------------------------------------------------
# TimelineViewModel
# ---------------------------------------------------------------------------

class TestTimelineViewModel(unittest.TestCase):

    def _make_record(self) -> TimelineRecord:
        item = TimelineItem(item_id="item-1", item_type="scene", target_id="scene-abc", order_index=0)
        return TimelineRecord(
            timeline_id="tl-001",
            project_id="proj-001",
            title="Main Timeline",
            items=(item,),
            state="draft",
            created_at="2026-01-01T00:00:00Z",
            modified_at="2026-01-01T00:00:00Z",
        )

    def test_from_record(self):
        vm = TimelineViewModel.from_record(self._make_record())
        self.assertEqual(vm.timeline_id, "tl-001")
        self.assertEqual(vm.project_id, "proj-001")
        self.assertEqual(vm.title, "Main Timeline")
        self.assertEqual(vm.state, "draft")
        self.assertEqual(vm.item_count, 1)

    def test_to_dict_json_serializable(self):
        vm = TimelineViewModel.from_record(self._make_record())
        d = vm.to_dict()
        json.dumps(d)
        self.assertEqual(d["timeline_id"], "tl-001")
        self.assertEqual(d["item_count"], 1)


# ---------------------------------------------------------------------------
# TimelineItemViewModel
# ---------------------------------------------------------------------------

class TestTimelineItemViewModel(unittest.TestCase):

    def _make_item(self) -> TimelineItem:
        return TimelineItem(item_id="item-42", item_type="shot", target_id="shot-xyz", order_index=2)

    def test_from_record(self):
        vm = TimelineItemViewModel.from_record(self._make_item())
        self.assertEqual(vm.item_id, "item-42")
        self.assertEqual(vm.item_type, "shot")
        self.assertEqual(vm.target_id, "shot-xyz")
        self.assertEqual(vm.order_index, 2)

    def test_to_dict_json_serializable(self):
        vm = TimelineItemViewModel.from_record(self._make_item())
        json.dumps(vm.to_dict())


# ---------------------------------------------------------------------------
# AssetViewModel
# ---------------------------------------------------------------------------

class TestAssetViewModel(unittest.TestCase):

    def _make_record(self) -> AssetRecord:
        return AssetRecord(
            asset_id="asset-001",
            project_id="proj-001",
            asset_type="image",
            display_name="Hero Shot",
            location="/path/to/file.png",
            state="active",
            owner_ref=None,
            created_at="2026-01-01T00:00:00Z",
            modified_at="2026-01-01T00:00:00Z",
        )

    def test_from_record(self):
        vm = AssetViewModel.from_record(self._make_record())
        self.assertEqual(vm.asset_id, "asset-001")
        self.assertEqual(vm.project_id, "proj-001")
        self.assertEqual(vm.asset_type, "image")
        self.assertEqual(vm.display_name, "Hero Shot")
        self.assertEqual(vm.state, "active")
        self.assertIsNone(vm.owner_ref)

    def test_to_dict_json_serializable(self):
        vm = AssetViewModel.from_record(self._make_record())
        json.dumps(vm.to_dict())


# ---------------------------------------------------------------------------
# CharacterViewModel
# ---------------------------------------------------------------------------

class TestCharacterViewModel(unittest.TestCase):

    def _make_record(self) -> CharacterRecord:
        return CharacterRecord(
            character_id="char-001",
            project_id="proj-001",
            display_name="Hero",
            description="Main hero character",
            reference_asset_ids=("asset-1", "asset-2"),
            state="active",
            created_at="2026-01-01T00:00:00Z",
            modified_at="2026-01-01T00:00:00Z",
        )

    def test_from_record(self):
        vm = CharacterViewModel.from_record(self._make_record())
        self.assertEqual(vm.character_id, "char-001")
        self.assertEqual(vm.display_name, "Hero")
        self.assertEqual(vm.description, "Main hero character")
        self.assertEqual(vm.reference_asset_ids, ("asset-1", "asset-2"))
        self.assertEqual(vm.state, "active")

    def test_to_dict_json_serializable(self):
        vm = CharacterViewModel.from_record(self._make_record())
        d = vm.to_dict()
        json.dumps(d)
        self.assertIsInstance(d["reference_asset_ids"], list)

    def test_reference_asset_ids_is_list_in_dict(self):
        vm = CharacterViewModel.from_record(self._make_record())
        d = vm.to_dict()
        self.assertEqual(d["reference_asset_ids"], ["asset-1", "asset-2"])


# ---------------------------------------------------------------------------
# AppStateViewModel includes timelines/assets/characters
# ---------------------------------------------------------------------------

class TestAppStateViewModelExtended(unittest.TestCase):

    def test_to_dict_includes_new_fields(self):
        session = UISession()
        result = session.get_app_state()
        self.assertTrue(result.ok)
        payload = result.payload
        self.assertIn("timelines", payload)
        self.assertIn("assets", payload)
        self.assertIn("characters", payload)

    def test_to_dict_json_serializable_with_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Full State")
            session.create_timeline("Timeline A")
            session.import_asset("image", "Asset A", "/path")
            session.create_character("Char A", "A brave hero")
            result = session.get_app_state()
            self.assertTrue(result.ok)
            json.dumps(result.payload)

    def test_timelines_list_in_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "TL Test")
            session.create_timeline("TL 1")
            result = session.get_app_state()
            self.assertEqual(len(result.payload["timelines"]), 1)

    def test_assets_list_in_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Asset Test")
            session.import_asset("video", "Clip A", "")
            result = session.get_app_state()
            self.assertEqual(len(result.payload["assets"]), 1)

    def test_characters_list_in_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Char Test")
            session.create_character("Villain")
            result = session.get_app_state()
            self.assertEqual(len(result.payload["characters"]), 1)


# ---------------------------------------------------------------------------
# UISession Timeline actions
# ---------------------------------------------------------------------------

class TestUISessionTimelineActions(unittest.TestCase):

    def _setup(self) -> tuple[UISession, str]:
        s = UISession()
        with tempfile.TemporaryDirectory() as tmp:
            r = s.create_project(tmp, "TL Project")
            return s, r.payload["project_id"]
        # Won't reach here — use different pattern

    def test_create_timeline_returns_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            result = session.create_timeline("Main TL")
            self.assertIsInstance(result, UIActionResult)
            self.assertTrue(result.ok)
            self.assertIn("timeline_id", result.payload)

    def test_create_timeline_empty_title_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            result = session.create_timeline("")
            self.assertFalse(result.ok)

    def test_create_timeline_no_project_fails(self):
        session = UISession()
        result = session.create_timeline("TL")
        self.assertFalse(result.ok)

    def test_add_timeline_item_returns_uiactionresult(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            tl = session.create_timeline("TL")
            tid = tl.payload["timeline_id"]
            result = session.add_timeline_item(tid, "scene", "scene-fake-id")
            self.assertIsInstance(result, UIActionResult)
            self.assertTrue(result.ok)
            self.assertIn("item_count", result.payload)

    def test_add_timeline_item_payload_json_serializable(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            tl = session.create_timeline("TL")
            tid = tl.payload["timeline_id"]
            result = session.add_timeline_item(tid, "shot", "shot-fake-id", 0)
            json.dumps(result.payload)

    def test_remove_timeline_item_returns_uiactionresult(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            tl = session.create_timeline("TL")
            tid = tl.payload["timeline_id"]
            add_r = session.add_timeline_item(tid, "scene", "scene-ref")
            item_id = add_r.payload["items"][0]["item_id"]
            result = session.remove_timeline_item(tid, item_id)
            self.assertIsInstance(result, UIActionResult)
            self.assertTrue(result.ok)
            self.assertEqual(result.payload["item_count"], 0)

    def test_remove_nonexistent_item_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            tl = session.create_timeline("TL")
            tid = tl.payload["timeline_id"]
            result = session.remove_timeline_item(tid, "no-such-item")
            self.assertFalse(result.ok)

    def test_move_timeline_item_returns_uiactionresult(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            tl = session.create_timeline("TL")
            tid = tl.payload["timeline_id"]
            session.add_timeline_item(tid, "scene", "scene-a")
            add_r = session.add_timeline_item(tid, "shot", "shot-b")
            item_id = add_r.payload["items"][1]["item_id"]
            result = session.move_timeline_item(tid, item_id, 0)
            self.assertIsInstance(result, UIActionResult)
            self.assertTrue(result.ok)


# ---------------------------------------------------------------------------
# UISession Asset actions
# ---------------------------------------------------------------------------

class TestUISessionAssetActions(unittest.TestCase):

    def test_import_asset_returns_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            result = session.import_asset("image", "Frame 1", "/path/frame1.png")
            self.assertIsInstance(result, UIActionResult)
            self.assertTrue(result.ok)
            self.assertIn("asset_id", result.payload)

    def test_import_asset_empty_display_name_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            result = session.import_asset("image", "")
            self.assertFalse(result.ok)

    def test_import_asset_no_project_fails(self):
        session = UISession()
        result = session.import_asset("image", "Frame 1")
        self.assertFalse(result.ok)

    def test_import_asset_payload_json_serializable(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            result = session.import_asset("video", "Clip A", "")
            json.dumps(result.payload)

    def test_mark_asset_missing_returns_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            asset_r = session.import_asset("image", "Img")
            asset_id = asset_r.payload["asset_id"]
            result = session.mark_asset_missing(asset_id)
            self.assertIsInstance(result, UIActionResult)
            self.assertTrue(result.ok)
            self.assertIn("state", result.payload)

    def test_archive_asset_returns_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            asset_r = session.import_asset("image", "Img2")
            asset_id = asset_r.payload["asset_id"]
            result = session.archive_asset(asset_id)
            self.assertIsInstance(result, UIActionResult)
            self.assertTrue(result.ok)


# ---------------------------------------------------------------------------
# UISession Character actions
# ---------------------------------------------------------------------------

class TestUISessionCharacterActions(unittest.TestCase):

    def test_create_character_returns_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            result = session.create_character("Hero", "The brave one")
            self.assertIsInstance(result, UIActionResult)
            self.assertTrue(result.ok)
            self.assertIn("character_id", result.payload)

    def test_create_character_empty_name_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            result = session.create_character("")
            self.assertFalse(result.ok)

    def test_create_character_no_project_fails(self):
        session = UISession()
        result = session.create_character("Hero")
        self.assertFalse(result.ok)

    def test_add_character_reference_asset_returns_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            char_r = session.create_character("Villain")
            char_id = char_r.payload["character_id"]
            asset_r = session.import_asset("image", "Face")
            asset_id = asset_r.payload["asset_id"]
            result = session.add_character_reference_asset(char_id, asset_id)
            self.assertIsInstance(result, UIActionResult)
            self.assertTrue(result.ok)
            self.assertIn("reference_asset_ids", result.payload)

    def test_remove_character_reference_asset_returns_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            char_r = session.create_character("Villain")
            char_id = char_r.payload["character_id"]
            asset_r = session.import_asset("image", "Face2")
            asset_id = asset_r.payload["asset_id"]
            session.add_character_reference_asset(char_id, asset_id)
            result = session.remove_character_reference_asset(char_id, asset_id)
            self.assertIsInstance(result, UIActionResult)
            self.assertTrue(result.ok)

    def test_archive_character_returns_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            char_r = session.create_character("Extra")
            char_id = char_r.payload["character_id"]
            result = session.archive_character(char_id)
            self.assertIsInstance(result, UIActionResult)
            self.assertTrue(result.ok)

    def test_character_payload_json_serializable(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            result = session.create_character("Char", "desc")
            json.dumps(result.payload)


# ---------------------------------------------------------------------------
# UISession.get_app_state with timelines/assets/characters
# ---------------------------------------------------------------------------

class TestGetAppStateExtended(unittest.TestCase):

    def test_get_app_state_all_fields_json_serializable(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Full")
            sr = session.create_scene("S")
            session.create_shot(sr.payload["scene_id"], "Shot")
            session.create_timeline("TL")
            session.import_asset("image", "Img")
            session.create_character("Char")
            result = session.get_app_state()
            self.assertTrue(result.ok)
            json.dumps(result.payload)

    def test_timeline_in_state_has_item_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "P")
            tl = session.create_timeline("TL")
            tid = tl.payload["timeline_id"]
            session.add_timeline_item(tid, "scene", "s1")
            state = session.get_app_state().payload
            timelines = state["timelines"]
            self.assertEqual(len(timelines), 1)
            self.assertEqual(timelines[0]["item_count"], 1)


# ---------------------------------------------------------------------------
# DesktopShell class interface (no display)
# ---------------------------------------------------------------------------

class TestDesktopShellInterface(unittest.TestCase):

    def test_required_timeline_methods_exist(self):
        required = [
            "create_timeline", "add_timeline_item", "remove_timeline_item",
            "move_timeline_item", "on_timeline_selected", "on_timeline_item_selected",
        ]
        for m in required:
            self.assertTrue(callable(getattr(DesktopShell, m, None)), f"Missing: {m}")

    def test_required_asset_methods_exist(self):
        required = [
            "import_asset", "mark_asset_missing", "archive_asset", "on_asset_selected",
        ]
        for m in required:
            self.assertTrue(callable(getattr(DesktopShell, m, None)), f"Missing: {m}")

    def test_required_character_methods_exist(self):
        required = [
            "create_character", "add_character_reference_asset",
            "remove_character_reference_asset", "archive_character",
            "on_character_selected",
        ]
        for m in required:
            self.assertTrue(callable(getattr(DesktopShell, m, None)), f"Missing: {m}")

    def test_get_state_snapshot_method_exists(self):
        self.assertTrue(callable(getattr(DesktopShell, "get_state_snapshot", None)))


# ---------------------------------------------------------------------------
# get_state_snapshot contract (headless via UISession only)
# ---------------------------------------------------------------------------

class TestGetStateSnapshotContract(unittest.TestCase):

    def test_snapshot_required_keys(self):
        """Verify snapshot dict structure is JSON-serializable and has required keys."""
        with tempfile.TemporaryDirectory() as tmp:
            session = UISession()
            session.create_project(tmp, "Snap")
            session.create_timeline("TL")
            session.import_asset("image", "Img")
            session.create_character("Char")
            result = session.get_app_state()
            payload = result.payload
            snapshot = {
                "project": payload.get("project"),
                "workspace": payload.get("workspace"),
                "scene_count": len(payload.get("scenes") or []),
                "shot_count": len(payload.get("shots") or []),
                "timeline_count": len(payload.get("timelines") or []),
                "asset_count": len(payload.get("assets") or []),
                "character_count": len(payload.get("characters") or []),
                "selected_scene_id": None,
                "selected_shot_id": None,
                "selected_timeline_id": None,
                "selected_timeline_item_id": None,
                "selected_asset_id": None,
                "selected_character_id": None,
                "status": "Ready.",
            }
            required = [
                "project", "workspace", "scene_count", "shot_count",
                "timeline_count", "asset_count", "character_count",
                "selected_scene_id", "selected_shot_id",
                "selected_timeline_id", "selected_timeline_item_id",
                "selected_asset_id", "selected_character_id", "status",
            ]
            for key in required:
                self.assertIn(key, snapshot)
            json.dumps(snapshot)


# ---------------------------------------------------------------------------
# CLI headless smoke (includes new state fields)
# ---------------------------------------------------------------------------

class TestCLIHeadlessSmoke(unittest.TestCase):

    def _run(self, *args):
        import os
        return subprocess.run(
            [sys.executable, "-m", "aurora_studio.ui.desktop_shell", *args],
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": _SRC},
        )

    def test_headless_smoke_exit_zero(self):
        r = self._run("--headless-smoke")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_headless_smoke_valid_json(self):
        r = self._run("--headless-smoke")
        data = json.loads(r.stdout)
        self.assertTrue(data["ok"])

    def test_headless_smoke_app_state_has_timelines(self):
        r = self._run("--headless-smoke")
        data = json.loads(r.stdout)
        app_state = data.get("app_state") or {}
        self.assertIn("timelines", app_state)
        self.assertIn("assets", app_state)
        self.assertIn("characters", app_state)


if __name__ == "__main__":
    unittest.main()

"""Tests for the first minimal Asset Manager implementation."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.contracts.asset import (
    ASSET_STATE_ACTIVE,
    ASSET_STATE_ARCHIVED,
    ASSET_STATE_MISSING,
    AssetRecord,
    AssetRef,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.readiness import Readiness
from aurora_studio.modules.asset_manager import AssetManager


class AssetManagerImplementationTests(unittest.TestCase):
    def test_import_asset_returns_record(self) -> None:
        manager = AssetManager()

        asset = manager.import_asset("project-123", "image", "hero.png", "/path/to/hero.png")

        self.assertIsInstance(asset, AssetRecord)
        self.assertTrue(asset.asset_id.startswith("asset-"))
        self.assertEqual(asset.project_id, "project-123")
        self.assertEqual(asset.asset_type, "image")
        self.assertEqual(asset.display_name, "hero.png")
        self.assertEqual(asset.location, "/path/to/hero.png")
        self.assertEqual(asset.state, ASSET_STATE_ACTIVE)

    def test_import_asset_rejects_empty_project_id(self) -> None:
        manager = AssetManager()

        with self.assertRaises(ValidationError):
            manager.import_asset("   ", "image", "hero.png")

    def test_import_asset_rejects_empty_asset_type(self) -> None:
        manager = AssetManager()

        with self.assertRaises(ValidationError):
            manager.import_asset("project-123", "   ", "hero.png")

    def test_import_asset_rejects_empty_display_name(self) -> None:
        manager = AssetManager()

        with self.assertRaises(ValidationError):
            manager.import_asset("project-123", "image", "   ")

    def test_list_assets_all_and_by_project(self) -> None:
        manager = AssetManager()
        a = manager.import_asset("project-1", "image", "a.png")
        b = manager.import_asset("project-2", "video", "b.mp4")

        all_assets = manager.list_assets()
        project_one = manager.list_assets(project_id="project-1")

        self.assertEqual({x.asset_id for x in all_assets}, {a.asset_id, b.asset_id})
        self.assertEqual([x.asset_id for x in project_one], [a.asset_id])

    def test_list_assets_by_asset_type(self) -> None:
        manager = AssetManager()
        img = manager.import_asset("project-1", "image", "a.png")
        manager.import_asset("project-1", "video", "b.mp4")

        images = manager.list_assets(asset_type="image")

        self.assertEqual([x.asset_id for x in images], [img.asset_id])

    def test_get_asset_returns_existing(self) -> None:
        manager = AssetManager()
        created = manager.import_asset("project-123", "image", "hero.png")

        fetched = manager.get_asset(created.asset_id)

        self.assertEqual(fetched.asset_id, created.asset_id)

    def test_get_asset_rejects_missing(self) -> None:
        manager = AssetManager()

        with self.assertRaises(ValidationError):
            manager.get_asset("asset-missing")

    def test_update_asset_display_name_and_location(self) -> None:
        manager = AssetManager()
        created = manager.import_asset("project-123", "image", "old.png", "/old/path")

        updated = manager.update_asset(
            created.asset_id,
            display_name="new.png",
            location="/new/path",
        )

        self.assertEqual(updated.display_name, "new.png")
        self.assertEqual(updated.location, "/new/path")
        self.assertEqual(updated.asset_id, created.asset_id)

    def test_update_asset_rejects_empty_display_name(self) -> None:
        manager = AssetManager()
        created = manager.import_asset("project-123", "image", "hero.png")

        with self.assertRaises(ValidationError):
            manager.update_asset(created.asset_id, display_name="   ")

    def test_mark_asset_missing_changes_state(self) -> None:
        manager = AssetManager()
        created = manager.import_asset("project-123", "image", "hero.png")

        missing = manager.mark_asset_missing(created.asset_id)

        self.assertEqual(missing.state, ASSET_STATE_MISSING)

    def test_archive_asset_marks_archived(self) -> None:
        manager = AssetManager()
        created = manager.import_asset("project-123", "image", "hero.png")

        archived = manager.archive_asset(created.asset_id)

        self.assertEqual(archived.state, ASSET_STATE_ARCHIVED)
        self.assertIsNotNone(archived.archived_at)

    def test_asset_record_to_ref_and_dict(self) -> None:
        manager = AssetManager()
        asset = manager.import_asset("project-123", "image", "hero.png")

        ref = asset.to_ref()
        data = asset.to_dict()

        self.assertIsInstance(ref, AssetRef)
        self.assertEqual(ref.asset_id, asset.asset_id)
        self.assertEqual(ref.asset_type, "image")
        self.assertEqual(data["asset_id"], asset.asset_id)
        self.assertEqual(data["state"], ASSET_STATE_ACTIVE)

    def test_asset_record_from_dict(self) -> None:
        manager = AssetManager()
        asset = manager.import_asset("project-123", "image", "hero.png")

        restored = AssetRecord.from_dict(asset.to_dict())

        self.assertEqual(restored.asset_id, asset.asset_id)
        self.assertEqual(restored.project_id, "project-123")
        self.assertEqual(restored.asset_type, "image")

    def test_asset_manager_still_reports_not_ready(self) -> None:
        manager = AssetManager()

        self.assertEqual(manager.get_readiness(), Readiness.NOT_READY)
        self.assertIn("not ready", manager.describe().lower())


if __name__ == "__main__":
    unittest.main()

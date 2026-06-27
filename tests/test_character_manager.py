"""Tests for the first minimal Character Manager implementation."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.contracts.character import (
    CHARACTER_STATE_ACTIVE,
    CHARACTER_STATE_ARCHIVED,
    CharacterRecord,
    CharacterRef,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.readiness import Readiness
from aurora_studio.modules.character_manager import CharacterManager


class CharacterManagerImplementationTests(unittest.TestCase):
    def test_create_character_returns_record(self) -> None:
        manager = CharacterManager()

        character = manager.create_character("project-123", "Elena", "Protagonist.")

        self.assertIsInstance(character, CharacterRecord)
        self.assertTrue(character.character_id.startswith("character-"))
        self.assertEqual(character.project_id, "project-123")
        self.assertEqual(character.display_name, "Elena")
        self.assertEqual(character.description, "Protagonist.")
        self.assertEqual(character.state, CHARACTER_STATE_ACTIVE)
        self.assertEqual(character.reference_asset_ids, ())

    def test_create_character_rejects_empty_project_id(self) -> None:
        manager = CharacterManager()

        with self.assertRaises(ValidationError):
            manager.create_character("   ", "Elena")

    def test_create_character_rejects_empty_display_name(self) -> None:
        manager = CharacterManager()

        with self.assertRaises(ValidationError):
            manager.create_character("project-123", "   ")

    def test_list_characters_all_and_filtered(self) -> None:
        manager = CharacterManager()
        a = manager.create_character("project-1", "Elena")
        b = manager.create_character("project-2", "Marcus")

        all_characters = manager.list_characters()
        project_one = manager.list_characters("project-1")

        self.assertEqual({c.character_id for c in all_characters}, {a.character_id, b.character_id})
        self.assertEqual([c.character_id for c in project_one], [a.character_id])

    def test_get_character_returns_existing(self) -> None:
        manager = CharacterManager()
        created = manager.create_character("project-123", "Elena")

        fetched = manager.get_character(created.character_id)

        self.assertEqual(fetched.character_id, created.character_id)

    def test_get_character_rejects_missing(self) -> None:
        manager = CharacterManager()

        with self.assertRaises(ValidationError):
            manager.get_character("character-missing")

    def test_update_character_display_name_and_description(self) -> None:
        manager = CharacterManager()
        created = manager.create_character("project-123", "Elena", "Old description")

        updated = manager.update_character(
            created.character_id,
            display_name="Elena Vasquez",
            description="Updated description",
        )

        self.assertEqual(updated.display_name, "Elena Vasquez")
        self.assertEqual(updated.description, "Updated description")
        self.assertEqual(updated.character_id, created.character_id)

    def test_update_character_rejects_empty_display_name(self) -> None:
        manager = CharacterManager()
        created = manager.create_character("project-123", "Elena")

        with self.assertRaises(ValidationError):
            manager.update_character(created.character_id, display_name="   ")

    def test_add_reference_asset_adds_asset_id(self) -> None:
        manager = CharacterManager()
        created = manager.create_character("project-123", "Elena")

        updated = manager.add_reference_asset(created.character_id, "asset-abc")

        self.assertIn("asset-abc", updated.reference_asset_ids)

    def test_add_reference_asset_prevents_duplicates(self) -> None:
        manager = CharacterManager()
        created = manager.create_character("project-123", "Elena")

        manager.add_reference_asset(created.character_id, "asset-abc")
        after_duplicate = manager.add_reference_asset(created.character_id, "asset-abc")

        self.assertEqual(after_duplicate.reference_asset_ids.count("asset-abc"), 1)

    def test_add_reference_asset_rejects_empty_asset_id(self) -> None:
        manager = CharacterManager()
        created = manager.create_character("project-123", "Elena")

        with self.assertRaises(ValidationError):
            manager.add_reference_asset(created.character_id, "   ")

    def test_remove_reference_asset_removes_asset_id(self) -> None:
        manager = CharacterManager()
        created = manager.create_character("project-123", "Elena")
        manager.add_reference_asset(created.character_id, "asset-abc")

        updated = manager.remove_reference_asset(created.character_id, "asset-abc")

        self.assertNotIn("asset-abc", updated.reference_asset_ids)

    def test_archive_character_marks_archived(self) -> None:
        manager = CharacterManager()
        created = manager.create_character("project-123", "Elena")

        archived = manager.archive_character(created.character_id)

        self.assertEqual(archived.state, CHARACTER_STATE_ARCHIVED)
        self.assertIsNotNone(archived.archived_at)

    def test_character_record_to_ref_and_dict(self) -> None:
        manager = CharacterManager()
        character = manager.create_character("project-123", "Elena")

        ref = character.to_ref()
        data = character.to_dict()

        self.assertIsInstance(ref, CharacterRef)
        self.assertEqual(ref.character_id, character.character_id)
        self.assertEqual(ref.display_name, "Elena")
        self.assertEqual(data["character_id"], character.character_id)
        self.assertEqual(data["state"], CHARACTER_STATE_ACTIVE)

    def test_character_record_from_dict(self) -> None:
        manager = CharacterManager()
        character = manager.create_character("project-123", "Elena")
        manager.add_reference_asset(character.character_id, "asset-abc")
        character = manager.get_character(character.character_id)

        restored = CharacterRecord.from_dict(character.to_dict())

        self.assertEqual(restored.character_id, character.character_id)
        self.assertEqual(restored.display_name, "Elena")
        self.assertIn("asset-abc", restored.reference_asset_ids)

    def test_character_manager_still_reports_not_ready(self) -> None:
        manager = CharacterManager()

        self.assertEqual(manager.get_readiness(), Readiness.NOT_READY)
        self.assertIn("not ready", manager.describe().lower())


if __name__ == "__main__":
    unittest.main()

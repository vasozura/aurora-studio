"""Tests for the first minimal Prompt Export Manager implementation."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.contracts.export import (
    EXPORT_STATUS_DRAFT,
    EXPORT_STATUS_FAILED,
    EXPORT_STATUS_READY,
    ExportArtifactRecord,
    ExportArtifactRef,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.readiness import Readiness
from aurora_studio.modules.prompt_export_manager import PromptExportManager


class PromptExportManagerImplementationTests(unittest.TestCase):
    def test_create_export_artifact_returns_record(self) -> None:
        manager = PromptExportManager()

        artifact = manager.create_export_artifact("scene-1", "image_prompt", "A cinematic wide shot.")

        self.assertIsInstance(artifact, ExportArtifactRecord)
        self.assertTrue(artifact.artifact_id.startswith("artifact-"))
        self.assertEqual(artifact.source_id, "scene-1")
        self.assertEqual(artifact.artifact_type, "image_prompt")
        self.assertEqual(artifact.content, "A cinematic wide shot.")
        self.assertEqual(artifact.status, EXPORT_STATUS_DRAFT)
        self.assertIsNone(artifact.provider_target)

    def test_create_export_artifact_with_provider_target(self) -> None:
        manager = PromptExportManager()

        artifact = manager.create_export_artifact(
            "scene-1", "image_prompt", "Wide shot.", provider_target="midjourney"
        )

        self.assertEqual(artifact.provider_target, "midjourney")

    def test_create_export_artifact_rejects_empty_source_id(self) -> None:
        manager = PromptExportManager()

        with self.assertRaises(ValidationError):
            manager.create_export_artifact("   ", "image_prompt", "Wide shot.")

    def test_create_export_artifact_rejects_empty_artifact_type(self) -> None:
        manager = PromptExportManager()

        with self.assertRaises(ValidationError):
            manager.create_export_artifact("scene-1", "   ", "Wide shot.")

    def test_create_export_artifact_rejects_empty_content(self) -> None:
        manager = PromptExportManager()

        with self.assertRaises(ValidationError):
            manager.create_export_artifact("scene-1", "image_prompt", "   ")

    def test_list_export_artifacts_all_and_filtered(self) -> None:
        manager = PromptExportManager()
        a = manager.create_export_artifact("scene-1", "image_prompt", "Shot A.")
        b = manager.create_export_artifact("scene-2", "image_prompt", "Shot B.")

        all_artifacts = manager.list_export_artifacts()
        scene_one = manager.list_export_artifacts("scene-1")

        self.assertEqual({x.artifact_id for x in all_artifacts}, {a.artifact_id, b.artifact_id})
        self.assertEqual([x.artifact_id for x in scene_one], [a.artifact_id])

    def test_get_export_artifact_returns_existing(self) -> None:
        manager = PromptExportManager()
        created = manager.create_export_artifact("scene-1", "image_prompt", "Wide shot.")

        fetched = manager.get_export_artifact(created.artifact_id)

        self.assertEqual(fetched.artifact_id, created.artifact_id)

    def test_get_export_artifact_rejects_missing(self) -> None:
        manager = PromptExportManager()

        with self.assertRaises(ValidationError):
            manager.get_export_artifact("artifact-missing")

    def test_mark_export_ready_changes_status(self) -> None:
        manager = PromptExportManager()
        created = manager.create_export_artifact("scene-1", "image_prompt", "Wide shot.")

        ready = manager.mark_export_ready(created.artifact_id)

        self.assertEqual(ready.status, EXPORT_STATUS_READY)

    def test_mark_export_failed_changes_status(self) -> None:
        manager = PromptExportManager()
        created = manager.create_export_artifact("scene-1", "image_prompt", "Wide shot.")

        failed = manager.mark_export_failed(created.artifact_id, "Provider timeout.")

        self.assertEqual(failed.status, EXPORT_STATUS_FAILED)
        self.assertEqual(failed.content, "Provider timeout.")

    def test_mark_export_failed_without_message_preserves_content(self) -> None:
        manager = PromptExportManager()
        created = manager.create_export_artifact("scene-1", "image_prompt", "Wide shot.")

        failed = manager.mark_export_failed(created.artifact_id)

        self.assertEqual(failed.status, EXPORT_STATUS_FAILED)
        self.assertEqual(failed.content, "Wide shot.")

    def test_artifact_to_ref_and_dict(self) -> None:
        manager = PromptExportManager()
        artifact = manager.create_export_artifact("scene-1", "image_prompt", "Wide shot.")

        ref = artifact.to_ref()
        data = artifact.to_dict()

        self.assertIsInstance(ref, ExportArtifactRef)
        self.assertEqual(ref.artifact_id, artifact.artifact_id)
        self.assertEqual(ref.source_id, "scene-1")
        self.assertEqual(data["status"], EXPORT_STATUS_DRAFT)

    def test_artifact_from_dict(self) -> None:
        manager = PromptExportManager()
        artifact = manager.create_export_artifact("scene-1", "image_prompt", "Wide shot.")

        restored = ExportArtifactRecord.from_dict(artifact.to_dict())

        self.assertEqual(restored.artifact_id, artifact.artifact_id)
        self.assertEqual(restored.source_id, "scene-1")
        self.assertEqual(restored.content, "Wide shot.")

    def test_prompt_export_manager_still_reports_not_ready(self) -> None:
        manager = PromptExportManager()

        self.assertEqual(manager.get_readiness(), Readiness.NOT_READY)
        self.assertIn("not ready", manager.describe().lower())


if __name__ == "__main__":
    unittest.main()

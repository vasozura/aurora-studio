"""Tests for the first minimal Project Manager implementation."""

from dataclasses import replace
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.contracts.project import PROJECT_FILENAME, CURRENT_PROJECT_VERSION
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.readiness import Readiness
from aurora_studio.modules.project_manager import ProjectManager


class ProjectManagerImplementationTests(unittest.TestCase):
    def test_create_project_writes_metadata_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "demo-project"
            manager = ProjectManager()

            metadata = manager.create_project(project_root, "Demo Project")

            self.assertEqual(metadata.title, "Demo Project")
            self.assertEqual(metadata.version, CURRENT_PROJECT_VERSION)
            self.assertTrue(metadata.project_id.startswith("project-"))
            self.assertTrue((project_root / PROJECT_FILENAME).exists())

    def test_open_project_reads_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "demo-project"
            manager = ProjectManager()

            created = manager.create_project(project_root, "Demo Project")
            opened = manager.open_project(project_root)

            self.assertEqual(opened.project_id, created.project_id)
            self.assertEqual(opened.title, "Demo Project")
            self.assertEqual(opened.version, CURRENT_PROJECT_VERSION)

    def test_save_project_updates_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "demo-project"
            manager = ProjectManager()

            created = manager.create_project(project_root, "Demo Project")
            changed = replace(created, title="Renamed Project")
            saved = manager.save_project(project_root, changed)
            reopened = manager.open_project(project_root)

            self.assertEqual(saved.title, "Renamed Project")
            self.assertEqual(reopened.title, "Renamed Project")
            self.assertEqual(reopened.project_id, created.project_id)

    def test_create_project_rejects_empty_title(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ProjectManager()

            with self.assertRaises(ValidationError):
                manager.create_project(Path(temp_dir) / "demo-project", "   ")

    def test_create_project_rejects_existing_project_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir) / "demo-project"
            manager = ProjectManager()

            manager.create_project(project_root, "Demo Project")

            with self.assertRaises(ValidationError):
                manager.create_project(project_root, "Another Project")

    def test_open_project_rejects_missing_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ProjectManager()

            with self.assertRaises(ValidationError):
                manager.open_project(Path(temp_dir) / "missing-project")

    def test_project_manager_still_reports_not_ready(self) -> None:
        manager = ProjectManager()

        self.assertEqual(manager.get_readiness(), Readiness.NOT_READY)
        self.assertIn("not ready", manager.describe().lower())


if __name__ == "__main__":
    unittest.main()

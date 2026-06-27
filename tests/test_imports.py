"""Import tests for Aurora Studio skeleton."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class ImportTests(unittest.TestCase):
    def test_package_imports(self) -> None:
        import aurora_studio

        self.assertEqual(aurora_studio.__version__, "0.1.0")

    def test_module_imports(self) -> None:
        from aurora_studio.modules import (
            AFLEngine,
            AssetManager,
            CharacterManager,
            PluginManager,
            ProjectManager,
            PromptExportManager,
            SceneManager,
            ShotManager,
            TimelineManager,
            Workspace,
        )

        classes = [
            ProjectManager,
            Workspace,
            SceneManager,
            ShotManager,
            TimelineManager,
            AssetManager,
            CharacterManager,
            AFLEngine,
            PromptExportManager,
            PluginManager,
        ]
        self.assertTrue(all(callable(cls) for cls in classes))

    def test_contract_imports(self) -> None:
        from aurora_studio.contracts import (
            AFLValidationReport,
            AssetRef,
            CharacterRef,
            ExportArtifactRef,
            PluginMetadata,
            ProjectMetadata,
            SceneRef,
            ShotRef,
            ValidationIssue,
            ValidationReport,
            WorkspaceState,
        )

        classes = [
            ProjectMetadata,
            WorkspaceState,
            SceneRef,
            ShotRef,
            AssetRef,
            CharacterRef,
            AFLValidationReport,
            ExportArtifactRef,
            PluginMetadata,
            ValidationIssue,
            ValidationReport,
        ]
        self.assertTrue(all(callable(cls) for cls in classes))


if __name__ == "__main__":
    unittest.main()

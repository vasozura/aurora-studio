"""Module boundary tests for Aurora Studio skeleton."""

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aurora_studio.core.readiness import Readiness
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


class ModuleBoundaryTests(unittest.TestCase):
    def test_all_modules_report_not_ready(self) -> None:
        modules = [
            ProjectManager(),
            Workspace(),
            SceneManager(),
            ShotManager(),
            TimelineManager(),
            AssetManager(),
            CharacterManager(),
            AFLEngine(),
            PromptExportManager(),
            PluginManager(),
        ]

        for module in modules:
            with self.subTest(module=module.module_name):
                self.assertEqual(module.get_readiness(), Readiness.NOT_READY)

    def test_modules_have_names(self) -> None:
        module = ProjectManager()
        self.assertEqual(module.module_name, "Project Manager")
        self.assertIn("not ready", module.describe().lower())


if __name__ == "__main__":
    unittest.main()

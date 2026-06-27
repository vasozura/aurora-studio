"""Tests for aurora_studio.cli smoke tool — TASK-000033."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
SRC = ROOT / "src"


def _run(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess:
    """Run the CLI via subprocess with PYTHONPATH set to src."""
    import os
    env = {**os.environ, "PYTHONPATH": str(SRC), "PYTHONPYCACHEPREFIX": "/tmp/pycache"}
    return subprocess.run(
        [sys.executable, "-m", "aurora_studio.cli", *args],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCliHelp(unittest.TestCase):

    def test_help_exits_zero(self):
        result = _run("--help")
        self.assertEqual(result.returncode, 0)

    def test_help_mentions_commands(self):
        result = _run("--help")
        self.assertIn("smoke", result.stdout)
        self.assertIn("create-project", result.stdout)
        self.assertIn("create-demo", result.stdout)
        self.assertIn("inspect-bundle", result.stdout)

    def test_help_creates_no_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("--help", cwd=Path(tmp))
            self.assertEqual(result.returncode, 0)
            files = list(Path(tmp).iterdir())
            self.assertEqual(files, [])

    def test_no_command_exits_zero(self):
        result = _run()
        self.assertEqual(result.returncode, 0)


class TestCliSmoke(unittest.TestCase):

    def test_smoke_exits_zero(self):
        result = _run("smoke")
        self.assertEqual(result.returncode, 0)

    def test_smoke_outputs_valid_json(self):
        result = _run("smoke")
        data = json.loads(result.stdout)
        self.assertIsInstance(data, dict)

    def test_smoke_json_keys(self):
        result = _run("smoke")
        data = json.loads(result.stdout)
        self.assertIn("ok", data)
        self.assertIn("application", data)
        self.assertIn("mode", data)

    def test_smoke_ok_is_true(self):
        result = _run("smoke")
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])

    def test_smoke_application_value(self):
        result = _run("smoke")
        data = json.loads(result.stdout)
        self.assertEqual(data["application"], "aurora-studio")


class TestCliCreateProject(unittest.TestCase):

    def test_create_project_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("create-project", "--path", tmp, "--title", "Test Project")
            self.assertEqual(result.returncode, 0)

    def test_create_project_outputs_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("create-project", "--path", tmp, "--title", "Test Project")
            data = json.loads(result.stdout)
            self.assertIsInstance(data, dict)

    def test_create_project_required_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("create-project", "--path", tmp, "--title", "Test Project")
            data = json.loads(result.stdout)
            for key in ("project_id", "title", "version", "created_at", "modified_at"):
                self.assertIn(key, data)

    def test_create_project_title_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("create-project", "--path", tmp, "--title", "My Film")
            data = json.loads(result.stdout)
            self.assertEqual(data["title"], "My Film")

    def test_create_project_empty_title_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("create-project", "--path", tmp, "--title", "")
            self.assertNotEqual(result.returncode, 0)

    def test_create_project_error_json_to_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("create-project", "--path", tmp, "--title", "")
            err_data = json.loads(result.stderr)
            self.assertIn("ok", err_data)
            self.assertFalse(err_data["ok"])
            self.assertIn("error", err_data)


class TestCliCreateDemo(unittest.TestCase):

    def test_create_demo_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("create-demo", "--path", tmp, "--title", "Demo")
            self.assertEqual(result.returncode, 0)

    def test_create_demo_outputs_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("create-demo", "--path", tmp, "--title", "Demo")
            data = json.loads(result.stdout)
            self.assertIsInstance(data, dict)

    def test_create_demo_required_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("create-demo", "--path", tmp, "--title", "Demo")
            data = json.loads(result.stdout)
            for key in ("project_id", "scene_id", "shot_id", "bundle_path"):
                self.assertIn(key, data)

    def test_create_demo_bundle_file_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("create-demo", "--path", tmp, "--title", "Demo")
            data = json.loads(result.stdout)
            self.assertTrue(Path(data["bundle_path"]).exists())

    def test_create_demo_ids_are_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = _run("create-demo", "--path", tmp, "--title", "Demo")
            data = json.loads(result.stdout)
            self.assertIsInstance(data["project_id"], str)
            self.assertIsInstance(data["scene_id"], str)
            self.assertIsInstance(data["shot_id"], str)


class TestCliInspectBundle(unittest.TestCase):

    def _create_demo(self, tmp: str) -> dict:
        result = _run("create-demo", "--path", tmp, "--title", "Inspect Test")
        return json.loads(result.stdout)

    def test_inspect_bundle_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._create_demo(tmp)
            result = _run("inspect-bundle", "--path", tmp)
            self.assertEqual(result.returncode, 0)

    def test_inspect_bundle_outputs_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._create_demo(tmp)
            result = _run("inspect-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertIsInstance(data, dict)

    def test_inspect_bundle_required_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._create_demo(tmp)
            result = _run("inspect-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            for key in ("schema_version", "scene_count", "shot_count",
                        "timeline_count", "asset_count", "character_count",
                        "afl_report_count", "export_artifact_count", "plugin_count"):
                self.assertIn(key, data)

    def test_inspect_bundle_counts_match_demo(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._create_demo(tmp)
            result = _run("inspect-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            self.assertEqual(data["scene_count"], 1)
            self.assertEqual(data["shot_count"], 1)

    def test_inspect_bundle_counts_are_ints(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._create_demo(tmp)
            result = _run("inspect-bundle", "--path", tmp)
            data = json.loads(result.stdout)
            for key in ("scene_count", "shot_count", "timeline_count"):
                self.assertIsInstance(data[key], int)

    def test_inspect_bundle_missing_path_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_path = str(Path(tmp) / "nonexistent")
            result = _run("inspect-bundle", "--path", bad_path)
            self.assertNotEqual(result.returncode, 0)

    def test_inspect_bundle_error_json_to_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_path = str(Path(tmp) / "nonexistent")
            result = _run("inspect-bundle", "--path", bad_path)
            err_data = json.loads(result.stderr)
            self.assertFalse(err_data["ok"])
            self.assertIn("error", err_data)


if __name__ == "__main__":
    unittest.main()

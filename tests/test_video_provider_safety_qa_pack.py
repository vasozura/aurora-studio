"""TASK-000120: Video Provider Safety QA Pack.

Source-level and behavioral safety checks for the v0.4 video provider stack.
No network calls. No video files. No ffmpeg. Standard library only.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"
AURORA_SRC = SRC / "aurora_studio"
DOCS = Path(__file__).parent.parent / "docs" / "v0_4"


class TestVideoProviderDocsExist(unittest.TestCase):

    def test_safety_boundary_doc_exists(self):
        self.assertTrue((DOCS / "VIDEO_PROVIDER_SAFETY_BOUNDARY.md").exists())

    def test_escalation_rules_doc_exists(self):
        self.assertTrue((DOCS / "VIDEO_PROVIDER_ESCALATION_RULES.md").exists())

    def test_qa_checklist_doc_exists(self):
        self.assertTrue((DOCS / "VIDEO_PROVIDER_ADAPTER_QA_CHECKLIST.md").exists())

    def test_security_review_doc_exists(self):
        self.assertTrue((DOCS / "VIDEO_PROVIDER_SECURITY_REVIEW.md").exists())

    def test_user_warning_doc_exists(self):
        self.assertTrue((DOCS / "REAL_VIDEO_PROVIDER_USER_WARNING.md").exists())


class TestVideoProviderDocContent(unittest.TestCase):

    def _boundary(self):
        return (DOCS / "VIDEO_PROVIDER_SAFETY_BOUNDARY.md").read_text(encoding="utf-8")

    def _warning(self):
        return (DOCS / "REAL_VIDEO_PROVIDER_USER_WARNING.md").read_text(encoding="utf-8")

    def _checklist(self):
        return (DOCS / "VIDEO_PROVIDER_ADAPTER_QA_CHECKLIST.md").read_text(encoding="utf-8")

    def test_boundary_states_real_video_blocked_by_default(self):
        self.assertIn("Real video provider execution is blocked", self._boundary())

    def test_boundary_states_no_video_generation(self):
        self.assertIn("does not generate videos", self._boundary())

    def test_boundary_states_no_upload(self):
        self.assertIn("does not upload files or assets", self._boundary())

    def test_boundary_states_no_media_decoding(self):
        self.assertIn("does not decode or process local media", self._boundary())

    def test_boundary_states_no_ffmpeg(self):
        self.assertIn("does not execute ffmpeg", self._boundary())

    def test_boundary_states_no_sdks(self):
        self.assertIn("does not add provider SDKs", self._boundary())

    def test_checklist_states_secrets_not_persisted(self):
        self.assertIn("Secrets are not persisted or logged", self._checklist())

    def test_checklist_states_no_network_in_tests(self):
        self.assertIn("Automated tests must not perform real network calls", self._checklist())

    def test_checklist_states_no_video_files_in_tests(self):
        self.assertIn("Automated tests must not create video files", self._checklist())

    def test_warning_states_prompt_may_leave_machine(self):
        self.assertIn("may send prompt text outside this machine", self._warning())

    def test_warning_states_reference_media_risk(self):
        self.assertIn("those files may also be sent outside this machine", self._warning())

    def test_warning_states_do_not_send_confidential(self):
        self.assertIn("Do not send confidential", self._warning())

    def test_warning_states_api_keys_not_saved(self):
        self.assertIn("API keys are not saved", self._warning())

    def test_warning_states_user_responsibility(self):
        self.assertIn("user's responsibility", self._warning())


class TestVideoProviderNoForbiddenImports(unittest.TestCase):

    def _source_files(self):
        return list(AURORA_SRC.rglob("*.py"))

    def test_no_pil_import(self):
        for f in self._source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import PIL", src, f"PIL import in {f}")
            self.assertNotIn("from PIL", src, f"PIL import in {f}")

    def test_no_cv2_import(self):
        for f in self._source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import cv2", src, f"cv2 import in {f}")

    def test_no_moviepy_import(self):
        for f in self._source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import moviepy", src, f"moviepy import in {f}")
            self.assertNotIn("from moviepy", src, f"moviepy import in {f}")

    def test_no_requests_import(self):
        for f in self._source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import requests", src, f"requests import in {f}")

    def test_no_httpx_import(self):
        for f in self._source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import httpx", src, f"httpx import in {f}")

    def test_no_aiohttp_import(self):
        for f in self._source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("import aiohttp", src, f"aiohttp import in {f}")

    def _video_source_files(self):
        """Only video provider modules for stricter subprocess/ffmpeg checks."""
        return [
            f for f in AURORA_SRC.rglob("*.py")
            if "video" in f.name.lower()
        ]

    def test_no_ffmpeg_in_video_modules(self):
        # Only flag actual import/call lines, not docstring or comment mentions
        for f in self._video_source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            for ln in src.splitlines():
                stripped = ln.strip()
                if stripped.startswith("#"):
                    continue
                self.assertNotIn("import ffmpeg", ln, f"import ffmpeg in {f}")
                self.assertNotIn("import ffprobe", ln, f"import ffprobe in {f}")

    def test_no_subprocess_in_video_modules(self):
        # Only flag import/call lines, not docstring mentions
        for f in self._video_source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            for ln in src.splitlines():
                stripped = ln.strip()
                if stripped.startswith("#"):
                    continue
                self.assertNotIn("import subprocess", ln,
                                 f"import subprocess in {f}: {ln}")
                self.assertNotIn("subprocess.run", ln,
                                 f"subprocess.run in {f}: {ln}")
                self.assertNotIn("subprocess.Popen", ln,
                                 f"subprocess.Popen in {f}: {ln}")

    def test_no_os_system_in_video_modules(self):
        for f in self._video_source_files():
            src = f.read_text(encoding="utf-8", errors="ignore")
            self.assertNotIn("os.system", src, f"os.system in {f}")

    def test_no_forbidden_sdk_at_runtime(self):
        sys.path.insert(0, str(SRC))
        import aurora_studio.modules.mock_video_provider_adapter as _  # noqa: F401
        top_level = {mod.split(".")[0] for mod in sys.modules}
        for forbidden in {"PIL", "cv2", "moviepy", "requests", "httpx", "aiohttp", "openai", "anthropic"}:
            self.assertNotIn(forbidden, top_level,
                             f"Forbidden module '{forbidden}' in sys.modules")


class TestVideoGateSafety(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.provider_execution_gate import VideoProviderExecutionGate
        self.gate = VideoProviderExecutionGate()

    def test_real_video_never_allowed(self):
        decision = self.gate.evaluate_real_video("any-provider")
        self.assertFalse(decision.allowed)

    def test_mock_video_always_allowed(self):
        decision = self.gate.evaluate_mock_video("mock-video")
        self.assertTrue(decision.allowed)

    def test_real_video_prerequisites_present(self):
        prereqs = self.gate.list_real_video_prerequisites()
        self.assertGreater(len(prereqs), 0)

    def test_all_prerequisites_unsatisfied(self):
        prereqs = self.gate.list_real_video_prerequisites()
        for p in prereqs:
            self.assertFalse(p.satisfied)

    def test_gate_decision_json_serializable(self):
        decision = self.gate.evaluate_real_video("mock-video")
        serialized = json.dumps(decision.to_dict())
        parsed = json.loads(serialized)
        self.assertFalse(parsed["allowed"])


class TestMockAdapterSafety(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.mock_video_provider_adapter import MockVideoProviderAdapter
        from aurora_studio.contracts.video_provider import VideoProviderRequest
        self.adapter = MockVideoProviderAdapter()
        self.Request = VideoProviderRequest

    def _req(self, mode="mock_video"):
        return self.Request(
            request_id="r1", provider_id="mock-video",
            mode=mode, prompt_text="A timelapse"
        )

    def test_mock_no_network(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertFalse(resp.network_call)

    def test_mock_is_mock_response(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertTrue(resp.mock_response)

    def test_real_video_blocked(self):
        resp = self.adapter.execute(self._req(mode="real_video"), secret_value="fake")
        self.assertEqual(resp.status, "blocked")

    def test_no_video_file_written(self):
        before = set(os.listdir(tempfile.gettempdir()))
        self.adapter.execute_mock(self._req())
        after = set(os.listdir(tempfile.gettempdir()))
        for fname in (after - before):
            for ext in (".mp4", ".mov", ".webm", ".avi", ".mkv"):
                self.assertFalse(fname.endswith(ext))

    def test_video_uri_mock_scheme(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertTrue(resp.video_uri.startswith("mock://"))

    def test_response_json_serializable(self):
        resp = self.adapter.execute_mock(self._req())
        serialized = json.dumps(resp.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["status"], "mock")

    def test_response_no_secret_keys(self):
        resp = self.adapter.execute_mock(self._req())
        d = resp.to_dict()
        for bad in ("api_key", "secret", "token", "password"):
            self.assertNotIn(bad, d)


class TestCLISmokeVideoProvider(unittest.TestCase):

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "aurora_studio.cli.main"] + list(args),
            capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(SRC)},
        )

    def test_video_provider_mock_exits_zero(self):
        r = self._run("video-provider-mock", "--provider", "mock-video",
                      "--prompt", "QA test prompt")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_video_provider_mock_status_mock(self):
        r = self._run("video-provider-mock", "--provider", "mock-video",
                      "--prompt", "QA test prompt")
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["status"], "mock")

    def test_video_provider_mock_no_secret_in_stdout(self):
        r = self._run("video-provider-mock", "--provider", "mock-video",
                      "--prompt", "QA test prompt")
        self.assertNotIn("api_key", r.stdout)
        self.assertNotIn("sk-", r.stdout)

    def test_video_provider_readiness_exits_zero(self):
        r = self._run("video-provider-readiness", "--provider", "mock-video")
    def test_video_provider_readiness_exits_zero(self):
        r = self._run("video-provider-readiness", "--provider", "mock-video")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_video_provider_readiness_always_blocked(self):
        r = self._run("video-provider-readiness", "--provider", "mock-video")
        parsed = json.loads(r.stdout)
        self.assertFalse(parsed["real_video_execution_ready"])

    def test_smoke_command_still_passes(self):
        r = self._run("smoke")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_image_provider_mock_still_works(self):
        r = self._run("image-provider-mock", "--provider", "mock-image",
                      "--prompt", "QA regression check")
        self.assertEqual(r.returncode, 0, r.stderr)
        parsed = json.loads(r.stdout)
        self.assertEqual(parsed["status"], "mock")


if __name__ == "__main__":
    unittest.main()

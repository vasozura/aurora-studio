"""TASK-000117: Video Provider Request/Response Contracts tests.

No network. No video files. Standard library only.
"""

import json
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"


class TestVideoProviderRequest(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.contracts.video_provider import VideoProviderRequest
        self.Request = VideoProviderRequest

    def _req(self, **kwargs):
        defaults = dict(
            request_id="r1", provider_id="mock-video",
            mode="mock_video", prompt_text="A sunset timelapse"
        )
        defaults.update(kwargs)
        return self.Request(**defaults)

    def test_request_json_serializable(self):
        req = self._req()
        serialized = json.dumps(req.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["provider_id"], "mock-video")

    def test_request_frozen(self):
        req = self._req()
        with self.assertRaises(AttributeError):
            req.prompt_text = "changed"

    def test_empty_prompt_fails_validation(self):
        from aurora_studio.modules.video_provider_adapter import validate_video_provider_request
        req = self._req(prompt_text="")
        errors = validate_video_provider_request(req)
        self.assertIn("prompt_empty", errors)

    def test_empty_provider_fails_validation(self):
        from aurora_studio.modules.video_provider_adapter import validate_video_provider_request
        req = self._req(provider_id="")
        errors = validate_video_provider_request(req)
        self.assertIn("provider_id_missing", errors)

    def test_invalid_mode_fails_validation(self):
        from aurora_studio.modules.video_provider_adapter import validate_video_provider_request
        req = self._req(mode="invalid_mode")
        errors = validate_video_provider_request(req)
        self.assertIn("execution_mode_invalid", errors)

    def test_valid_request_no_errors(self):
        from aurora_studio.modules.video_provider_adapter import validate_video_provider_request
        req = self._req()
        errors = validate_video_provider_request(req)
        self.assertEqual(errors, [])

    def test_parameters_json_serializable(self):
        req = self._req(parameters=(("width", 1280), ("height", 720)))
        d = req.to_dict()
        json.dumps(d)  # must not raise

    def test_forbidden_parameter_keys_rejected(self):
        from aurora_studio.modules.video_provider_adapter import validate_video_provider_request
        req = self._req(parameters=(("video_bytes", "abc"),))
        errors = validate_video_provider_request(req)
        self.assertIn("forbidden_parameter_keys", errors)

    def test_forbidden_api_key_parameter_rejected(self):
        from aurora_studio.modules.video_provider_adapter import validate_video_provider_request
        req = self._req(parameters=(("api_key", "sk-abc"),))
        errors = validate_video_provider_request(req)
        self.assertIn("forbidden_parameter_keys", errors)

    def test_to_dict_no_secret_fields(self):
        req = self._req()
        d = req.to_dict()
        for bad in ("api_key", "secret", "token", "password", "video_bytes"):
            self.assertNotIn(bad, d)

    def test_to_json_no_binary(self):
        req = self._req()
        j = req.to_json()
        self.assertNotIn("video_bytes", j)
        self.assertNotIn("video_base64", j)


class TestVideoProviderResponse(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.contracts.video_provider import VideoProviderResponse
        self.Response = VideoProviderResponse

    def _resp(self, **kwargs):
        defaults = dict(
            response_id="resp1", request_id="r1",
            provider_id="mock-video", mode="mock_video", status="mock"
        )
        defaults.update(kwargs)
        return self.Response(**defaults)

    def test_response_json_serializable(self):
        resp = self._resp()
        serialized = json.dumps(resp.to_dict())
        parsed = json.loads(serialized)
        self.assertEqual(parsed["status"], "mock")

    def test_response_frozen(self):
        resp = self._resp()
        with self.assertRaises(AttributeError):
            resp.status = "changed"

    def test_raw_response_preview_truncated(self):
        long_preview = "x" * 500
        resp = self._resp(raw_response_preview=long_preview)
        d = resp.to_dict()
        self.assertLessEqual(len(d["raw_response_preview"]), 200)

    def test_response_no_secret_fields(self):
        resp = self._resp()
        d = resp.to_dict()
        for bad in ("api_key", "secret", "token", "password", "video_bytes"):
            self.assertNotIn(bad, d)

    def test_video_uri_field_exists(self):
        resp = self._resp(video_uri="mock://video/r1")
        self.assertEqual(resp.video_uri, "mock://video/r1")

    def test_job_id_field_exists(self):
        resp = self._resp(job_id="mock-job-r1")
        self.assertEqual(resp.job_id, "mock-job-r1")

    def test_network_call_default_false(self):
        resp = self._resp()
        self.assertFalse(resp.network_call)

    def test_mock_response_field(self):
        resp = self._resp(mock_response=True)
        self.assertTrue(resp.mock_response)


class TestVideoProviderAdapterBase(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.video_provider_adapter import VideoProviderAdapter
        from aurora_studio.contracts.video_provider import VideoProviderRequest
        self.adapter = VideoProviderAdapter()
        self.Request = VideoProviderRequest

    def _req(self, mode="mock_video"):
        return self.Request(
            request_id="r1", provider_id="mock-video",
            mode=mode, prompt_text="A sunset timelapse"
        )

    def test_base_execute_mock_returns_mock_status(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertEqual(resp.status, "mock")

    def test_base_execute_mock_no_network(self):
        resp = self.adapter.execute_mock(self._req())
        self.assertFalse(resp.network_call)

    def test_base_execute_real_video_blocked(self):
        resp = self.adapter.execute_real_video(self._req("real_video"), "fake")
        self.assertEqual(resp.status, "blocked")

    def test_base_execute_routes_mock(self):
        resp = self.adapter.execute(self._req("mock_video"))
        self.assertEqual(resp.status, "mock")

    def test_base_execute_routes_real_blocked(self):
        resp = self.adapter.execute(self._req("real_video"), "fake")
        self.assertEqual(resp.status, "blocked")

    def test_base_execute_invalid_prompt_invalid_request(self):
        req = self.Request(
            request_id="r1", provider_id="mock-video",
            mode="mock_video", prompt_text=""
        )
        resp = self.adapter.execute_mock(req)
        self.assertEqual(resp.status, "invalid_request")

    def test_sanitize_response_payload_removes_secrets(self):
        payload = {"status": "mock", "api_key": "sk-abc", "video_uri": "mock://video/r1"}
        safe = self.adapter.sanitize_response_payload(payload)
        self.assertNotIn("api_key", safe)
        self.assertIn("status", safe)

    def test_sanitize_response_payload_truncates_preview(self):
        payload = {"raw_response_preview": "x" * 500}
        safe = self.adapter.sanitize_response_payload(payload)
        self.assertLessEqual(len(safe["raw_response_preview"]), 200)


class TestForbiddenParameterKeys(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.contracts.video_provider import FORBIDDEN_PARAMETER_KEYS
        self.forbidden = FORBIDDEN_PARAMETER_KEYS

    def test_video_bytes_forbidden(self):
        self.assertIn("video_bytes", self.forbidden)

    def test_video_base64_forbidden(self):
        self.assertIn("video_base64", self.forbidden)

    def test_audio_bytes_forbidden(self):
        self.assertIn("audio_bytes", self.forbidden)

    def test_audio_base64_forbidden(self):
        self.assertIn("audio_base64", self.forbidden)

    def test_reference_video_base64_forbidden(self):
        self.assertIn("reference_video_base64", self.forbidden)

    def test_api_key_forbidden(self):
        self.assertIn("api_key", self.forbidden)

    def test_secret_forbidden(self):
        self.assertIn("secret", self.forbidden)


if __name__ == "__main__":
    unittest.main()

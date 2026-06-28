"""Tests for TASK-000112: Image Provider Request/Response Contract Pack.

No network calls. No image generation. No image files. Standard library only.
"""

import json
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"


class TestImageProviderRequest(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.contracts.image_provider import ImageProviderRequest
        self.cls = ImageProviderRequest

    def test_basic_instantiation(self):
        r = self.cls(request_id="r1", provider_id="mock-image", mode="mock_image",
                     prompt_text="A sunset")
        self.assertEqual(r.prompt_text, "A sunset")

    def test_to_dict(self):
        r = self.cls(request_id="r1", provider_id="mock-image", mode="mock_image",
                     prompt_text="A sunset")
        d = r.to_dict()
        self.assertEqual(d["prompt_text"], "A sunset")
        self.assertEqual(d["mode"], "mock_image")

    def test_to_json_serializable(self):
        r = self.cls(request_id="r1", provider_id="mock-image", mode="mock_image",
                     prompt_text="A sunset")
        parsed = json.loads(r.to_json())
        self.assertEqual(parsed["provider_id"], "mock-image")

    def test_from_dict_roundtrip(self):
        r = self.cls(request_id="r1", provider_id="mock-image", mode="mock_image",
                     prompt_text="A sunset", negative_prompt_text="blurry")
        r2 = self.cls.from_dict(r.to_dict())
        self.assertEqual(r2.prompt_text, "A sunset")
        self.assertEqual(r2.negative_prompt_text, "blurry")

    def test_parameters_as_dict(self):
        r = self.cls(request_id="r1", provider_id="mock-image", mode="mock_image",
                     prompt_text="test", parameters=(("steps", 30), ("cfg", 7.5)))
        d = r.parameters_as_dict()
        self.assertEqual(d["steps"], 30)

    def test_no_secret_fields_in_to_dict(self):
        r = self.cls(request_id="r1", provider_id="mock-image", mode="mock_image",
                     prompt_text="test")
        d = r.to_dict()
        secret_keys = {"api_key", "secret", "token", "password", "authorization"}
        self.assertTrue(secret_keys.isdisjoint(d.keys()))

    def test_no_image_bytes_in_to_dict(self):
        r = self.cls(request_id="r1", provider_id="mock-image", mode="mock_image",
                     prompt_text="test")
        d = r.to_dict()
        forbidden = {"image_bytes", "image_base64", "mask_base64", "reference_image_base64"}
        self.assertTrue(forbidden.isdisjoint(d.keys()))

    def test_frozen(self):
        r = self.cls(request_id="r1", provider_id="mock-image", mode="mock_image",
                     prompt_text="test")
        with self.assertRaises((AttributeError, TypeError)):
            r.prompt_text = "changed"


class TestImageProviderResponse(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.contracts.image_provider import ImageProviderResponse
        self.cls = ImageProviderResponse

    def test_basic_instantiation(self):
        r = self.cls(response_id="rsp1", request_id="r1", provider_id="mock-image",
                     mode="mock_image", status="mock")
        self.assertEqual(r.status, "mock")

    def test_to_dict(self):
        r = self.cls(response_id="rsp1", request_id="r1", provider_id="mock-image",
                     mode="mock_image", status="mock", image_uri="mock://image/r1")
        d = r.to_dict()
        self.assertEqual(d["image_uri"], "mock://image/r1")
        self.assertFalse(d["network_call"])

    def test_to_json_serializable(self):
        r = self.cls(response_id="rsp1", request_id="r1", provider_id="mock-image",
                     mode="mock_image", status="mock")
        parsed = json.loads(r.to_json())
        self.assertEqual(parsed["status"], "mock")

    def test_no_secret_fields_in_to_dict(self):
        r = self.cls(response_id="rsp1", request_id="r1", provider_id="mock-image",
                     mode="mock_image", status="mock")
        d = r.to_dict()
        secret_keys = {"api_key", "secret", "token", "password", "authorization"}
        self.assertTrue(secret_keys.isdisjoint(d.keys()))

    def test_frozen(self):
        r = self.cls(response_id="rsp1", request_id="r1", provider_id="mock-image",
                     mode="mock_image", status="mock")
        with self.assertRaises((AttributeError, TypeError)):
            r.status = "changed"

    def test_mock_image_uri_scheme(self):
        r = self.cls(response_id="rsp1", request_id="r1", provider_id="mock-image",
                     mode="mock_image", status="mock", image_uri="mock://image/r1")
        self.assertTrue(r.image_uri.startswith("mock://"))


class TestImageValidation(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.image_provider_adapter import (
            validate_image_provider_request,
            validate_image_provider_parameters,
        )
        from aurora_studio.contracts.image_provider import ImageProviderRequest
        self.validate_request = validate_image_provider_request
        self.validate_params = validate_image_provider_parameters
        self.Request = ImageProviderRequest

    def test_valid_request_no_errors(self):
        r = self.Request(request_id="r1", provider_id="mock-image", mode="mock_image",
                         prompt_text="A sunset over mountains")
        self.assertEqual(self.validate_request(r), [])

    def test_empty_prompt_error(self):
        r = self.Request(request_id="r1", provider_id="mock-image", mode="mock_image",
                         prompt_text="")
        self.assertIn("prompt_empty", self.validate_request(r))

    def test_whitespace_prompt_error(self):
        r = self.Request(request_id="r1", provider_id="mock-image", mode="mock_image",
                         prompt_text="   ")
        self.assertIn("prompt_empty", self.validate_request(r))

    def test_missing_provider_id_error(self):
        r = self.Request(request_id="r1", provider_id="", mode="mock_image",
                         prompt_text="A sunset")
        self.assertIn("provider_id_missing", self.validate_request(r))

    def test_invalid_mode_error(self):
        r = self.Request(request_id="r1", provider_id="mock-image", mode="bogus",
                         prompt_text="A sunset")
        self.assertIn("mode_invalid", self.validate_request(r))

    def test_prompt_too_long(self):
        from aurora_studio.contracts.image_provider import MAX_IMAGE_PROMPT_LENGTH
        r = self.Request(request_id="r1", provider_id="mock-image", mode="mock_image",
                         prompt_text="a" * (MAX_IMAGE_PROMPT_LENGTH + 1))
        self.assertIn("prompt_too_long", self.validate_request(r))

    def test_forbidden_key_rejected(self):
        errors = self.validate_params({"image_base64": "abc"})
        self.assertIn("parameters_contain_forbidden_key", errors)

    def test_api_key_in_params_rejected(self):
        errors = self.validate_params({"api_key": "sk-123"})
        self.assertIn("parameters_contain_forbidden_key", errors)

    def test_valid_parameters_ok(self):
        errors = self.validate_params({"steps": 30, "cfg_scale": 7.5, "seed": 42})
        self.assertEqual(errors, [])

    def test_non_serializable_params_rejected(self):
        errors = self.validate_params({"fn": lambda x: x})
        self.assertIn("parameters_not_serializable", errors)


class TestImageProviderAdapterBase(unittest.TestCase):

    def setUp(self):
        sys.path.insert(0, str(SRC))
        from aurora_studio.modules.image_provider_adapter import ImageProviderAdapter
        from aurora_studio.contracts.image_provider import ImageProviderRequest
        self.adapter = ImageProviderAdapter()
        self.Request = ImageProviderRequest

    def test_execute_mock_returns_mock_status(self):
        r = self.Request(request_id="r1", provider_id="mock-image", mode="mock_image",
                         prompt_text="A sunset")
        resp = self.adapter.execute_mock(r)
        self.assertEqual(resp.status, "mock")

    def test_execute_mock_no_network(self):
        r = self.Request(request_id="r1", provider_id="mock-image", mode="mock_image",
                         prompt_text="A sunset")
        resp = self.adapter.execute_mock(r)
        self.assertFalse(resp.network_call)

    def test_execute_mock_image_uri_scheme(self):
        r = self.Request(request_id="r1", provider_id="mock-image", mode="mock_image",
                         prompt_text="A sunset")
        resp = self.adapter.execute_mock(r)
        self.assertTrue(resp.image_uri.startswith("mock://"))

    def test_execute_real_image_blocked_in_base(self):
        r = self.Request(request_id="r1", provider_id="mock-image", mode="real_image",
                         prompt_text="A sunset")
        resp = self.adapter.execute_real_image(r, secret_value="fake")
        self.assertEqual(resp.status, "blocked")
        self.assertFalse(resp.network_call)

    def test_execute_routes_mock_image(self):
        r = self.Request(request_id="r1", provider_id="mock-image", mode="mock_image",
                         prompt_text="A sunset")
        resp = self.adapter.execute(r)
        self.assertEqual(resp.status, "mock")

    def test_execute_routes_real_image_blocked(self):
        r = self.Request(request_id="r1", provider_id="mock-image", mode="real_image",
                         prompt_text="A sunset")
        resp = self.adapter.execute(r)
        self.assertEqual(resp.status, "blocked")

    def test_execute_blocked_real_image(self):
        r = self.Request(request_id="r1", provider_id="mock-image",
                         mode="blocked_real_image", prompt_text="A sunset")
        resp = self.adapter.execute(r)
        self.assertEqual(resp.status, "blocked")

    def test_sanitize_response_payload_redacts_secret(self):
        payload = {"status": "mock", "api_key": "sk-abc", "image_uri": "mock://image/r1"}
        sanitized = self.adapter.sanitize_response_payload(payload)
        self.assertEqual(sanitized["api_key"], "<redacted>")
        self.assertEqual(sanitized["image_uri"], "mock://image/r1")

    def test_sanitize_response_payload_truncates_preview(self):
        long_preview = "x" * 500
        payload = {"raw_response_preview": long_preview}
        sanitized = self.adapter.sanitize_response_payload(payload)
        self.assertLess(len(sanitized["raw_response_preview"]), 300)

    def test_sanitize_response_payload_removes_image_bytes(self):
        payload = {"image_bytes": b"\x00\x01", "image_base64": "abc==", "status": "mock"}
        sanitized = self.adapter.sanitize_response_payload(payload)
        self.assertIn("<image data removed>", sanitized.get("image_bytes", ""))

    def test_build_request_returns_request(self):
        r = self.adapter.build_request("A sunset", "mock-image", mode="mock_image")
        self.assertEqual(r.provider_id, "mock-image")
        self.assertEqual(r.mode, "mock_image")

    def test_no_image_file_created_in_any_path(self):
        import tempfile, os
        before = set(os.listdir(tempfile.gettempdir()))
        r = self.Request(request_id="r1", provider_id="mock-image", mode="mock_image",
                         prompt_text="A sunset")
        self.adapter.execute_mock(r)
        after = set(os.listdir(tempfile.gettempdir()))
        new_files = after - before
        image_exts = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff"}
        for f in new_files:
            self.assertFalse(any(f.endswith(ext) for ext in image_exts),
                             f"Unexpected image file created: {f}")


if __name__ == "__main__":
    unittest.main()

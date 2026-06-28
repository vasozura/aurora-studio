"""Tests for TASK-000107: Text Provider Request/Response Contract Pack.

No network calls. No provider SDK. Standard library only.
"""

import json
import unittest
from pathlib import Path

SRC = Path(__file__).parent.parent / "src"


class TestTextProviderRequestContract(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.contracts.text_provider import TextProviderRequest
        self.cls = TextProviderRequest

    def test_basic_instantiation(self):
        r = self.cls(provider_id="openai", prompt="Hello")
        self.assertEqual(r.provider_id, "openai")
        self.assertEqual(r.prompt, "Hello")

    def test_defaults(self):
        r = self.cls(provider_id="openai", prompt="test")
        self.assertEqual(r.execution_mode, "dry_run")
        self.assertEqual(r.max_tokens, 512)
        self.assertAlmostEqual(r.temperature, 0.7)

    def test_to_dict(self):
        r = self.cls(provider_id="openai", prompt="test", model_id="gpt-4")
        d = r.to_dict()
        self.assertEqual(d["provider_id"], "openai")
        self.assertIn("prompt", d)
        self.assertIn("model_id", d)
        self.assertIn("execution_mode", d)

    def test_to_safe_dict_redacts_secret_ref(self):
        r = self.cls(provider_id="openai", prompt="test", ephemeral_secret_ref="sk-abc123")
        d = r.to_safe_dict()
        self.assertEqual(d["ephemeral_secret_ref"], "<redacted>")

    def test_to_safe_dict_empty_secret_ref_stays_empty(self):
        r = self.cls(provider_id="openai", prompt="test")
        d = r.to_safe_dict()
        self.assertEqual(d["ephemeral_secret_ref"], "")

    def test_to_json_does_not_expose_secret(self):
        r = self.cls(provider_id="openai", prompt="test", ephemeral_secret_ref="sk-abc123")
        serialized = r.to_json()
        self.assertNotIn("sk-abc123", serialized)

    def test_from_dict_roundtrip(self):
        r = self.cls(provider_id="openai", prompt="hello", model_id="gpt-4")
        d = r.to_dict()
        r2 = self.cls.from_dict(d)
        self.assertEqual(r2.provider_id, r.provider_id)
        self.assertEqual(r2.prompt, r.prompt)

    def test_frozen(self):
        r = self.cls(provider_id="openai", prompt="test")
        with self.assertRaises((AttributeError, TypeError)):
            r.prompt = "changed"

    def test_stop_sequences_tuple(self):
        r = self.cls(provider_id="p", prompt="t", stop_sequences=("stop", "end"))
        self.assertIsInstance(r.stop_sequences, tuple)
        self.assertIn("stop", r.stop_sequences)

    def test_extra_params_tuple_of_pairs(self):
        r = self.cls(provider_id="p", prompt="t", extra_params=(("key1", "val1"),))
        self.assertIsInstance(r.extra_params, tuple)


class TestTextProviderResponseContract(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.contracts.text_provider import TextProviderResponse
        self.cls = TextProviderResponse

    def test_basic_instantiation(self):
        r = self.cls(provider_id="openai", request_id="r1", status="success")
        self.assertEqual(r.status, "success")

    def test_defaults(self):
        r = self.cls(provider_id="openai", request_id="r1", status="mock")
        self.assertFalse(r.network_call)
        self.assertFalse(r.mock_response)
        self.assertEqual(r.execution_mode, "dry_run")

    def test_to_dict(self):
        r = self.cls(
            provider_id="openai", request_id="r1", status="mock",
            text="hello", mock_response=True
        )
        d = r.to_dict()
        self.assertEqual(d["status"], "mock")
        self.assertTrue(d["mock_response"])
        self.assertFalse(d["network_call"])

    def test_to_json_serializable(self):
        r = self.cls(provider_id="openai", request_id="r1", status="dry_run")
        serialized = r.to_json()
        parsed = json.loads(serialized)
        self.assertEqual(parsed["status"], "dry_run")

    def test_from_dict_roundtrip(self):
        r = self.cls(
            provider_id="openai", request_id="r1", status="success",
            text="hi", input_tokens=10, output_tokens=5
        )
        r2 = self.cls.from_dict(r.to_dict())
        self.assertEqual(r2.text, "hi")
        self.assertEqual(r2.input_tokens, 10)

    def test_frozen(self):
        r = self.cls(provider_id="openai", request_id="r1", status="success")
        with self.assertRaises((AttributeError, TypeError)):
            r.text = "changed"

    def test_no_secret_fields(self):
        d = self.cls(provider_id="p", request_id="r", status="success").to_dict()
        secret_keys = {"api_key", "secret", "token", "password", "authorization"}
        self.assertTrue(secret_keys.isdisjoint(d.keys()))


class TestTextProviderConstants(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))

    def test_execution_modes_complete(self):
        from aurora_studio.contracts.text_provider import TEXT_PROVIDER_EXECUTION_MODES
        self.assertIn("dry_run", TEXT_PROVIDER_EXECUTION_MODES)
        self.assertIn("mock", TEXT_PROVIDER_EXECUTION_MODES)
        self.assertIn("real_text", TEXT_PROVIDER_EXECUTION_MODES)
        self.assertIn("blocked_real", TEXT_PROVIDER_EXECUTION_MODES)

    def test_validation_errors_complete(self):
        from aurora_studio.contracts.text_provider import VALIDATION_ERRORS
        self.assertIn("prompt_empty", VALIDATION_ERRORS)
        self.assertIn("prompt_too_long", VALIDATION_ERRORS)
        self.assertIn("provider_id_missing", VALIDATION_ERRORS)

    def test_max_prompt_length_reasonable(self):
        from aurora_studio.contracts.text_provider import MAX_PROMPT_LENGTH
        self.assertGreater(MAX_PROMPT_LENGTH, 1000)


class TestTextProviderValidation(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.modules.text_provider_adapter import (
            validate_text_provider_request,
            validate_text_provider_parameters,
        )
        from aurora_studio.contracts.text_provider import TextProviderRequest
        self.validate_request = validate_text_provider_request
        self.validate_params = validate_text_provider_parameters
        self.Request = TextProviderRequest

    def test_valid_request_no_errors(self):
        r = self.Request(provider_id="openai", prompt="Hello world")
        errors = self.validate_request(r)
        self.assertEqual(errors, [])

    def test_empty_prompt_error(self):
        r = self.Request(provider_id="openai", prompt="")
        errors = self.validate_request(r)
        self.assertIn("prompt_empty", errors)

    def test_whitespace_prompt_error(self):
        r = self.Request(provider_id="openai", prompt="   ")
        errors = self.validate_request(r)
        self.assertIn("prompt_empty", errors)

    def test_missing_provider_id_error(self):
        r = self.Request(provider_id="", prompt="hello")
        errors = self.validate_request(r)
        self.assertIn("provider_id_missing", errors)

    def test_prompt_too_long_error(self):
        from aurora_studio.contracts.text_provider import MAX_PROMPT_LENGTH
        r = self.Request(provider_id="openai", prompt="a" * (MAX_PROMPT_LENGTH + 1))
        errors = self.validate_request(r)
        self.assertIn("prompt_too_long", errors)

    def test_invalid_execution_mode_error(self):
        r = self.Request(provider_id="openai", prompt="test", execution_mode="bogus")
        errors = self.validate_request(r)
        self.assertIn("execution_mode_invalid", errors)

    def test_validate_params_temperature_out_of_range(self):
        errors = self.validate_params(temperature=5.0)
        self.assertIn("temperature_out_of_range", errors)

    def test_validate_params_temperature_valid(self):
        errors = self.validate_params(temperature=1.0)
        self.assertEqual(errors, [])

    def test_validate_params_max_tokens_out_of_range(self):
        errors = self.validate_params(max_tokens=0)
        self.assertIn("max_tokens_out_of_range", errors)

    def test_validate_params_max_tokens_valid(self):
        errors = self.validate_params(max_tokens=512)
        self.assertEqual(errors, [])

    def test_validate_params_empty_model_id(self):
        errors = self.validate_params(model_id="")
        self.assertIn("model_id_missing", errors)

    def test_validate_params_valid_model_id(self):
        errors = self.validate_params(model_id="gpt-4o")
        self.assertEqual(errors, [])


class TestTextProviderAdapterBase(unittest.TestCase):

    def setUp(self):
        import sys; sys.path.insert(0, str(SRC))
        from aurora_studio.modules.text_provider_adapter import TextProviderAdapter
        from aurora_studio.contracts.text_provider import TextProviderRequest
        self.adapter = TextProviderAdapter()
        self.Request = TextProviderRequest

    def test_dry_run_returns_response(self):
        r = self.Request(provider_id="openai", prompt="Hello")
        resp = self.adapter.execute_dry_run(r)
        self.assertEqual(resp.status, "dry_run")
        self.assertFalse(resp.network_call)

    def test_dry_run_invalid_request(self):
        r = self.Request(provider_id="", prompt="")
        resp = self.adapter.execute_dry_run(r)
        self.assertEqual(resp.status, "invalid_request")

    def test_mock_returns_response(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="mock")
        resp = self.adapter.execute_mock(r)
        self.assertEqual(resp.status, "mock")
        self.assertTrue(resp.mock_response)
        self.assertFalse(resp.network_call)

    def test_execute_real_text_blocked_in_base(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="real_text")
        resp = self.adapter.execute_real_text(r, ephemeral_secret="fake")
        self.assertEqual(resp.status, "blocked")
        self.assertFalse(resp.network_call)

    def test_execute_routes_dry_run(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="dry_run")
        resp = self.adapter.execute(r)
        self.assertEqual(resp.status, "dry_run")

    def test_execute_routes_mock(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="mock")
        resp = self.adapter.execute(r)
        self.assertEqual(resp.status, "mock")

    def test_execute_real_text_blocked_without_gate(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="real_text")
        resp = self.adapter.execute(r)
        self.assertEqual(resp.status, "blocked")

    def test_execute_blocked_real_returns_blocked(self):
        r = self.Request(provider_id="openai", prompt="Hello", execution_mode="blocked_real")
        resp = self.adapter.execute(r)
        self.assertEqual(resp.status, "blocked")

    def test_no_network_in_any_base_path(self):
        from aurora_studio.contracts.text_provider import TextProviderRequest
        for mode in ("dry_run", "mock", "blocked_real"):
            r = TextProviderRequest(provider_id="openai", prompt="hello", execution_mode=mode)
            resp = self.adapter.execute(r)
            self.assertFalse(resp.network_call, f"Mode {mode} should not make network call")


if __name__ == "__main__":
    unittest.main()

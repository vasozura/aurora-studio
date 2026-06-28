"""Provider test connection manager for Aurora Studio v0.4.

Supports dry_run and mock modes only. No network calls. No provider SDK.
blocked_real mode always returns blocked.
Standard library only.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.provider import (
    ProviderTestConnectionRequest,
    ProviderTestConnectionResult,
    TEST_CONNECTION_MODES,
)

_DRY_RUN_PROVIDER_ID = "dry-run-local"

_BLOCKED_REAL_MESSAGE = (
    "Real provider test connection is blocked in v0.4. "
    "No network calls are permitted. No provider SDK is installed. "
    "Use dry_run or mock mode."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id() -> str:
    return str(uuid.uuid4())


class ProviderTestConnectionManager:
    """Manages provider test connections (dry/mock only in v0.4).

    No network calls. No provider SDK. No real API key required.
    All results are JSON-serializable.
    """

    def __init__(self) -> None:
        # Known provider IDs for dry-run pass: provider registry is the source of truth,
        # but to avoid a hard dependency we accept dry-run-local by default
        # and treat any non-empty provider_id as "known" for dry_run mode.
        pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def test_connection(
        self, provider_id: str, mode: str = "dry_run"
    ) -> ProviderTestConnectionResult:
        """Run a provider test connection in the specified mode.

        Modes:
          dry_run     — passes if provider_id is non-empty
          mock        — passes deterministically using local logic
          blocked_real — always blocked (no network)
        """
        req_id = _make_id()
        res_id = _make_id()
        now = _utc_now()

        if not provider_id:
            return ProviderTestConnectionResult(
                result_id=res_id,
                request_id=req_id,
                provider_id="",
                mode=mode,
                status="fail",
                message="provider_id is required",
                details={"error": "empty_provider_id"},
                created_at=now,
            )

        if mode not in TEST_CONNECTION_MODES:
            return ProviderTestConnectionResult(
                result_id=res_id,
                request_id=req_id,
                provider_id=provider_id,
                mode=mode,
                status="fail",
                message=f"Invalid mode '{mode}'. Allowed: {sorted(TEST_CONNECTION_MODES)}",
                details={"error": "invalid_mode"},
                created_at=now,
            )

        if mode == "dry_run":
            return self.test_dry_run_connection(provider_id)
        if mode == "mock":
            return self.test_mock_connection(provider_id)
        # blocked_real
        return self.block_real_connection_test(provider_id)

    def test_dry_run_connection(self, provider_id: str) -> ProviderTestConnectionResult:
        """Dry-run test: passes if provider_id is non-empty. No network."""
        req_id = _make_id()
        res_id = _make_id()
        now = _utc_now()

        if not provider_id:
            return ProviderTestConnectionResult(
                result_id=res_id, request_id=req_id,
                provider_id="", mode="dry_run",
                status="fail", message="provider_id is required",
                details={"error": "empty_provider_id"}, created_at=now,
            )

        return ProviderTestConnectionResult(
            result_id=res_id,
            request_id=req_id,
            provider_id=provider_id,
            mode="dry_run",
            status="pass",
            message=f"Dry-run only. Provider '{provider_id}' accepted. No network call made.",
            details={
                "dry_run": True,
                "network_call": False,
                "provider_sdk": False,
                "real_api_key_required": False,
            },
            created_at=now,
        )

    def test_mock_connection(self, provider_id: str) -> ProviderTestConnectionResult:
        """Mock test: passes deterministically using local logic. No network."""
        req_id = _make_id()
        res_id = _make_id()
        now = _utc_now()

        if not provider_id:
            return ProviderTestConnectionResult(
                result_id=res_id, request_id=req_id,
                provider_id="", mode="mock",
                status="fail", message="provider_id is required",
                details={"error": "empty_provider_id"}, created_at=now,
            )

        # Deterministic mock response: always passes, simulates a "ping" response
        mock_response = f"MOCK_PONG:{provider_id}:v0.4"
        return ProviderTestConnectionResult(
            result_id=res_id,
            request_id=req_id,
            provider_id=provider_id,
            mode="mock",
            status="pass",
            message=(
                f"Mock only. Local deterministic mock passed for '{provider_id}'. "
                "No network call made. Real provider calls disabled."
            ),
            details={
                "mock": True,
                "mock_response": mock_response,
                "network_call": False,
                "provider_sdk": False,
                "real_api_key_required": False,
            },
            created_at=now,
        )

    def block_real_connection_test(self, provider_id: str) -> ProviderTestConnectionResult:
        """Real connection test: always blocked in v0.4."""
        req_id = _make_id()
        res_id = _make_id()
        now = _utc_now()
        return ProviderTestConnectionResult(
            result_id=res_id,
            request_id=req_id,
            provider_id=provider_id or "",
            mode="blocked_real",
            status="blocked",
            message=_BLOCKED_REAL_MESSAGE,
            details={
                "blocked": True,
                "reason": "Real provider test is blocked in this version",
                "network_call": False,
            },
            created_at=now,
        )

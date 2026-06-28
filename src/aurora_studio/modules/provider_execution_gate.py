"""Provider execution gate for Aurora Studio v0.4.

Extended in TASK-000106 to support dry_run, mock, real_text, and blocked_real modes.
Real text execution is blocked by default unless all prerequisites are satisfied.
No provider SDK. No network. No subprocess.
Standard library only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.provider_security import (
    REAL_TEXT_PREREQUISITES,
    ProviderExecutionGateDecision,
    ProviderExecutionPrerequisite,
)


_BLOCK_REASON_DEFAULT = (
    "Real provider execution is blocked by default. "
    "All prerequisites must be satisfied and execution must be explicitly confirmed."
)

_DRY_RUN_ALLOWED_REASON = "Dry-run mode allowed without prerequisites."
_MOCK_ALLOWED_REASON = "Mock mode allowed without prerequisites."
_REAL_TEXT_BLOCKED_REASON = (
    "Real text execution blocked: not all prerequisites satisfied. "
    "Check missing_conditions for details."
)
_REAL_TEXT_ALLOWED_REASON = (
    "All prerequisites satisfied and execution explicitly confirmed. "
    "Real text execution allowed for this request only."
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_config_prerequisites(config: dict[str, Any] | None) -> tuple[list[str], list[str]]:
    """Evaluate which REAL_TEXT_PREREQUISITES are satisfied from a config dict.

    Returns (satisfied_list, missing_list).
    All prerequisites are missing if config is None or empty.
    """
    if not config or not isinstance(config, dict):
        return [], list(REAL_TEXT_PREREQUISITES)

    satisfied: list[str] = []
    missing: list[str] = []

    for prereq in REAL_TEXT_PREREQUISITES:
        # Each prerequisite is satisfied if config has a truthy value for that key
        val = config.get(prereq)
        if val:
            satisfied.append(prereq)
        else:
            missing.append(prereq)

    return satisfied, missing


class ProviderExecutionGate:
    """Controls whether a provider may execute in a given mode.

    Extended in TASK-000106 to support dry_run, mock, real_text, and blocked_real.
    Real text execution is always blocked by default.
    """

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Primary API
    # ------------------------------------------------------------------

    def evaluate_execution(
        self,
        provider_id: str,
        requested_action: str,
        mode: str = "dry_run",
        config: Any = None,
        request: Any = None,
    ) -> ProviderExecutionGateDecision:
        """Evaluate whether a provider may execute in the requested mode."""
        pid = str(provider_id).strip() if provider_id else ""
        action = str(requested_action).strip() if requested_action else ""

        if mode == "dry_run":
            return self.evaluate_dry_run(pid)
        if mode == "mock":
            return self.evaluate_mock(pid)
        if mode == "real_text":
            return self.evaluate_real_text_execution(pid, config=config, request=request)
        # blocked_real or unknown mode
        return self.block_real_execution(pid, action, reason=_BLOCK_REASON_DEFAULT)

    def evaluate_real_text_execution(
        self,
        provider_id: str,
        config: Any = None,
        request: Any = None,
    ) -> ProviderExecutionGateDecision:
        """Evaluate prerequisites for real text execution.

        Returns allowed=True only if ALL prerequisites in REAL_TEXT_PREREQUISITES
        are satisfied by the config dict. Blocked by default.
        """
        pid = str(provider_id).strip() if provider_id else ""
        now = _utc_now()

        satisfied, missing = _validate_config_prerequisites(
            config if isinstance(config, dict) else {}
        )

        if missing:
            return ProviderExecutionGateDecision(
                provider_id=pid,
                requested_action="real_text_execute",
                allowed=False,
                reason=_REAL_TEXT_BLOCKED_REASON,
                required_conditions=tuple(REAL_TEXT_PREREQUISITES),
                missing_conditions=tuple(missing),
                mode="real_text",
                created_at=now,
            )

        # All prerequisites satisfied
        return ProviderExecutionGateDecision(
            provider_id=pid,
            requested_action="real_text_execute",
            allowed=True,
            reason=_REAL_TEXT_ALLOWED_REASON,
            required_conditions=tuple(REAL_TEXT_PREREQUISITES),
            missing_conditions=(),
            mode="real_text",
            created_at=now,
        )

    def evaluate_dry_run(self, provider_id: str) -> ProviderExecutionGateDecision:
        """Dry-run mode is always allowed — no prerequisites required."""
        return ProviderExecutionGateDecision(
            provider_id=str(provider_id) if provider_id else "",
            requested_action="dry_run",
            allowed=True,
            reason=_DRY_RUN_ALLOWED_REASON,
            required_conditions=(),
            missing_conditions=(),
            mode="dry_run",
            created_at=_utc_now(),
        )

    def evaluate_mock(self, provider_id: str) -> ProviderExecutionGateDecision:
        """Mock mode is always allowed — no prerequisites required."""
        return ProviderExecutionGateDecision(
            provider_id=str(provider_id) if provider_id else "",
            requested_action="mock",
            allowed=True,
            reason=_MOCK_ALLOWED_REASON,
            required_conditions=(),
            missing_conditions=(),
            mode="mock",
            created_at=_utc_now(),
        )

    def block_real_execution(
        self,
        provider_id: str,
        requested_action: str,
        reason: str = "",
    ) -> ProviderExecutionGateDecision:
        """Explicitly create a blocked decision for real execution."""
        return ProviderExecutionGateDecision(
            provider_id=str(provider_id) if provider_id else "",
            requested_action=str(requested_action) if requested_action else "",
            allowed=False,
            reason=reason or _BLOCK_REASON_DEFAULT,
            required_conditions=tuple(REAL_TEXT_PREREQUISITES),
            missing_conditions=tuple(REAL_TEXT_PREREQUISITES),
            mode="blocked_real",
            created_at=_utc_now(),
        )

    def is_real_execution_allowed(self, provider_id: str) -> bool:
        """Return False always when called without explicit config (backward-compatible)."""
        return False

    def list_real_text_prerequisites(self) -> list[ProviderExecutionPrerequisite]:
        """Return all prerequisites required for real text execution."""
        descriptions = {
            "provider_registered": "Provider must be registered in the provider registry.",
            "provider_enabled": "Provider must be enabled in provider config.",
            "real_execution_requested": "Real execution must be explicitly requested by the caller.",
            "real_execution_allowed": "real_execution_allowed must be True in gate config.",
            "secret_reference_available": "A secret reference must be available (not the secret value itself).",
            "secret_storage_approved": "Secret storage approach must be approved for this provider.",
            "text_only_request": "Request must be text-only (no image/video/audio).",
            "redaction_enabled": "Log redaction must be enabled for this provider.",
            "logging_sanitized": "Logging must be verified to sanitize secrets and prompts.",
            "network_allowed_for_provider": "Network access must be allowed for this provider.",
            "user_confirmed": "User must have explicitly confirmed real execution.",
        }
        return [
            ProviderExecutionPrerequisite(
                name=name,
                description=descriptions.get(name, ""),
                satisfied=False,
            )
            for name in REAL_TEXT_PREREQUISITES
        ]


# ---------------------------------------------------------------------------
# Image mode support (TASK-000111)
# ---------------------------------------------------------------------------

_IMAGE_BLOCK_REASON = (
    "Real image provider execution is blocked by default. "
    "All prerequisites must be satisfied and execution must be explicitly confirmed."
)
_MOCK_IMAGE_ALLOWED_REASON = "Mock image mode allowed without prerequisites."


class ImageProviderExecutionGate:
    """Gate for image provider execution modes.

    mock_image — always allowed (no secret, no network).
    real_image — blocked by default; requires all REAL_IMAGE_PREREQUISITES.
    blocked_real_image — always blocked.
    """

    def evaluate_execution(
        self,
        provider_id: str,
        requested_action: str,
        mode: str = "mock_image",
        config: dict | None = None,
    ) -> "ProviderExecutionGateDecision":
        pid = str(provider_id).strip() if provider_id else ""
        action = str(requested_action).strip() if requested_action else ""

        if mode == "mock_image":
            return self.evaluate_mock_image(pid)
        if mode == "real_image":
            return self.evaluate_real_image(pid, config=config)
        return self.block_real_image(pid, action)

    def evaluate_mock_image(self, provider_id: str) -> "ProviderExecutionGateDecision":
        from aurora_studio.contracts.provider_security import ProviderExecutionGateDecision
        return ProviderExecutionGateDecision(
            provider_id=str(provider_id) if provider_id else "",
            requested_action="mock_image",
            allowed=True,
            reason=_MOCK_IMAGE_ALLOWED_REASON,
            required_conditions=(),
            missing_conditions=(),
            mode="mock_image",
            created_at=_utc_now(),
        )

    def evaluate_real_image(
        self,
        provider_id: str,
        config: dict | None = None,
    ) -> "ProviderExecutionGateDecision":
        from aurora_studio.contracts.provider_security import (
            ProviderExecutionGateDecision,
            REAL_IMAGE_PREREQUISITES,
        )
        pid = str(provider_id).strip() if provider_id else ""
        now = _utc_now()
        cfg = config if isinstance(config, dict) else {}

        satisfied: list[str] = []
        missing: list[str] = []
        for prereq in REAL_IMAGE_PREREQUISITES:
            (satisfied if cfg.get(prereq) else missing).append(prereq)

        if missing:
            return ProviderExecutionGateDecision(
                provider_id=pid,
                requested_action="real_image_execute",
                allowed=False,
                reason=_IMAGE_BLOCK_REASON,
                required_conditions=tuple(REAL_IMAGE_PREREQUISITES),
                missing_conditions=tuple(missing),
                mode="real_image",
                created_at=now,
            )
        return ProviderExecutionGateDecision(
            provider_id=pid,
            requested_action="real_image_execute",
            allowed=True,
            reason="All prerequisites satisfied.",
            required_conditions=tuple(REAL_IMAGE_PREREQUISITES),
            missing_conditions=(),
            mode="real_image",
            created_at=now,
        )

    def block_real_image(
        self,
        provider_id: str,
        requested_action: str,
        reason: str = "",
    ) -> "ProviderExecutionGateDecision":
        from aurora_studio.contracts.provider_security import (
            ProviderExecutionGateDecision,
            REAL_IMAGE_PREREQUISITES,
        )
        return ProviderExecutionGateDecision(
            provider_id=str(provider_id) if provider_id else "",
            requested_action=str(requested_action) if requested_action else "",
            allowed=False,
            reason=reason or _IMAGE_BLOCK_REASON,
            required_conditions=tuple(REAL_IMAGE_PREREQUISITES),
            missing_conditions=tuple(REAL_IMAGE_PREREQUISITES),
            mode="blocked_real_image",
            created_at=_utc_now(),
        )

    def list_real_image_prerequisites(self) -> list:
        from aurora_studio.contracts.provider_security import (
            REAL_IMAGE_PREREQUISITES,
            ProviderExecutionPrerequisite,
        )
        descriptions = {
            "provider_registered": "Image provider must be registered in the provider registry.",
            "provider_enabled": "Image provider must be enabled in provider config.",
            "real_image_execution_requested": "Real image execution must be explicitly requested.",
            "real_image_execution_allowed": "real_image_execution_allowed must be True in gate config.",
            "secret_reference_available": "A secret reference must be available (not the value).",
            "secret_storage_approved": "Secret storage must be approved for this provider.",
            "prompt_only_request": "Request must be prompt-only (no reference image upload).",
            "no_reference_image_upload": "No reference image, mask, or asset may be uploaded.",
            "redaction_enabled": "Log redaction must be enabled for this provider.",
            "logging_sanitized": "Logging must sanitize secrets and prompt data.",
            "network_allowed_for_provider": "Network access must be allowed for this provider.",
            "user_confirmed": "User must have explicitly confirmed real image execution.",
            "no_pii_in_prompt_confirmed": "User must confirm no PII in prompt text.",
        }
        return [
            ProviderExecutionPrerequisite(
                name=name,
                description=descriptions.get(name, ""),
                satisfied=False,
            )
            for name in REAL_IMAGE_PREREQUISITES
        ]


_VIDEO_BLOCK_REASON = (
    "Real video provider execution is blocked by default in Aurora Studio v0.4. "
    "No video generation is implemented. Use mock_video mode."
)


class VideoProviderExecutionGate:
    """Execution gate for video provider requests (TASK-000116).

    mock_video: always allowed.
    real_video: blocked in v0.4. All prerequisites unsatisfied.
    blocked_real_video: always blocked.
    No network calls. No secret retrieval. JSON-serializable decisions.
    """

    def evaluate_execution(
        self,
        provider_id: str,
        requested_action: str,
        mode: str = "mock_video",
        config: dict | None = None,
    ) -> "ProviderExecutionGateDecision":
        if mode == "mock_video":
            return self.evaluate_mock_video(provider_id)
        if mode in ("real_video", "blocked_real_video"):
            return self.block_real_video(provider_id, requested_action)
        return self.evaluate_mock_video(provider_id)

    def evaluate_mock_video(
        self, provider_id: str, requested_action: str = "generate"
    ) -> "ProviderExecutionGateDecision":
        from aurora_studio.contracts.provider_security import ProviderExecutionGateDecision
        return ProviderExecutionGateDecision(
            provider_id=str(provider_id) if provider_id else "",
            requested_action=str(requested_action),
            allowed=True,
            reason="Mock video execution is always allowed. No network, no generation.",
            mode="mock_video",
            created_at=_utc_now(),
        )

    def evaluate_real_video(
        self, provider_id: str, config: dict | None = None
    ) -> "ProviderExecutionGateDecision":
        return self.block_real_video(
            str(provider_id) if provider_id else "", "generate"
        )

    def block_real_video(
        self,
        provider_id: str,
        requested_action: str = "generate",
        reason: str = "",
    ) -> "ProviderExecutionGateDecision":
        from aurora_studio.contracts.provider_security import (
            ProviderExecutionGateDecision,
            REAL_VIDEO_PREREQUISITES,
        )
        return ProviderExecutionGateDecision(
            provider_id=str(provider_id) if provider_id else "",
            requested_action=str(requested_action),
            allowed=False,
            reason=reason or _VIDEO_BLOCK_REASON,
            required_conditions=tuple(REAL_VIDEO_PREREQUISITES),
            missing_conditions=tuple(REAL_VIDEO_PREREQUISITES),
            mode="blocked_real_video",
            created_at=_utc_now(),
        )

    def list_real_video_prerequisites(self) -> list:
        from aurora_studio.contracts.provider_security import (
            REAL_VIDEO_PREREQUISITES,
            ProviderExecutionPrerequisite,
        )
        descriptions = {
            "provider_registered": "Video provider must be registered in the provider registry.",
            "provider_enabled": "Video provider must be enabled in provider config.",
            "real_video_execution_requested": "Real video execution must be explicitly requested.",
            "real_video_execution_allowed": "real_video_execution_allowed must be True in gate config.",
            "secret_reference_available": "A secret reference must be available (not the value).",
            "secret_storage_approved": "Secret storage must be approved for this provider.",
            "prompt_only_request": "Request must be prompt-only (no reference video upload).",
            "no_reference_video_upload": "No reference video may be uploaded.",
            "no_reference_image_upload": "No reference image, mask, or asset may be uploaded.",
            "redaction_enabled": "Log redaction must be enabled for this provider.",
            "logging_sanitized": "Logging must sanitize secrets and prompt data.",
            "network_allowed_for_provider": "Network access must be allowed for this provider.",
            "user_confirmed": "User must have explicitly confirmed real video execution.",
            "no_pii_in_prompt_confirmed": "User must confirm no PII in prompt text.",
            "video_safety_review_completed": "Video safety review must be completed and approved.",
        }
        return [
            ProviderExecutionPrerequisite(
                name=name,
                description=descriptions.get(name, ""),
                satisfied=False,
            )
            for name in REAL_VIDEO_PREREQUISITES
        ]

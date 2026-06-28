"""Provider config manager for Aurora Studio v0.4.

Manages non-secret provider configuration metadata.
No provider SDK. No network. No real API key storage.
Standard library only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.provider_security import SECRET_FIELD_NAMES

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VALID_CONFIG_STATUSES = frozenset({
    "not_configured",
    "configured_without_secret",
    "secret_required",
    "secret_entry_not_saved",
    "storage_not_configured",
    "disabled",
    "blocked",
    "invalid",
})

_VALID_SECRET_STORAGE_STATUSES = frozenset({
    "not_supported",
    "not_configured",
    "planned",
    "external_required",
    "blocked",
})


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# ProviderConfigManager
# ---------------------------------------------------------------------------

class ProviderConfigManager:
    """Manages non-secret provider configuration metadata.

    Stores only non-secret metadata. No API key values.
    real_execution_allowed is always False in v0.4.
    """

    def __init__(self) -> None:
        self._configs: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Config metadata
    # ------------------------------------------------------------------

    def set_provider_config_metadata(self, provider_id: str, **fields: Any) -> dict[str, Any]:
        """Set or update provider config metadata fields.

        Secret-like fields are rejected.
        real_execution_allowed cannot be set to True in v0.4.
        """
        if not provider_id:
            raise ValueError("provider_id is required")

        # Strip any secret-like field names
        safe_fields = {
            k: v for k, v in fields.items()
            if k.lower() not in SECRET_FIELD_NAMES
        }

        existing = self._configs.get(provider_id, {
            "provider_id": provider_id,
            "enabled": False,
            "configured": False,
            "config_status": "not_configured",
            "display_name": provider_id,
            "provider_type": "other",
            "requires_api_key": False,
            "supports_dry_run": True,
            "real_execution_allowed": False,
            "secret_storage_status": "not_configured",
            "last_error": "",
            "notes": "",
            "updated_at": _utc_now(),
        })

        # Never allow real_execution_allowed to be set True in v0.4
        if "real_execution_allowed" in safe_fields:
            safe_fields["real_execution_allowed"] = False

        # Validate config_status
        if "config_status" in safe_fields:
            if safe_fields["config_status"] not in _VALID_CONFIG_STATUSES:
                safe_fields["config_status"] = "invalid"

        # Validate secret_storage_status
        if "secret_storage_status" in safe_fields:
            if safe_fields["secret_storage_status"] not in _VALID_SECRET_STORAGE_STATUSES:
                safe_fields["secret_storage_status"] = "not_configured"

        updated = {**existing, **safe_fields, "updated_at": _utc_now()}
        updated["real_execution_allowed"] = False  # enforce
        self._configs[provider_id] = updated
        return dict(updated)

    def get_provider_config_metadata(self, provider_id: str) -> dict[str, Any] | None:
        """Get config metadata for a provider. Returns None if not found."""
        record = self._configs.get(provider_id)
        return dict(record) if record else None

    def list_provider_config_metadata(self) -> list[dict[str, Any]]:
        """List all provider config metadata records."""
        return [dict(r) for r in self._configs.values()]

    def set_provider_enabled(self, provider_id: str, enabled: bool) -> dict[str, Any]:
        """Enable or disable a provider."""
        return self.set_provider_config_metadata(provider_id, enabled=bool(enabled))

    def set_secret_storage_status(self, provider_id: str, status: str) -> dict[str, Any]:
        """Set the secret storage status for a provider."""
        return self.set_provider_config_metadata(provider_id, secret_storage_status=status)

    def set_real_execution_allowed(self, provider_id: str, allowed: bool) -> dict[str, Any]:
        """Attempt to set real execution allowed.

        In v0.4, this always keeps real_execution_allowed=False.
        Returns the config with a note explaining the block.
        """
        record = self.set_provider_config_metadata(
            provider_id,
            real_execution_allowed=False,
            notes="Real execution cannot be enabled in v0.4. Deferred to TASK-000106+.",
        )
        return record

    def build_safe_config_snapshot(self, provider_id: str) -> dict[str, Any]:
        """Build a safe snapshot of provider config with no secret fields."""
        record = self.get_provider_config_metadata(provider_id)
        if record is None:
            return {"provider_id": provider_id, "config_status": "not_configured"}
        # Exclude any secret-like keys
        return {
            k: v for k, v in record.items()
            if k.lower() not in SECRET_FIELD_NAMES
        }

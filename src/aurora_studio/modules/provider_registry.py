"""Provider registry for Aurora Studio v0.3.

Stores provider metadata only.
No provider SDK imports.
No network calls.
No secret storage.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.provider import (
    DRY_RUN_PROVIDER_ID,
    PROVIDER_STATES,
    PROVIDER_TYPES,
    ProviderCapability,
    ProviderDefinition,
)
from aurora_studio.core.errors import ValidationError


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


_DRY_RUN_PROVIDER = ProviderDefinition(
    provider_id=DRY_RUN_PROVIDER_ID,
    name="Local Dry-Run Provider",
    version="0.3.0",
    provider_type="dry_run",
    state="available",
    capabilities=(
        ProviderCapability("dry_run", "Echoes sanitized prompt summary without network call."),
        ProviderCapability("text", "Accepts text prompts."),
    ),
    requires_api_key=False,
    supports_dry_run=True,
    description="Built-in dry-run provider. No network, no SDK, no secrets.",
    created_at=_utc_now(),
    updated_at=_utc_now(),
)


class ProviderRegistry:
    """In-memory provider registry.

    Stores ProviderDefinition records keyed by provider_id.
    The built-in dry-run provider is always available.
    """

    def __init__(self) -> None:
        self._providers: dict[str, ProviderDefinition] = {
            DRY_RUN_PROVIDER_ID: _DRY_RUN_PROVIDER,
        }

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_provider(self, definition: ProviderDefinition) -> ProviderDefinition:
        pid = definition.provider_id.strip()
        if not pid:
            raise ValidationError("provider_id must not be empty.")
        if definition.provider_type not in PROVIDER_TYPES:
            raise ValidationError(
                f"Invalid provider_type: {definition.provider_type!r}. "
                f"Allowed: {sorted(PROVIDER_TYPES)}"
            )
        record = definition.with_updates(provider_id=pid)
        self._providers[pid] = record
        return record

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_providers(
        self,
        provider_type: str | None = None,
        state: str | None = None,
    ) -> list[ProviderDefinition]:
        results = list(self._providers.values())
        if provider_type is not None:
            results = [r for r in results if r.provider_type == provider_type]
        if state is not None:
            results = [r for r in results if r.state == state]
        return results

    def get_provider(self, provider_id: str) -> ProviderDefinition:
        pid = provider_id.strip()
        if pid not in self._providers:
            raise ValidationError(f"Provider not found: {pid!r}")
        return self._providers[pid]

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    def enable_provider(self, provider_id: str) -> ProviderDefinition:
        defn = self.get_provider(provider_id)
        updated = defn.with_updates(state="available", error_message="", updated_at=_utc_now())
        self._providers[provider_id.strip()] = updated
        return updated

    def disable_provider(self, provider_id: str) -> ProviderDefinition:
        defn = self.get_provider(provider_id)
        updated = defn.with_updates(state="disabled", updated_at=_utc_now())
        self._providers[provider_id.strip()] = updated
        return updated

    def mark_provider_error(self, provider_id: str, message: str = "") -> ProviderDefinition:
        defn = self.get_provider(provider_id)
        updated = defn.with_updates(
            state="error", error_message=str(message), updated_at=_utc_now()
        )
        self._providers[provider_id.strip()] = updated
        return updated

    def clear_provider_error(self, provider_id: str) -> ProviderDefinition:
        defn = self.get_provider(provider_id)
        updated = defn.with_updates(
            state="not_configured", error_message="", updated_at=_utc_now()
        )
        self._providers[provider_id.strip()] = updated
        return updated

    # ------------------------------------------------------------------
    # Capabilities
    # ------------------------------------------------------------------

    def list_capabilities(self, provider_id: str) -> list[ProviderCapability]:
        return list(self.get_provider(provider_id).capabilities)

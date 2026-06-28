"""Prompt template contract for Aurora Studio v0.2."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

TEMPLATE_STATE_ACTIVE = "active"
TEMPLATE_STATE_ARCHIVED = "archived"

TEMPLATE_TARGET_TYPES = frozenset({
    "project", "scene", "shot", "timeline", "character", "asset"
})


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class PromptTemplateRecord:
    """Local prompt template record — no provider calls, no AI generation."""

    template_id: str
    project_id: str
    name: str
    target_type: str
    template_text: str
    description: str = ""
    state: str = TEMPLATE_STATE_ACTIVE
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def with_updates(self, **changes: Any) -> "PromptTemplateRecord":
        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PromptTemplateRecord":
        return cls(
            template_id=str(data.get("template_id", "")),
            project_id=str(data.get("project_id", "")),
            name=str(data.get("name", "")),
            target_type=str(data.get("target_type", "scene")),
            template_text=str(data.get("template_text", "")),
            description=str(data.get("description", "")),
            state=str(data.get("state", TEMPLATE_STATE_ACTIVE)),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

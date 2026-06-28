"""Export profile contract for Aurora Studio."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

PROFILE_STATE_ACTIVE = "active"
PROFILE_STATE_ARCHIVED = "archived"
PROFILE_TARGET_TYPES = frozenset({
    "project", "scene", "shot", "timeline", "character", "asset",
})

_PROJECT_ID_DEFAULT = "__default__"


@dataclass(frozen=True)
class ExportProfileRecord:
    """A named export profile binding a template to an output format."""

    profile_id: str
    project_id: str
    name: str
    target_type: str
    template_id: str = ""
    template_text: str = ""
    description: str = ""
    state: str = PROFILE_STATE_ACTIVE
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def with_updates(self, **changes: Any) -> "ExportProfileRecord":
        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: Any) -> "ExportProfileRecord":
        return cls(
            profile_id=str(data["profile_id"]),
            project_id=str(data.get("project_id", "")),
            name=str(data["name"]),
            target_type=str(data["target_type"]),
            template_id=str(data.get("template_id", "")),
            template_text=str(data.get("template_text", "")),
            description=str(data.get("description", "")),
            state=str(data.get("state", PROFILE_STATE_ACTIVE)),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )

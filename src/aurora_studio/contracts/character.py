"""Character contract — v0.2 adds detail fields and structured references (TASK-000058/059)."""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

CHARACTER_STATE_ACTIVE = "active"
CHARACTER_STATE_ARCHIVED = "archived"

REFERENCE_TYPES = frozenset({"face", "costume", "pose", "mood", "voice", "style", "other"})


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class CharacterRef:
    character_id: str
    display_name: str = ""


@dataclass(frozen=True)
class CharacterReference:
    """Structured reference linking an asset to a character with type metadata (TASK-000059)."""

    asset_id: str
    reference_type: str = "other"
    is_primary: bool = False
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CharacterReference":
        if "asset_id" not in data:
            raise ValueError("CharacterReference missing required key: asset_id")
        return cls(
            asset_id=str(data["asset_id"]),
            reference_type=str(data.get("reference_type", "other")),
            is_primary=bool(data.get("is_primary", False)),
            notes=str(data.get("notes", "")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
        )


@dataclass(frozen=True)
class CharacterRecord:
    """Character record — v0.2 adds detail fields and structured references."""

    character_id: str
    project_id: str
    display_name: str
    # v0.1 compat fields
    description: str = ""
    reference_asset_ids: tuple[str, ...] = ()
    state: str = CHARACTER_STATE_ACTIVE
    created_at: str = ""
    modified_at: str = ""
    archived_at: str | None = None
    # v0.2 detail fields (TASK-000058)
    role: str = ""
    visual_description: str = ""
    personality: str = ""
    motivation: str = ""
    conflict: str = ""
    arc_notes: str = ""
    notes: str = ""
    # v0.2 structured references (TASK-000059)
    reference_assets: tuple[CharacterReference, ...] = ()

    def to_ref(self) -> CharacterRef:
        return CharacterRef(character_id=self.character_id, display_name=self.display_name)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["reference_asset_ids"] = list(d["reference_asset_ids"])
        d["reference_assets"] = [
            ra if isinstance(ra, dict) else ra for ra in d["reference_assets"]
        ]
        return d

    def with_updates(self, **changes: Any) -> "CharacterRecord":
        return replace(self, **changes)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CharacterRecord":
        required = ("character_id", "project_id", "display_name", "state", "created_at", "modified_at")
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"Character record missing required keys: {', '.join(missing)}")

        # Build structured references (TASK-000059)
        raw_refs = data.get("reference_assets", [])
        if isinstance(raw_refs, (list, tuple)):
            structured_refs = tuple(
                CharacterReference.from_dict(r) if isinstance(r, dict) else r
                for r in raw_refs
            )
        else:
            structured_refs = ()

        # Derive reference_asset_ids from structured refs if not present (migration path)
        raw_ids = data.get("reference_asset_ids", [])
        if not raw_ids and structured_refs:
            ref_ids = tuple(r.asset_id for r in structured_refs)
        else:
            ref_ids = tuple(str(a) for a in raw_ids)

        return cls(
            character_id=str(data["character_id"]),
            project_id=str(data["project_id"]),
            display_name=str(data["display_name"]),
            description=str(data.get("description", "")),
            reference_asset_ids=ref_ids,
            state=str(data["state"]),
            created_at=str(data["created_at"]),
            modified_at=str(data["modified_at"]),
            archived_at=None if data.get("archived_at") is None else str(data["archived_at"]),
            role=str(data.get("role", "")),
            visual_description=str(data.get("visual_description", "")),
            personality=str(data.get("personality", "")),
            motivation=str(data.get("motivation", "")),
            conflict=str(data.get("conflict", "")),
            arc_notes=str(data.get("arc_notes", "")),
            notes=str(data.get("notes", "")),
            reference_assets=structured_refs,
        )

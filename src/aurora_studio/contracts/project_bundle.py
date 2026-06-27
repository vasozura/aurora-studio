"""Project bundle contract for local JSON persistence."""

from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

CURRENT_BUNDLE_VERSION = "0.1.0"
DEFAULT_BUNDLE_FILENAME = "aurora_bundle.json"
_SUPPORTED_VERSIONS = frozenset({"0.1.0"})

_COLLECTION_FIELDS = (
    "scenes",
    "shots",
    "timelines",
    "assets",
    "characters",
    "afl_reports",
    "export_artifacts",
    "plugins",
)


def utc_now_iso() -> str:
    """Return an ISO-8601 UTC timestamp."""

    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ProjectBundle:
    """Minimal project bundle contract for local JSON persistence.

    Stores serialized output from existing in-memory managers.
    Does not define final schemas for individual records.
    Does not implement automatic manager rehydration.
    """

    schema_version: str
    project_metadata: dict
    workspace_state: dict | None = None
    scenes: tuple = ()
    shots: tuple = ()
    timelines: tuple = ()
    assets: tuple = ()
    characters: tuple = ()
    afl_reports: tuple = ()
    export_artifacts: tuple = ()
    plugins: tuple = ()
    created_at: str = ""
    modified_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable bundle."""

        return {
            "schema_version": self.schema_version,
            "project_metadata": self.project_metadata,
            "workspace_state": self.workspace_state,
            "scenes": list(self.scenes),
            "shots": list(self.shots),
            "timelines": list(self.timelines),
            "assets": list(self.assets),
            "characters": list(self.characters),
            "afl_reports": list(self.afl_reports),
            "export_artifacts": list(self.export_artifacts),
            "plugins": list(self.plugins),
            "created_at": self.created_at,
            "modified_at": self.modified_at,
        }

    def with_updates(self, **changes: Any) -> "ProjectBundle":
        """Return a new bundle with selected fields changed."""

        return replace(self, **changes)

    @classmethod
    def empty(cls, project_metadata: dict | None = None) -> "ProjectBundle":
        """Return a new empty bundle with optional project metadata."""

        now = utc_now_iso()
        return cls(
            schema_version=CURRENT_BUNDLE_VERSION,
            project_metadata=project_metadata if project_metadata is not None else {},
            created_at=now,
            modified_at=now,
        )

    @classmethod
    def from_dict(cls, data: Any) -> "ProjectBundle":
        """Create a bundle from JSON-like data with validation."""

        from aurora_studio.core.errors import ValidationError

        if not isinstance(data, dict):
            raise ValidationError("Bundle root must be a dict.")

        if "schema_version" not in data:
            raise ValidationError("Bundle missing required key: schema_version.")

        schema_version = str(data["schema_version"])
        if schema_version not in _SUPPORTED_VERSIONS:
            raise ValidationError(
                f"Unsupported bundle schema_version: {schema_version!r}. "
                f"Supported: {sorted(_SUPPORTED_VERSIONS)}"
            )

        project_metadata = data.get("project_metadata", {})
        if not isinstance(project_metadata, dict):
            raise ValidationError("Bundle project_metadata must be a dict.")

        workspace_state = data.get("workspace_state")
        if workspace_state is not None and not isinstance(workspace_state, dict):
            raise ValidationError("Bundle workspace_state must be a dict or None.")

        collections: dict[str, tuple] = {}
        for field in _COLLECTION_FIELDS:
            raw = data.get(field, [])
            if not isinstance(raw, (list, tuple)):
                raise ValidationError(f"Bundle field '{field}' must be a list.")
            for item in raw:
                if not isinstance(item, dict):
                    raise ValidationError(f"Bundle field '{field}' items must be dicts.")
            collections[field] = tuple(raw)

        return cls(
            schema_version=schema_version,
            project_metadata=project_metadata,
            workspace_state=workspace_state,
            scenes=collections["scenes"],
            shots=collections["shots"],
            timelines=collections["timelines"],
            assets=collections["assets"],
            characters=collections["characters"],
            afl_reports=collections["afl_reports"],
            export_artifacts=collections["export_artifacts"],
            plugins=collections["plugins"],
            created_at=str(data.get("created_at", "")),
            modified_at=str(data.get("modified_at", "")),
        )

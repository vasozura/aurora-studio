"""Prompt Export Manager first minimal implementation."""

from __future__ import annotations

from aurora_studio.contracts.export import (
    EXPORT_STATUS_DRAFT,
    EXPORT_STATUS_FAILED,
    EXPORT_STATUS_READY,
    ExportArtifactRecord,
    utc_now_iso,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id
from aurora_studio.core.readiness import Readiness


class PromptExportManager:
    """Minimal Prompt Export Manager implementation.

    This class manages only in-memory export artifact records.

    It does not implement:
    - Real prompt generation
    - AFL-to-prompt conversion
    - Provider calls
    - Export file persistence
    - Database persistence
    - GUI behavior
    """

    module_name = "Prompt Export Manager"
    readiness = Readiness.NOT_READY

    def __init__(self) -> None:
        self._artifacts: dict[str, ExportArtifactRecord] = {}

    def get_readiness(self) -> Readiness:
        """Return module readiness."""

        return self.readiness

    def describe(self) -> str:
        """Return a short implementation description."""

        return (
            "Prompt Export Manager supports minimal in-memory export artifact records "
            "and remains not ready for full product implementation."
        )

    def create_export_artifact(
        self,
        source_id: str,
        artifact_type: str,
        content: str,
        provider_target: str | None = None,
    ) -> ExportArtifactRecord:
        """Register an export artifact in memory.

        This does not generate prompts or call providers.
        """

        clean_source_id = self._validate_required_ref(source_id, "source_id")
        clean_artifact_type = self._validate_required_ref(artifact_type, "artifact_type")
        clean_content = self._validate_required_ref(content, "content")
        now = utc_now_iso()

        artifact = ExportArtifactRecord(
            artifact_id=new_id("artifact"),
            source_id=clean_source_id,
            artifact_type=clean_artifact_type,
            content=clean_content,
            status=EXPORT_STATUS_DRAFT,
            provider_target=provider_target.strip() if provider_target is not None else None,
            created_at=now,
            modified_at=now,
        )
        self._artifacts[artifact.artifact_id] = artifact
        return artifact

    def list_export_artifacts(self, source_id: str | None = None) -> list[ExportArtifactRecord]:
        """List export artifact records, optionally filtered by source reference."""

        artifacts = list(self._artifacts.values())
        if source_id is not None:
            clean_source_id = self._validate_required_ref(source_id, "source_id")
            artifacts = [a for a in artifacts if a.source_id == clean_source_id]
        return artifacts

    def get_export_artifact(self, artifact_id: str) -> ExportArtifactRecord:
        """Return an export artifact record by ID."""

        clean_artifact_id = self._validate_required_ref(artifact_id, "artifact_id")
        try:
            return self._artifacts[clean_artifact_id]
        except KeyError as exc:
            raise ValidationError(f"Export artifact not found: {clean_artifact_id}") from exc

    def mark_export_ready(self, artifact_id: str) -> ExportArtifactRecord:
        """Mark an export artifact as ready."""

        artifact = self.get_export_artifact(artifact_id)
        updated = artifact.with_updates(status=EXPORT_STATUS_READY, modified_at=utc_now_iso())
        self._artifacts[updated.artifact_id] = updated
        return updated

    def mark_export_failed(self, artifact_id: str, message: str = "") -> ExportArtifactRecord:
        """Mark an export artifact as failed. Stores failure message in content."""

        artifact = self.get_export_artifact(artifact_id)
        updated_content = message.strip() if message.strip() else artifact.content
        updated = artifact.with_updates(
            status=EXPORT_STATUS_FAILED,
            content=updated_content,
            modified_at=utc_now_iso(),
        )
        self._artifacts[updated.artifact_id] = updated
        return updated

    def _validate_required_ref(self, value: str, field_name: str) -> str:
        """Validate a required reference-like string."""

        clean_value = value.strip()
        if not clean_value:
            raise ValidationError(f"{field_name} must not be empty.")
        return clean_value

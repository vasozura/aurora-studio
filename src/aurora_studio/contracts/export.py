"""Export contract placeholders."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ExportArtifactRef:
    """Placeholder export artifact reference contract.

    Export artifacts are outputs, not source meaning.
    """

    artifact_id: str
    source_id: str
    artifact_type: str

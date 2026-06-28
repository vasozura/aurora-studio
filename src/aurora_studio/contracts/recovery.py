"""Recovery contracts for Aurora Studio v0.3.

Local backup and recovery metadata. No cloud/network behavior.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ProjectBackupRecord:
    backup_id: str
    project_id: str
    source_path: str
    backup_path: str
    reason: str = "manual"
    created_at: str = ""
    size_bytes: int = 0
    checksum_hint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Any) -> "ProjectBackupRecord":
        return cls(
            backup_id=str(data.get("backup_id", "")),
            project_id=str(data.get("project_id", "")),
            source_path=str(data.get("source_path", "")),
            backup_path=str(data.get("backup_path", "")),
            reason=str(data.get("reason", "manual")),
            created_at=str(data.get("created_at", "")),
            size_bytes=int(data.get("size_bytes", 0)),
            checksum_hint=str(data.get("checksum_hint", "")),
        )


@dataclass(frozen=True)
class ProjectRecoveryCandidate:
    candidate_id: str
    project_id: str
    candidate_path: str
    candidate_type: str
    created_at: str = ""
    size_bytes: int = 0
    is_valid_json: bool = False
    validation_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ProjectRecoveryReport:
    status: str
    candidate_count: int
    candidates: tuple[ProjectRecoveryCandidate, ...]
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "candidate_count": self.candidate_count,
            "candidates": [c.to_dict() for c in self.candidates],
            "message": self.message,
        }

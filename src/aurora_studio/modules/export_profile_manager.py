"""ExportProfileManager for Aurora Studio."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from aurora_studio.contracts.export_profile import (
    PROFILE_STATE_ACTIVE,
    PROFILE_STATE_ARCHIVED,
    ExportProfileRecord,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


_PROJECT_ID_DEFAULT = "__default__"

_ALLOWED_UPDATE_FIELDS = frozenset({"name", "template_id", "template_text", "description", "target_type"})

_DEFAULT_PROFILES = [
    ExportProfileRecord(
        profile_id="default-profile-generic-image",
        project_id=_PROJECT_ID_DEFAULT,
        name="Generic Image Prompt",
        target_type="shot",
        template_text=(
            "{{shot.title}}. {{shot.description}} "
            "Camera: {{shot.camera_movement}}. Framing: {{shot.framing}}. "
            "Emotion: {{shot.emotion_target}}."
        ),
        description="Generic image generation prompt for shots.",
    ),
    ExportProfileRecord(
        profile_id="default-profile-cinematic-shot",
        project_id=_PROJECT_ID_DEFAULT,
        name="Cinematic Shot Prompt",
        target_type="shot",
        template_text=(
            "Cinematic shot. {{shot.shot_type}} — {{shot.camera_angle}}. "
            "{{shot.camera_movement}} movement. Lens: {{shot.lens}}. "
            "Duration: {{shot.duration_seconds}}s. Focus: {{shot.visual_focus}}."
        ),
        description="Detailed cinematic shot description for video generation.",
    ),
    ExportProfileRecord(
        profile_id="default-profile-video-generation",
        project_id=_PROJECT_ID_DEFAULT,
        name="Video Generation Prompt",
        target_type="scene",
        template_text=(
            "Scene: {{scene.title}}. Location: {{scene.location}}. "
            "Mood: {{scene.mood}}. Time: {{scene.time_of_day}}. "
            "{{scene.description}}"
        ),
        description="Scene-level prompt for video generation tools.",
    ),
    ExportProfileRecord(
        profile_id="default-profile-storyboard",
        project_id=_PROJECT_ID_DEFAULT,
        name="Storyboard Prompt",
        target_type="scene",
        template_text=(
            "Storyboard panel. Scene: {{scene.title}}. "
            "{{scene.description}} Setting: {{scene.location}} at {{scene.time_of_day}}. "
            "Mood: {{scene.mood}}."
        ),
        description="Storyboard illustration prompt for scenes.",
    ),
    ExportProfileRecord(
        profile_id="default-profile-character-reference",
        project_id=_PROJECT_ID_DEFAULT,
        name="Character Reference Prompt",
        target_type="character",
        template_text=(
            "Character reference sheet. Name: {{character.display_name}}. "
            "{{character.visual_description}} Role: {{character.role}}."
        ),
        description="Character reference image prompt.",
    ),
    ExportProfileRecord(
        profile_id="default-profile-negative-prompt",
        project_id=_PROJECT_ID_DEFAULT,
        name="Negative Prompt",
        target_type="shot",
        template_text=(
            "blurry, low quality, deformed, text, watermark, "
            "inconsistent lighting, overexposed, underexposed"
        ),
        description="Standard negative prompt for image generation.",
    ),
]


class ExportProfileManager:
    """In-memory manager for export profiles."""

    def __init__(self) -> None:
        self._profiles: dict[str, ExportProfileRecord] = {
            p.profile_id: p for p in _DEFAULT_PROFILES
        }

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create_profile(
        self,
        name: str,
        target_type: str,
        template_id: str = "",
        template_text: str = "",
        description: str = "",
        project_id: str = "",
    ) -> ExportProfileRecord:
        name = name.strip()
        if not name:
            raise ValidationError("Profile name must not be empty.")
        target_type = target_type.strip()
        from aurora_studio.contracts.export_profile import PROFILE_TARGET_TYPES
        if target_type not in PROFILE_TARGET_TYPES:
            raise ValidationError(
                f"Invalid target_type: {target_type!r}. "
                f"Allowed: {sorted(PROFILE_TARGET_TYPES)}"
            )
        now = _utc_now()
        record = ExportProfileRecord(
            profile_id=new_id("profile"),
            project_id=project_id.strip(),
            name=name,
            target_type=target_type,
            template_id=template_id.strip(),
            template_text=template_text,
            description=description.strip(),
            state=PROFILE_STATE_ACTIVE,
            created_at=now,
            updated_at=now,
        )
        self._profiles[record.profile_id] = record
        return record

    def list_profiles(
        self,
        project_id: str | None = None,
        target_type: str | None = None,
        include_defaults: bool = True,
    ) -> list[ExportProfileRecord]:
        results = list(self._profiles.values())
        if not include_defaults:
            results = [r for r in results if not r.profile_id.startswith("default-profile-")]
        if project_id is not None:
            results = [
                r for r in results
                if r.project_id == project_id or r.project_id == _PROJECT_ID_DEFAULT
            ]
        if target_type is not None:
            results = [r for r in results if r.target_type == target_type]
        return results

    def list_default_profiles(self) -> list[ExportProfileRecord]:
        return [r for r in self._profiles.values() if r.profile_id.startswith("default-profile-")]

    def get_profile(self, profile_id: str) -> ExportProfileRecord:
        pid = profile_id.strip()
        if pid not in self._profiles:
            raise ValidationError(f"Profile not found: {pid!r}")
        return self._profiles[pid]

    def update_profile(self, profile_id: str, **fields: Any) -> ExportProfileRecord:
        pid = profile_id.strip()
        if pid not in self._profiles:
            raise ValidationError(f"Profile not found: {pid!r}")
        if pid.startswith("default-profile-"):
            raise ValidationError("Default profiles cannot be updated.")
        unknown = set(fields) - _ALLOWED_UPDATE_FIELDS
        if unknown:
            raise ValidationError(f"Unknown update fields: {sorted(unknown)}")
        now = _utc_now()
        record = self._profiles[pid].with_updates(updated_at=now, **fields)
        self._profiles[pid] = record
        return record

    def archive_profile(self, profile_id: str) -> ExportProfileRecord:
        pid = profile_id.strip()
        if pid not in self._profiles:
            raise ValidationError(f"Profile not found: {pid!r}")
        if pid.startswith("default-profile-"):
            raise ValidationError("Default profiles cannot be archived.")
        record = self._profiles[pid].with_updates(
            state=PROFILE_STATE_ARCHIVED, updated_at=_utc_now()
        )
        self._profiles[pid] = record
        return record

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render_profile_text(self, template_text: str, context: dict[str, Any]) -> str:
        result = template_text
        for key, value in context.items():
            result = result.replace("{{" + key + "}}", str(value) if value is not None else "")
        return result

    def render_with_profile(
        self,
        profile_id: str,
        context: dict[str, Any],
        prompt_template_manager: Any = None,
    ) -> str:
        profile = self.get_profile(profile_id)
        # If profile has template_id, resolve via prompt_template_manager
        if profile.template_id and prompt_template_manager is not None:
            return prompt_template_manager.render_template(profile.template_id, context)
        # Otherwise use inline template_text
        return self.render_profile_text(profile.template_text, context)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def replace_profiles(self, records: list[ExportProfileRecord]) -> None:
        """Replace custom profiles; keep defaults."""
        custom_ids = [
            pid for pid in list(self._profiles)
            if not pid.startswith("default-profile-")
        ]
        for pid in custom_ids:
            del self._profiles[pid]
        for r in records:
            if not r.profile_id.startswith("default-profile-"):
                self._profiles[r.profile_id] = r

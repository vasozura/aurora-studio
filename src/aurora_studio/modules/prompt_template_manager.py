"""Prompt Template Manager — local string-based template rendering only.

No Jinja2. No external templating. No provider calls. No AI generation.
"""

from __future__ import annotations

from aurora_studio.contracts.prompt_template import (
    TEMPLATE_STATE_ACTIVE,
    TEMPLATE_STATE_ARCHIVED,
    TEMPLATE_TARGET_TYPES,
    PromptTemplateRecord,
    utc_now_iso,
)
from aurora_studio.core.errors import ValidationError
from aurora_studio.core.ids import new_id

_ALLOWED_UPDATE_FIELDS = frozenset({
    "name", "template_text", "description", "target_type"
})

# ── Default templates (in-memory, not persisted unless custom project saves them)

_DEFAULT_TEMPLATES: list[dict] = [
    {
        "name": "scene_basic",
        "target_type": "scene",
        "template_text": (
            "Scene: {{scene.title}}\n"
            "Location: {{scene.location}}\n"
            "Mood: {{scene.mood}}\n"
            "Time of Day: {{scene.time_of_day}}\n"
            "Description: {{scene.description}}\n"
            "Conflict: {{scene.conflict}}"
        ),
        "description": "Basic scene description prompt.",
    },
    {
        "name": "shot_cinematic",
        "target_type": "shot",
        "template_text": (
            "Shot: {{shot.title}}\n"
            "Camera Movement: {{shot.camera_movement}}\n"
            "Framing: {{shot.framing}}\n"
            "Camera Angle: {{shot.camera_angle}}\n"
            "Lens: {{shot.lens}}\n"
            "Emotion Target: {{shot.emotion_target}}\n"
            "Visual Focus: {{shot.visual_focus}}\n"
            "Description: {{shot.description}}"
        ),
        "description": "Cinematic shot prompt.",
    },
    {
        "name": "character_reference",
        "target_type": "character",
        "template_text": (
            "Character: {{character.display_name}}\n"
            "Role: {{character.role}}\n"
            "Visual Description: {{character.visual_description}}\n"
            "Personality: {{character.personality}}\n"
            "Motivation: {{character.motivation}}"
        ),
        "description": "Character reference prompt.",
    },
    {
        "name": "timeline_summary",
        "target_type": "timeline",
        "template_text": (
            "Project: {{project.title}}\n"
            "Scene: {{scene.title}}\n"
            "Timeline summary for editorial reference."
        ),
        "description": "Timeline summary prompt.",
    },
    {
        "name": "asset_reference",
        "target_type": "asset",
        "template_text": (
            "Asset: {{asset.display_name}}\n"
            "Type: {{asset.asset_type}}\n"
            "Description: {{asset.description}}\n"
            "Notes: {{asset.notes}}"
        ),
        "description": "Asset reference prompt.",
    },
]


class PromptTemplateManager:
    """Manages local prompt templates. All rendering is local string substitution.

    Does not call providers. Does not generate AI content.
    """

    _PROJECT_ID_DEFAULT = "__default__"

    def __init__(self) -> None:
        self._templates: dict[str, PromptTemplateRecord] = {}
        self._defaults_loaded = False
        self._load_defaults()

    # ── Internal helpers

    def _load_defaults(self) -> None:
        """Populate in-memory default templates (idempotent)."""
        if self._defaults_loaded:
            return
        now = utc_now_iso()
        for spec in _DEFAULT_TEMPLATES:
            tid = f"default-{spec['name']}"
            record = PromptTemplateRecord(
                template_id=tid,
                project_id=self._PROJECT_ID_DEFAULT,
                name=spec["name"],
                target_type=spec["target_type"],
                template_text=spec["template_text"],
                description=spec["description"],
                state=TEMPLATE_STATE_ACTIVE,
                created_at=now,
                updated_at=now,
            )
            self._templates[tid] = record
        self._defaults_loaded = True

    def _validate_nonempty(self, value: str, field: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValidationError(f"{field} must not be empty.")
        return clean

    # ── Public API

    def create_template(
        self,
        name: str,
        target_type: str,
        template_text: str,
        description: str = "",
        project_id: str = "",
    ) -> PromptTemplateRecord:
        name = self._validate_nonempty(name, "name")
        target_type = target_type.strip()
        if target_type not in TEMPLATE_TARGET_TYPES:
            raise ValidationError(
                f"Invalid target_type {target_type!r}. Allowed: {sorted(TEMPLATE_TARGET_TYPES)}"
            )
        template_text = self._validate_nonempty(template_text, "template_text")
        now = utc_now_iso()
        record = PromptTemplateRecord(
            template_id=new_id("tmpl"),
            project_id=project_id.strip(),
            name=name,
            target_type=target_type,
            template_text=template_text,
            description=description.strip(),
            state=TEMPLATE_STATE_ACTIVE,
            created_at=now,
            updated_at=now,
        )
        self._templates[record.template_id] = record
        return record

    def list_templates(
        self,
        project_id: str | None = None,
        target_type: str | None = None,
        include_defaults: bool = True,
    ) -> list[PromptTemplateRecord]:
        results = list(self._templates.values())
        if not include_defaults:
            results = [r for r in results if not r.template_id.startswith("default-")]
        if project_id is not None:
            results = [r for r in results if r.project_id == project_id]
        if target_type is not None:
            results = [r for r in results if r.target_type == target_type]
        results = [r for r in results if r.state == TEMPLATE_STATE_ACTIVE]
        return results

    def list_default_templates(self) -> list[PromptTemplateRecord]:
        return [r for r in self._templates.values()
                if r.project_id == self._PROJECT_ID_DEFAULT]

    def get_template(self, template_id: str) -> PromptTemplateRecord:
        tid = template_id.strip()
        if tid not in self._templates:
            raise ValidationError(f"Template not found: {tid!r}")
        return self._templates[tid]

    def update_template(self, template_id: str, **fields: Any) -> PromptTemplateRecord:
        record = self.get_template(template_id)
        unknown = set(fields) - _ALLOWED_UPDATE_FIELDS
        if unknown:
            raise ValidationError(f"Unknown update fields: {sorted(unknown)}")
        changes: dict = {"updated_at": utc_now_iso()}
        if "name" in fields:
            changes["name"] = self._validate_nonempty(fields["name"], "name")
        if "template_text" in fields:
            changes["template_text"] = self._validate_nonempty(fields["template_text"], "template_text")
        if "description" in fields:
            changes["description"] = str(fields["description"]).strip()
        if "target_type" in fields:
            tt = str(fields["target_type"]).strip()
            if tt not in TEMPLATE_TARGET_TYPES:
                raise ValidationError(f"Invalid target_type: {tt!r}")
            changes["target_type"] = tt
        updated = record.with_updates(**changes)
        self._templates[template_id] = updated
        return updated

    def archive_template(self, template_id: str) -> PromptTemplateRecord:
        record = self.get_template(template_id)
        updated = record.with_updates(state=TEMPLATE_STATE_ARCHIVED, updated_at=utc_now_iso())
        self._templates[template_id] = updated
        return updated

    def render_template_text(self, template_text: str, context: dict) -> str:
        """Replace {{key}} placeholders with context values.

        Missing keys render as empty string.
        """
        result = template_text
        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            result = result.replace(placeholder, str(value) if value is not None else "")
        return result

    def render_template(self, template_id: str, context: dict) -> str:
        """Render a stored template by ID with the given context."""
        record = self.get_template(template_id)
        return self.render_template_text(record.template_text, context)

    def replace_templates(self, records: list[PromptTemplateRecord]) -> None:
        """Replace custom (non-default) templates. Used by bundle rehydration."""
        # Keep defaults, replace custom entries
        defaults = {tid: r for tid, r in self._templates.items()
                    if r.project_id == self._PROJECT_ID_DEFAULT}
        self._templates = defaults
        for r in records:
            self._templates[r.template_id] = r

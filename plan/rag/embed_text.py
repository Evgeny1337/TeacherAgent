import json

from intake.schemas.lesson_info_response import LessonInfoResponse

_EMBED_FIELDS = (
    "goal",
    "topic",
    "cefr_level",
    "duration_minutes",
    "skills",
    "lesson_type",
    "language_focus",
)


def build_embed_text_from_brief(lesson_info: LessonInfoResponse) -> str:
    data = lesson_info.model_dump(include=set(_EMBED_FIELDS), mode="json")
    parts: list[str] = []
    for key in _EMBED_FIELDS:
        value = data.get(key)
        if value in (None, "", []):
            continue
        if isinstance(value, list):
            value = ", ".join(str(item) for item in value)
        parts.append(f"{key}: {value}")
    return " | ".join(parts)


def plans_to_prompt_block(plans: list[dict] | None) -> str:
    if not plans:
        return ""
    parts = ["example_lesson_plans:"]
    for i, plan in enumerate(plans, 1):
        parts.append(f"### example_{i}")
        parts.append(json.dumps(plan, ensure_ascii=False, indent=2))
    return "\n".join(parts) + "\n"

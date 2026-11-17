from pathlib import Path

from plan.generate.generate_plan import revise_lesson_plan
from plan.recordWord.record_word import record_lesson_plan_to_word
from plan.schemas.plan_shema import LessonPlan
from pipeline.common import API_KEY, materials_text


def run_revise_lesson(
    previous_plan: LessonPlan,
    revision_notes: str,
    file_name: Path,
    materials: list[Path] | None = None,
    format_preferences: str = "none",
) -> LessonPlan:
    if not API_KEY:
        raise Exception("Не задан ключ DeepSeek")
    if previous_plan is None:
        raise ValueError("Нет текущего плана для доработки")
    notes = (revision_notes or "").strip()
    if not notes:
        raise ValueError("Пустые замечания для доработки")
    text_chunks = materials_text(materials or [])
    plan = revise_lesson_plan(
        api_key=API_KEY,
        previous_plan=previous_plan,
        revision_notes=notes,
        materials=text_chunks,
        format_preferences=format_preferences,
    )
    record_lesson_plan_to_word(plan, file_name)
    return plan

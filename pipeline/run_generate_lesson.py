import datetime
from pathlib import Path

from intake.llm.fetch_lesson_info import fetch_lesson_info
from plan.generate.generate_plan import generate_lesson_plan
from plan.rag import fetch_similar_plans
from plan.recordWord.record_word import record_lesson_plan_to_word
from plan.schemas.plan_shema import LessonPlan
from pipeline.common import API_KEY, LESSON_DIR, materials_text


def create_file_name() -> Path:
    lesson_dir = Path(LESSON_DIR)
    day = datetime.datetime.now().strftime("%Y%m%d")
    n = 1
    while True:
        path = lesson_dir / f"{day}_{n}.docx"
        if not path.exists():
            return path
        n += 1


def run_generate_lesson(
    materials: list[Path],
    teacher_description: str,
    file_name: Path,
    format_preferences: str = "none",
) -> LessonPlan:
    if not API_KEY:
        raise Exception("Не задан ключ DeepSeek")
    text_chunks = materials_text(materials)
    lesson_info = fetch_lesson_info(
        materials_text=text_chunks,
        teacher_description=teacher_description,
        api_key=API_KEY,
    )
    similar_plans = fetch_similar_plans(lesson_info)
    plan = generate_lesson_plan(
        lesson_brief=lesson_info.model_dump_json(),
        teacher="MaryA",
        lesson_date=datetime.datetime.now().strftime("%Y-%m-%d"),
        materials=text_chunks,
        teacher_description=teacher_description,
        format_preferences=format_preferences,
        api_key=API_KEY,
        similar_plans=similar_plans or None,
    )
    record_lesson_plan_to_word(plan, file_name)
    return plan

from plan.generate.llm import SYSTEM_PROMPT, chat_json
from plan.generate.revise import revise_lesson_plan
from plan.schemas.plan_shema import LessonPlan


__all__ = ["generate_lesson_plan", "revise_lesson_plan"]


def generate_lesson_plan(
    api_key: str,
    materials: str,
    lesson_brief: str,
    teacher: str,
    lesson_date: str,
    teacher_description: str,
    format_preferences: str = "none",
    similar_plans: str | None = None,
) -> LessonPlan:
    user_prompt = (
        "Build the lesson plan JSON.\n\n"
        f"teacher_overrides:\ndate: {lesson_date}\nteacher: {teacher}\n\n"
        f"teacher_description:\n{teacher_description}\n\n"
        f"format_preferences:\n{format_preferences or 'none'}\n\n"
        f"lesson_brief:\n{lesson_brief}\n\n"
        f"materials:\n{materials or 'None'}\n"
    )
    if similar_plans:
        user_prompt += f"{similar_plans}\n"
    return chat_json(
        api_key,
        user_prompt,
        LessonPlan,
        system_prompt=SYSTEM_PROMPT,
    )

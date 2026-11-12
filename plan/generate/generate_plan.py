from pathlib import Path

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from plan.schemas.plan_shema import LessonPlan


def generate_lesson_plan(
    api_key: str,
    materials: str,
    lesson_brief: str,
    teacher: str,
    lesson_date: str,
    teacher_description: str,
    format_preferences: str = "none",
) -> LessonPlan:
    user_prompt = (
        "Build the lesson plan JSON.\n\n"
        f"teacher_overrides:\ndate: {lesson_date}\nteacher: {teacher}\n\n"
        f"teacher_description:\n{teacher_description}\n\n"
        f"format_preferences:\n{format_preferences or 'none'}\n\n"
        f"lesson_brief:\n{lesson_brief}\n\n"
        f"materials:\n{materials or 'None'}\n"
    )

    system_prompt = (Path(__file__).parent / "create_plan_prompt.md").read_text(
        encoding="utf-8"
    )

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content or not content.strip():
        raise ValueError("DeepSeek returned empty content")
    return LessonPlan.model_validate_json(content)

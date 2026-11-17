from pathlib import Path

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from plan.schemas.plan_shema import LessonPlan

_PROMPTS_DIR = Path(__file__).parent

SYSTEM_PROMPT = (_PROMPTS_DIR / "create_plan_prompt.md").read_text(encoding="utf-8")
REVISE_ROUTER_PROMPT = (_PROMPTS_DIR / "revise_router_prompt.md").read_text(
    encoding="utf-8"
)
REVISE_PATCH_PROMPT = (_PROMPTS_DIR / "revise_patch_prompt.md").read_text(
    encoding="utf-8"
)

def _request_lesson_plan(api_key: str, user_prompt: str, system_prompt: str = SYSTEM_PROMPT) -> LessonPlan:
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
        max_tokens=8192,
        extra_body={"thinking": {"type": "disabled"}},
    )
    content = response.choices[0].message.content
    if not content or not content.strip():
        raise ValueError("DeepSeek returned empty content")
    try:
        return LessonPlan.model_validate_json(content)
    except Exception as exc:
        preview = content if len(content) <= 500 else f"{content[:500]}..."
        raise ValueError(
            f"Невалидный JSON плана урока ({exc}). "
            f"finish_reason={response.choices[0].finish_reason!r}. "
            f"Фрагмент ответа: {preview}"
        ) from exc


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
    return _request_lesson_plan(api_key, user_prompt)


def revise_lesson_plan(
    api_key: str,
    previous_plan: LessonPlan,
    revision_notes: str,
    materials: str = "",
    format_preferences: str = "none",
) -> LessonPlan:
    user_prompt = (
        "Revise the existing lesson plan JSON using revision_notes. "
        "Keep the same JSON shape and return the full updated plan.\n\n"
        f"revision_notes:\n{revision_notes}\n\n"
        f"format_preferences:\n{format_preferences or 'none'}\n\n"
        f"previous_plan:\n{previous_plan.model_dump_json()}\n\n"
        f"materials:\n{materials or 'None'}\n"
    )
    return _request_lesson_plan(api_key, user_prompt)

from pathlib import Path

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from intake.schemas.lesson_info_response import LessonInfoResponse


def fetch_lesson_info(
    teacher_description: str,
    materials_text: str,
    api_key: str,
) -> LessonInfoResponse:
    system_prompt = (Path(__file__).parent / "create_brief_prompt.md").read_text(
        encoding="utf-8"
    )
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"teacher_description:\n{teacher_description}\n\n"
                f"pinned_material_chunks:\n{materials_text}"
            ),
        },
    ]
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content or not content.strip():
        raise ValueError("DeepSeek returned empty content")
    return LessonInfoResponse.model_validate_json(content)

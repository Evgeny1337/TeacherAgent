from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from intake.schemas.lesson_info_response import LessonInfoResponse

SYSTEM_PROMPT = """
You are an assistant that prepares a structured lesson brief for an English teacher.

You receive:
1) teacher_description — free-text request
2) materials — extracted text chunks from attached files

Your job:
- Understand what lesson the teacher wants
- Use materials only as evidence
- Do NOT write a full lesson plan with timed activities
- Do NOT invent worksheet content that is not supported by materials
- If information is missing, put null and ask clarifying questions
- If a material has little/no usable text, mention that in clarifying_questions

Return ONLY valid json with these keys:
{
  "goal": string,
  "topic": string | null,
  "cefr_level": "A1"|"A2"|"B1"|"B2"|"C1"|"C2"|null,
  "duration_minutes": number | null,
  "skills": string[],
  "lesson_type": "grammar"|"skills"|"exam_prep"|"revision"|"mixed"|"unclear",
  "language_focus": string[],
  "based_on_materials": string[],
  "assumptions": string[],
  "clarifying_questions": string[],
  "readiness": "ready"|"needs_clarification"|"insufficient_input",
  "confidence": number
}
"""


def fetch_lesson_info(
    teacher_description: str,
    materials_text: str,
    api_key: str,
) -> LessonInfoResponse:
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )
    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": SYSTEM_PROMPT},
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

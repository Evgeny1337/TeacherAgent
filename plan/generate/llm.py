from pathlib import Path
from typing import TypeVar

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

_PROMPTS_DIR = Path(__file__).parent

SYSTEM_PROMPT = (_PROMPTS_DIR / "create_plan_prompt.md").read_text(encoding="utf-8")
REVISE_ROUTER_PROMPT = (_PROMPTS_DIR / "revise_router_prompt.md").read_text(
    encoding="utf-8"
)
REVISE_PATCH_PROMPT = (_PROMPTS_DIR / "revise_patch_prompt.md").read_text(
    encoding="utf-8"
)

T = TypeVar("T", bound=BaseModel)


def chat_json(
    api_key: str,
    user_prompt: str,
    model_type: type[T],
    *,
    system_prompt: str = SYSTEM_PROMPT,
    max_tokens: int = 8192,
) -> T:
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
        max_tokens=max_tokens,
        extra_body={"thinking": {"type": "disabled"}},
    )
    content = response.choices[0].message.content
    if not content or not content.strip():
        raise ValueError("DeepSeek returned empty content")
    try:
        return model_type.model_validate_json(content)
    except Exception as exc:
        preview = content if len(content) <= 500 else f"{content[:500]}..."
        raise ValueError(
            f"Невалидный JSON ({model_type.__name__}: {exc}). "
            f"finish_reason={response.choices[0].finish_reason!r}. "
            f"Фрагмент ответа: {preview}"
        ) from exc

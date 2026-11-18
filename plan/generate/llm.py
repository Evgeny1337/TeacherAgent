import json
from pathlib import Path
from typing import TypeVar

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, ValidationError

_PROMPTS_DIR = Path(__file__).parent

SYSTEM_PROMPT = (_PROMPTS_DIR / "create_plan_prompt.md").read_text(encoding="utf-8")
REVISE_ROUTER_PROMPT = (_PROMPTS_DIR / "revise_router_prompt.md").read_text(
    encoding="utf-8"
)
REVISE_PATCH_PROMPT = (_PROMPTS_DIR / "revise_patch_prompt.md").read_text(
    encoding="utf-8"
)

T = TypeVar("T", bound=BaseModel)
_MAX_ATTEMPTS = 3


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
    schema = json.dumps(
        model_type.model_json_schema(),
        ensure_ascii=False,
    )
    last_error: Exception | None = None
    last_content = ""
    last_finish: str | None = None

    for attempt in range(_MAX_ATTEMPTS):
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
            extra_body={"thinking": {"type": "disabled"}},
        )
        content = response.choices[0].message.content
        last_finish = response.choices[0].finish_reason
        if not content or not content.strip():
            last_error = ValueError("DeepSeek returned empty content")
            messages.append({"role": "assistant", "content": content or ""})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Previous reply was empty. Return valid JSON for {model_type.__name__} only.\n"
                        f"json_schema:\n{schema}\n"
                    ),
                }
            )
            continue

        last_content = content
        try:
            return model_type.model_validate_json(content)
        except ValidationError as exc:
            last_error = exc
            if attempt >= _MAX_ATTEMPTS - 1:
                break
            messages.append({"role": "assistant", "content": content})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Your JSON failed validation for {model_type.__name__}. "
                        "Fix it and return ONLY corrected JSON.\n\n"
                        f"validation_errors:\n{exc}\n\n"
                        f"json_schema:\n{schema}\n"
                    ),
                }
            )

    preview = last_content if len(last_content) <= 500 else f"{last_content[:500]}..."
    raise ValueError(
        f"Невалидный JSON ({model_type.__name__}: {last_error}). "
        f"finish_reason={last_finish!r}. "
        f"Фрагмент ответа: {preview}"
    ) from last_error

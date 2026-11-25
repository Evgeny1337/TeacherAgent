import os

import httpx
from dotenv import load_dotenv

from intake.schemas.lesson_info_response import LessonInfoResponse
from plan.rag.embed_text import build_embed_text_from_brief, plans_to_prompt_block
from plan.rag.schemas import PlansResponseSchema

load_dotenv()


def _rag_base() -> str:
    return os.environ.get("RAG_URL", "http://localhost:8003").rstrip("/")


def fetch_lesson_data(lesson_id: int, *, timeout: float = 30.0) -> dict:
    response = httpx.get(
        f"{_rag_base()}/api/teacher/{lesson_id}/data/",
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError("Некорректный ответ /data/")
    return data


def fetch_similar_plans(
    lesson_info: LessonInfoResponse,
    *,
    limit: int = 3,
    timeout: float = 30.0,
) -> str:
    rag_url = os.environ.get("RAG_URL", "").rstrip("/")
    if not rag_url:
        return ""

    embed_text = build_embed_text_from_brief(lesson_info)
    if not embed_text:
        return ""

    body: dict = {
        "embed_text": embed_text,
        "limit": limit,
    }
    if lesson_info.cefr_level is not None:
        body["level"] = lesson_info.cefr_level.value
    if lesson_info.lesson_type is not None:
        body["lesson_type"] = lesson_info.lesson_type.value

    try:
        response = httpx.post(
            f"{rag_url}/api/teacher/similar",
            json=body,
            timeout=timeout,
        )
        response.raise_for_status()
        payload = PlansResponseSchema.model_validate(response.json())
    except (httpx.HTTPError, ValueError):
        return ""

    return plans_to_prompt_block(payload.plans)

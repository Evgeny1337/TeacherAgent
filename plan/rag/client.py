import httpx

from intake.schemas.lesson_info_response import LessonInfoResponse
from pipeline.common import (
    RAG_PATH_HISTORY,
    RAG_PATH_LESSON_DATA,
    RAG_PATH_SAVE,
    RAG_PATH_SIMILAR,
    RAG_URL,
    rag_endpoint,
)
from plan.rag.embed_text import build_embed_text_from_brief, plans_to_prompt_block
from plan.rag.schemas import PlansResponseSchema


def fetch_history(*, timeout: float = 15.0) -> list[dict]:
    response = httpx.get(rag_endpoint(RAG_PATH_HISTORY), timeout=timeout)
    response.raise_for_status()
    rows = response.json()
    if not isinstance(rows, list):
        raise ValueError("Некорректный ответ history")
    return rows


def save_lesson(payload: dict, *, timeout: float = 30.0) -> None:
    response = httpx.post(
        rag_endpoint(RAG_PATH_SAVE),
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()


def fetch_lesson_data(lesson_id: int, *, timeout: float = 30.0) -> dict:
    response = httpx.get(
        rag_endpoint(RAG_PATH_LESSON_DATA, lesson_id=lesson_id),
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
    if not RAG_URL:
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
            rag_endpoint(RAG_PATH_SIMILAR),
            json=body,
            timeout=timeout,
        )
        response.raise_for_status()
        payload = PlansResponseSchema.model_validate(response.json())
    except (httpx.HTTPError, ValueError):
        return ""

    return plans_to_prompt_block(payload.plans)

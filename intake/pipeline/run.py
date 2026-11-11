from intake.chunking.chunk_markdown import get_text_chunks
from intake.extract.to_markdown import extract_files
from intake.llm.fetch_lesson_info import fetch_lesson_info
from intake.schemas.lesson_info_response import (
    LessonInfoResponse,
    LessonType,
    Readiness,
)
from intake.schemas.teacher_request import TeacherRequest


def _empty_materials_response() -> LessonInfoResponse:
    return LessonInfoResponse(
        goal="Недостаточно текста из материалов, чтобы собрать бриф урока.",
        topic=None,
        cefr_level=None,
        duration_minutes=None,
        skills=[],
        lesson_type=LessonType.UNCLEAR,
        language_focus=[],
        based_on_materials=[],
        assumptions=[],
        missing_info=["usable text from attached materials"],
        clarifying_questions=[
            "Приложите pdf/docx/pptx с извлекаемым текстом или вставьте текст материала.",
        ],
        readiness=Readiness.INSUFFICIENT_INPUT,
        confidence=0.0,
    )


def run_intake(request: TeacherRequest, api_key: str) -> LessonInfoResponse:
    extracted = extract_files(request.files)
    chunks: list[str] = []
    for doc in extracted:
        chunks.extend(chunk for chunk in get_text_chunks(doc) if chunk.strip())

    if not chunks:
        return _empty_materials_response()

    materials_text = "\n\n--- фрагмент материала ---\n\n".join(chunks)
    return fetch_lesson_info(request.teacher_description, materials_text, api_key)

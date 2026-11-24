import os
from datetime import datetime
from pathlib import Path

from intake.chunking.chunk_markdown import get_text_chunks
from intake.extract.to_markdown import extract_files
from intake.llm.fetch_lesson_info import fetch_lesson_info
from plan.generate.generate_plan import generate_lesson_plan
from plan.recordWord.record_word import record_lesson_plan_to_word


def get_lesson_plan(materials:list[Path], teacher_description):
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise Exception("Ключ DeepSeek не задан")
    markdown_files = extract_files(materials)
    files_chunks = []
    for markdown_file in markdown_files:
        files_chunks.append(get_text_chunks(markdown_file))
    text_chunks = "".join(
        f"Чанк [{i}] {x}" for i, x in enumerate(files_chunks, start=1)
    )
    format_preferences = "none"
    lesson_info = fetch_lesson_info(
        materials_text=text_chunks,
        teacher_description=teacher_description,
        api_key=api_key,
    )
    plan = generate_lesson_plan(
        lesson_brief=lesson_info.model_dump_json(),
        teacher="MaryA",
        lesson_date=datetime.now().strftime("%Y-%m-%d"),
        materials=text_chunks,
        teacher_description=teacher_description,
        format_preferences=format_preferences,
        api_key=api_key,
    )
    record_lesson_plan_to_word(plan)

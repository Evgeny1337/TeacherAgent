from pathlib import Path
from datetime import datetime

from intake.chunking.chunk_markdown import get_text_chunks
from intake.extract.to_markdown import extract_files
from intake.llm.fetch_lesson_info import fetch_lesson_info
from plan.generate.generate_plan import generate_lesson_plan
from plan.recordWord.record_word import record_lesson_plan_to_word


def main():
    file = Path(__file__).parent / "doc.docx"
    markdown_files = extract_files([file])
    files_chunks = []
    for markdown_file in markdown_files:
        files_chunks.append(get_text_chunks(markdown_file))
    text_chunks = "".join(
        f"Чанк [{i}] {x}" for i, x in enumerate(files_chunks, start=1)
    )

    teacher_description = (
        "Урок A2 на 45 минут по Clothes. Present Simple vs Present Continuous и in/on/at. "
        "Подростки, около 12 человек. Опирайся на приложенный worksheet. "
        "Больше pair work. Homework — 5 предложений."
    )

    format_preferences = "none"

    api_key = "sk-ca9734c652cc47c0b5e753a48ecd95e1"

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


if __name__ == "__main__":
    main()

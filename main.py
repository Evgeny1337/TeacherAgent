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
    for file in markdown_files:
        files_chunks.append(get_text_chunks(file))
    text_chunks = "".join(f"Чанк [{i}] {x}" for i, x in enumerate(files_chunks, start=1))
    lesson_info = fetch_lesson_info(materials_text=text_chunks, teacher_description="""
        Сделай бриф и затем план урока A2 на 45 минут по теме Clothes.
        Нужно отработать Present Simple vs Present Continuous и предлоги in/on/at.
        Класс: подростки 10–12 лет, 10–12 человек.
        Опирайся на приложенный worksheet.
        
        Важно по материалам в плане:
        1) Class handout / worksheet оформи как настоящий раздаточный материал в Markdown:
           - шапка Name / Class / Date таблицей или строками;
           - задания 1–4 с явной структурой;
           - где уместно — Markdown-таблицы (например True/False Me|Partner, или choose-the-form в таблице);
           - для vocabulary — таблица Word | Example sentence или карточки в виде таблицы 2×3 / 3×2.
        2) Homework оформи отдельно как набор карточек/prompts в Markdown:
           - карточки-задания (Card 1, Card 2…) или таблица Prompt | My sentence;
           - checklist таблицей или task list;
           - scoring отдельно.
        3) Не делай отдельный handout только с answer key для учеников.
        4) Handouts — только то, что реально раздаётся классу; ключи при необходимости кратко в procedure учителя.
    """,
    api_key="sk-ca9734c652cc47c0b5e753a48ecd95e1")

    plan = generate_lesson_plan(
            lesson_brief=lesson_info.model_dump_json(),
            teacher="MaryA",
            lesson_date=datetime.now().strftime("%Y-%m-%d"),
            materials=text_chunks,
            api_key="sk-ca9734c652cc47c0b5e753a48ecd95e1"
    )
    record_lesson_plan_to_word(plan)



if __name__ == "__main__":
    main()
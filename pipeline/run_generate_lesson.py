import os
from dotenv import load_dotenv
import datetime
from pathlib import Path

from intake.chunking.chunk_markdown import get_text_chunks
from intake.extract.to_markdown import extract_files
from intake.llm.fetch_lesson_info import fetch_lesson_info
from plan.generate.generate_plan import generate_lesson_plan
from plan.recordWord.record_word import record_lesson_plan_to_word
from plan.schemas.plan_shema import LessonPlan

load_dotenv()

LESSON_DIR = os.environ.get("LESSON_DIR", "./")
API_KEY = os.environ.get("API_KEY", "")

def create_file_name() -> Path:
    lesson_dir = Path(LESSON_DIR)
    day = datetime.datetime.now().strftime("%Y%m%d")
    n = 1
    while True:
        path = lesson_dir / f"{day}_{n}.docx"
        if not path.exists():
            return path
        n += 1

def run_generate_lesson(materials: list[Path], teacher_description: str, file_name: Path, format_preferences:str = "none") -> LessonPlan:
    if not API_KEY:
        raise Exception("Не задан ключ DeepSeek")
    markdown_files = extract_files(materials)
    files_chunks = []
    for markdown_file in markdown_files:
        files_chunks.append(get_text_chunks(markdown_file))
    text_chunks = "".join(
        f"Чанк [{i}] {x}" for i, x in enumerate(files_chunks, start=1)
    )

    lesson_info = fetch_lesson_info(
        materials_text=text_chunks,
        teacher_description=teacher_description,
        api_key=API_KEY,
    )

    plan = generate_lesson_plan(
        lesson_brief=lesson_info.model_dump_json(),
        teacher="MaryA",
        lesson_date=datetime.datetime.now().strftime("%Y-%m-%d"),
        materials=text_chunks,
        teacher_description=teacher_description,
        format_preferences=format_preferences,
        api_key=API_KEY,
    )

    return plan



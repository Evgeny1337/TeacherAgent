import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from intake.chunking.chunk_markdown import get_text_chunks
from intake.extract.to_markdown import extract_files


def _load_env() -> None:
    if getattr(sys, "frozen", False) and getattr(sys, "_MEIPASS", None):
        load_dotenv(Path(sys._MEIPASS) / ".env", override=False)
    load_dotenv(override=False)


_load_env()


def _default_lesson_dir() -> str:
    desktop = Path.home() / "Desktop"
    if desktop.is_dir():
        return str(desktop)
    return str(Path.home())


API_KEY = os.environ.get("API_KEY", "")
LESSON_DIR = os.environ.get("LESSON_DIR") or _default_lesson_dir()
RAG_URL = os.environ.get("RAG_URL", "")


def rag_doc_path(lesson_id: int) -> Path:
    return Path(LESSON_DIR) / f"rag_{lesson_id}.docx"



def materials_text(materials: list[Path]) -> str:
    if not materials:
        return ""
    markdown_files = extract_files(materials)
    files_chunks = [get_text_chunks(markdown_file) for markdown_file in markdown_files]
    return "".join(f"Чанк [{i}] {x}" for i, x in enumerate(files_chunks, start=1))

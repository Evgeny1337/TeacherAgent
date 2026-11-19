import os
from pathlib import Path

from dotenv import load_dotenv

from intake.chunking.chunk_markdown import get_text_chunks
from intake.extract.to_markdown import extract_files

load_dotenv()

API_KEY = os.environ.get("API_KEY", "")
LESSON_DIR = os.environ.get("LESSON_DIR", "./")
RAG_URL = os.environ.get("RAG_URL", "")



def materials_text(materials: list[Path]) -> str:
    if not materials:
        return ""
    markdown_files = extract_files(materials)
    files_chunks = [get_text_chunks(markdown_file) for markdown_file in markdown_files]
    return "".join(f"Чанк [{i}] {x}" for i, x in enumerate(files_chunks, start=1))

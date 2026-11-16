import os
import tempfile
from pathlib import Path

from docxtpl import DocxTemplate
from dotenv import load_dotenv
from mddocx import render_string, RenderConfig

from plan.schemas.plan_shema import LessonPlan

load_dotenv()

LESSON_DIR = os.getenv("LESSON_DIR", "./")
_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[2] / "templates" / "lesson" / "lesson_plan.docx"
)


def convert_md(doc: DocxTemplate, md_text: str):
    docx_bytes = render_string(md_text or "", config=RenderConfig(theme="modern"))
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(docx_bytes)
        tmp_path = tmp.name
    return doc.new_subdoc(tmp_path)


def record_lesson_plan_to_word(lesson_plan: LessonPlan, file_name: Path) -> Path:
    if not _TEMPLATE_PATH.is_file():
        raise FileNotFoundError(f"Шаблон не найден: {_TEMPLATE_PATH}")
    file_name = Path(file_name)
    file_name.parent.mkdir(parents=True, exist_ok=True)
    doc = DocxTemplate(str(_TEMPLATE_PATH))
    context = lesson_plan.model_dump()
    context["handouts"] = list(context.get("handouts") or [])
    for handout in context["handouts"]:
        handout["body"] = convert_md(doc, handout.get("body", ""))
    worksheet = context.get("worksheet")
    if worksheet and isinstance(worksheet, dict):
        worksheet["body"] = convert_md(doc, worksheet.get("body", ""))
    doc.render(context)
    doc.save(file_name)
    if not file_name.is_file():
        raise RuntimeError(f"Файл не создан: {file_name}")
    return file_name
import tempfile

from docxtpl import DocxTemplate
from mddocx import render_string, RenderConfig

from plan.schemas.plan_shema import LessonPlan

def convert_md(doc: DocxTemplate, md_text: str):
    docx_bytes = render_string(md_text or "", config=RenderConfig(theme="modern"))
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(docx_bytes)
        tmp_path = tmp.name
    return doc.new_subdoc(tmp_path)


def record_lesson_plan_to_word(lesson_plan: LessonPlan) -> bool:
    doc = DocxTemplate("templates/lesson/lesson_plan.docx")
    print(lesson_plan)
    context = lesson_plan.model_dump()
    for handout in context.get("handouts") or []:
        handout["body"] = convert_md(doc, handout.get("body", ""))
    worksheet = context.get("worksheet")
    if worksheet and isinstance(worksheet, dict):
        worksheet["body"] = convert_md(doc, worksheet.get("body", ""))
    doc.render(context)
    doc.save("out.docx")
    return True
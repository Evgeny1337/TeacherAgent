import os
from pathlib import Path

from dotenv import load_dotenv

from intake.pipeline.run import run_intake
from intake.schemas.teacher_request import TeacherRequest

load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY is not set")

request = TeacherRequest(
    teacher_description=(
        "Сделай бриф урока A1–A2 на 40–45 минут по was/were для Elementary. "
        "Есть готовый worksheet: gap-fill, choose was/were, rewrite am/is/are → was/were. "
        "Нужны цель урока, фокус грамматики и чего не хватает для полного плана. "
        "Класс: дети 10–12 лет, 10 учеников."
    ),
    files=[Path(__file__).parent / "test_teacher.pdf"],
)

lesson = run_intake(request, API_KEY)
print(lesson)

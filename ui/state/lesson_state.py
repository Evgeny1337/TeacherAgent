import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from uuid import uuid4

from plan.schemas.plan_shema import LessonPlan

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class LessonStatus(str, Enum):
    CREATING = "Создание"
    GENERATED = "Сгенерирован"
    ERROR = "Ошибка"


@dataclass
class LessonItem:
    id: str = field(default_factory=lambda: uuid4().hex[:8])
    description: str = ""
    status: LessonStatus = LessonStatus.CREATING
    summary: str = ""
    file_path: Path | None = None
    plan: LessonPlan | None = None
    error: str | None = None
    materials: list[Path] = field(default_factory=list)

    def set_plan(self, plan: LessonPlan, path: Path) -> None:
        self.plan = plan
        self.file_path = path
        self.status = LessonStatus.GENERATED
        self.error = None
        parts = [plan.lesson.level.strip(), plan.lesson.aim.strip()]
        self.summary = " · ".join(p for p in parts if p) or "Урок готов"

    def set_error(self, message: str) -> None:
        self.status = LessonStatus.ERROR
        self.error = message.strip() or "Ошибка"
        self.summary = self.error[:120]

    def get_plan_for_request(self) -> dict:
        if self.plan is None:
            raise ValueError("Нет плана для апрува")
        header = self.plan.lesson
        raw_date = (header.date or "").strip()
        date = raw_date if _ISO_DATE.match(raw_date) else None
        return {
            "date": date,
            "level": header.level,
            "topic": (self.description or "").strip()[:255],
            "lesson_type": "",
            "duration_minutes": None,
            "aim": header.aim,
            "sub_aim": header.sub_aim or "",
            "homework_summary": header.homework_summary or "",
            "plan_json": self.plan.model_dump(mode="json"),
            "embed_text": (
                f"level: {header.level} | aim: {header.aim} | {header.sub_aim}"
            ),
        }


@dataclass
class AppState:
    lessons: list[LessonItem] = field(default_factory=list)
    active_id: str | None = None
    busy: bool = False
    draft_paths: list[Path] = field(default_factory=list)

    @property
    def active(self) -> LessonItem | None:
        return next((x for x in self.lessons if x.id == self.active_id), None)

    def clear_draft(self) -> None:
        self.draft_paths.clear()
        self.active_id = None

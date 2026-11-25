import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from uuid import uuid4

from pipeline.common import rag_doc_path
from plan.schemas.plan_shema import LessonPlan

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class LessonStatus(str, Enum):
    CREATING = "Создание"
    GENERATED = "Сгенерирован"
    APPROVED = "Подтверждён"
    READY = "Документ готов"
    ERROR = "Ошибка"


@dataclass
class LessonItem:
    # RAG/DB id; None until урок сохранён в TeacherRag
    id: int | None = None
    local_id: str = field(default_factory=lambda: uuid4().hex[:8])
    description: str = ""
    status: LessonStatus = LessonStatus.CREATING
    summary: str = ""
    file_path: Path | None = None
    plan: LessonPlan | None = None
    error: str | None = None
    materials: list[Path] = field(default_factory=list)

    @property
    def is_approved(self) -> bool:
        return self.id is not None or self.status in (
            LessonStatus.APPROVED,
            LessonStatus.READY,
        )

    @property
    def can_open(self) -> bool:
        return self.file_path is not None and self.file_path.is_file()

    @property
    def can_materialize(self) -> bool:
        return self.id is not None and not self.can_open

    @classmethod
    def from_history(cls, row: dict) -> "LessonItem":
        remote_id = row.get("id")
        topic = (row.get("topic") or "").strip()
        aim = (row.get("aim") or "").strip()
        lesson_id = int(remote_id) if remote_id is not None else None
        path = rag_doc_path(lesson_id) if lesson_id is not None else None
        ready = path is not None and path.is_file()
        return cls(
            id=lesson_id,
            local_id=str(lesson_id) if lesson_id is not None else uuid4().hex[:8],
            description=topic,
            summary=aim or topic or "Урок из истории",
            file_path=path if ready else None,
            status=LessonStatus.READY if ready else LessonStatus.APPROVED,
        )

    def apply_remote_data(self, data: dict, path: Path) -> None:
        plan_json = data.get("plan_json")
        if not isinstance(plan_json, dict):
            raise ValueError("В ответе нет plan_json")
        plan = LessonPlan.model_validate(plan_json)
        self.plan = plan
        self.file_path = path
        self.error = None
        if data.get("id") is not None:
            self.id = int(data["id"])
        topic = (data.get("topic") or "").strip()
        aim = (data.get("aim") or plan.lesson.aim or "").strip()
        if topic:
            self.description = topic
        self.summary = aim or topic or self.summary or "Урок готов"
        self.status = LessonStatus.READY

    def set_plan(self, plan: LessonPlan, path: Path) -> None:
        self.plan = plan
        self.file_path = path
        self.status = LessonStatus.GENERATED
        self.error = None
        parts = [plan.lesson.level.strip(), plan.lesson.aim.strip()]
        self.summary = " · ".join(p for p in parts if p) or "Урок готов"

    def mark_approved(self, remote_id: int | None = None) -> None:
        if remote_id is not None:
            self.id = int(remote_id)
        self.status = (
            LessonStatus.READY if self.can_open else LessonStatus.APPROVED
        )

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
            "is_reference": False,
        }


@dataclass
class AppState:
    lessons: list[LessonItem] = field(default_factory=list)
    active_id: str | None = None
    busy: bool = False
    draft_paths: list[Path] = field(default_factory=list)

    @property
    def active(self) -> LessonItem | None:
        return next(
            (x for x in self.lessons if x.local_id == self.active_id),
            None,
        )

    def load_history(self, rows: list[dict]) -> None:
        self.lessons = [LessonItem.from_history(row) for row in rows]

    def clear_draft(self) -> None:
        self.draft_paths.clear()
        self.active_id = None

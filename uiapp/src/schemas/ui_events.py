from pathlib import Path

from pydantic import BaseModel, Field

from plan.schemas.plan_shema import LessonPlan
from schemas.lesson_session import LessonStatus


class LessonGenerateEvent(BaseModel):
    file_path: Path
    teacher_description: str = ""
    materials: list[Path] = Field(default_factory=list)
    status: LessonStatus = LessonStatus.GENERATING
    plan: LessonPlan | None = None

    @property
    def card_id(self) -> str:
        return self.file_path.name

    @property
    def title(self) -> str:
        return self.file_path.stem

    @property
    def subtitle(self) -> str:
        desc = (self.teacher_description or "").strip()
        if desc:
            return desc if len(desc) <= 80 else f"{desc[:77]}..."
        count = len(self.materials)
        return f"{count} файл(ов)" if count else "Без материалов"


class HistoryEntryEvent(BaseModel):
    text: str

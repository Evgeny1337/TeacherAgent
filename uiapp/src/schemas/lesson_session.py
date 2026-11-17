from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field

from plan.schemas.plan_shema import LessonPlan


class LessonStatus(str, Enum):
    GENERATING = "generating"
    READY = "ready"
    REVISING = "revising"
    CONFIRMED = "confirmed"
    ERROR = "error"


class LessonSession(BaseModel):
    id: str
    file_path: Path
    plan: LessonPlan | None = None
    status: LessonStatus = Field(default=LessonStatus.GENERATING)
    teacher_description: str = ""
    materials: list[Path] = Field(default_factory=list)
    revision_notes: str = ""


class AppState:
    def __init__(self) -> None:
        self.active: LessonSession | None = None

from enum import Enum

from pydantic import BaseModel


class CefrLevel(Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

class LessonType(Enum):
    GRAMMAR = "grammar"
    SKILLS = "skills"
    EXAM_PREP = "exam_prep"
    REVISION = "revision"
    MIXED = "mixed"
    UNCLEAR = "unclear"


class Readiness(Enum):
    READY = "ready"
    NEEDS_CLARIFICATION = "needs_clarification"
    INSUFFICIENT_INPUT = "insufficient_input"


class LessonInfoResponse(BaseModel):
    goal: str
    topic: str | None
    cefr_level: CefrLevel | None
    duration_minutes: int | None
    skills: list[str]
    lesson_type: LessonType | None
    language_focus: list[str]
    based_on_materials: list[str]
    assumptions: list[str]
    missing_info: list[str]
    clarifying_questions: list[str]
    readiness: Readiness | None
    confidence: float





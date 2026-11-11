from enum import Enum

from pydantic import BaseModel


# {
#   "goal": string,
#   "topic": string | null,
#   "cefr_level": "A1"|"A2"|"B1"|"B2"|"C1"|"C2"|null,
#   "duration_minutes": number | null,
#   "skills": string[],
#   "lesson_type": "grammar"|"skills"|"exam_prep"|"revision"|"mixed"|"unclear",
#   "language_focus": string[],
#   "based_on_materials": string[],
#   "assumptions": string[],
#   "missing_info": string[],
#   "clarifying_questions": string[],
#   "readiness": "ready"|"needs_clarification"|"insufficient_input",
#   "confidence": number
# }

class CefrLevel(Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2",

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
    clarifying_questions: list[str]
    readiness: Readiness | None
    confidence: float





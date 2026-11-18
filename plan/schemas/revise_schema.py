from enum import Enum

from pydantic import BaseModel, Field

from plan.schemas.plan_shema import Handout, StageRow, Worksheet


class ReviseScope(str, Enum):
    LOCAL = "local"
    RIPPLE = "ripple"
    FULL = "full"


class ReviseRoute(BaseModel):
    scope: ReviseScope = ReviseScope.LOCAL
    targets: list[str] = Field(default_factory=list)
    set: dict[str, str] = Field(default_factory=dict)


class LessonPlanPatch(BaseModel):
    set: dict[str, str] = Field(default_factory=dict)
    stages: dict[str, StageRow] = Field(default_factory=dict)
    handouts: dict[str, Handout] = Field(default_factory=dict)
    worksheet: Worksheet | None = None

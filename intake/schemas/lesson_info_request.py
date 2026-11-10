from typing import List

from pydantic import BaseModel

class LessonInfoRequest(BaseModel):
    teacher_description: str
    materials: List[str]
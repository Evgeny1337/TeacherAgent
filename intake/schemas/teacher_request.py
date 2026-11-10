from pathlib import Path

from pydantic import BaseModel


class TeacherRequest(BaseModel):
    teacher_description: str
    files: list[Path]
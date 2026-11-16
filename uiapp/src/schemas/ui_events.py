from pathlib import Path

from pydantic import BaseModel, Field


class LessonGenerateEvent(BaseModel):
    file_path: Path
    teacher_description: str = ""
    materials: list[Path] = Field(default_factory=list)
    status: str = "generating"

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


class LessonPreviewEvent(BaseModel):
    title: str
    subtitle: str = ""
    status: str = "preview"
    card_id: str = "preview"


class HistoryEntryEvent(BaseModel):
    text: str

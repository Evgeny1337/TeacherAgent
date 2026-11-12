from typing import List

from pydantic import BaseModel, Field

class LessonHeader(BaseModel):
    date: str = Field(description="Дата урока")
    level: str = Field(description="Уровень")
    teacher: str = Field(description="ФИО учителя")
    aim: str = Field(description="Цель урока")
    sub_aim: str = Field(description="Подцель урока")
    homework_summary: str = Field(description="Краткое дз")

class StageRow(BaseModel):
    title: str = Field(description="Этап")
    procedure: str = Field(description="Текст этапа")
    time_interaction: str = Field(description="Время этапа/номер слайда")

class Handout(BaseModel):
    title: str = Field(description="Заголовок")
    mode: str = Field(description="Вид работы")
    instructions: str = Field(description="Краткая инструкция")
    body: str = Field(description="Содержимое")

class Worksheet(BaseModel):
    title: str = Field(description="Заголовок")
    instructions: str = Field(description="Краткая инструкция")
    body: str = Field(description="Содержимое")


class LessonPlan(BaseModel):
    lesson: LessonHeader
    stages: List[StageRow]
    handouts: List[Handout] | None
    worksheet: Worksheet | None

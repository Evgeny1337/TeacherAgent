from pydantic import BaseModel, Field

class PlanTableRow(BaseModel):
    stage: str = Field(description="Этап урока")
    procedure: str = Field(description="Содержание этапа")
    material_slides: str = Field(description="Ссылки ")

class PlanSchema(BaseModel):
    aim: str = Field(description="Цель урока")
    sub_aim: str =  Field(description="Второстепенная цель")
    homework: str = Field(description="Домашнее задание")
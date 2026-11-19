from pydantic import BaseModel, Field


class PlansResponseSchema(BaseModel):
    plans: list[dict] = Field(description="Список планов уроков")
    plans_count: int = Field(description="Количество планов уроков")

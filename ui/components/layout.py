import os
import httpx
from dotenv import load_dotenv
from nicegui import ui

from ui.components.input_component import make_input_panel
from ui.components.lessons_component import make_lessons_panel
from ui.state.lesson_state import AppState


def build_ui(state: AppState) -> None:
    load_dotenv()
    panels: list = []
    rag_url = os.environ.get("RAG_URL",'http://localhost:8083')
    with httpx.Client() as client:
        response = client.get(rag_url + '/api/teacher/history/')
        lessons = response.json()
        state.lessons = lessons

    def refresh() -> None:
        for panel in panels:
            panel.refresh()

    input_panel = make_input_panel(state, on_refresh=refresh)
    lessons_panel = make_lessons_panel(state, on_refresh=refresh)
    panels.extend([input_panel, lessons_panel])

    # Явный ряд: ввод слева, карточки справа
    with ui.element("div").classes(
        "w-full flex flex-row flex-nowrap items-start gap-4 p-4"
    ):
        with ui.card().classes("w-1/2 min-w-[320px] p-4").style("order: 1"):
            input_panel()
        with ui.card().classes("w-1/2 min-w-[320px] p-4").style("order: 2"):
            lessons_panel()

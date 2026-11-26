import sys
from multiprocessing import freeze_support
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nicegui import ui, native

from ui.components.layout import build_ui
from ui.state.lesson_state import AppState


@ui.page("/")
def index() -> None:
    ui.colors(primary="#1F4E79")
    ui.query("body").classes("bg-grey-2")
    with ui.header().classes("items-center px-4"):
        ui.label("TeacherAgent").classes("text-h6 text-white")
    build_ui(AppState())


# ui.run(title="TeacherAgent", reload=True)


if __name__ in {"__main__", "__mp_main__"}:
    freeze_support()
    ui.run(
        title="TeacherAgent",
        native=True,
        reload=False,
        port=native.find_open_port(),
    )

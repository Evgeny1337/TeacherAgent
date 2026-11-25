from collections.abc import Callable

from nicegui import ui

from ui.components.open_doc import open_document
from ui.state.lesson_state import AppState, LessonStatus

_COLORS = {
    LessonStatus.CREATING: "grey",
    LessonStatus.GENERATED: "positive",
    LessonStatus.ERROR: "negative",
}


def make_lessons_panel(state: AppState, on_refresh: Callable[[], None]):
    @ui.refreshable
    def panel() -> None:
        ui.label("Уроки").classes("text-h6")
        if not state.lessons:
            ui.label("Пока пусто — сгенерируйте слева.").classes(
                "text-caption text-grey-6"
            )
            return

        for item in state.lessons:
            selected = item.id == state.active_id
            border = "border-primary" if selected else "border-grey-4"

            def select(_e=None, lesson_id=item.id) -> None:
                state.active_id = lesson_id
                on_refresh()

            with ui.card().classes(f"w-full cursor-pointer {border}").on(
                "click", select
            ):
                ui.badge(item.status.value, color=_COLORS[item.status])
                ui.label(item.summary or item.description or "Без описания").classes(
                    "text-subtitle1"
                )
                if item.error:
                    ui.label(item.error).classes("text-negative text-sm")

                can_open = (
                    item.status == LessonStatus.GENERATED
                    and item.file_path is not None
                    and item.file_path.is_file()
                )

                def open_click(_e=None, path=item.file_path) -> None:
                    if path:
                        open_document(path)

                btn = ui.button("Открыть документ", on_click=open_click).props(
                    "dense outline"
                )
                if not can_open:
                    btn.disable()

    return panel

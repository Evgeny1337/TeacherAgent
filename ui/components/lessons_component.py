import asyncio
from collections.abc import Callable

from nicegui import ui

from pipeline import create_file_name
from plan.rag import fetch_lesson_data
from plan.recordWord.record_word import record_lesson_plan_to_word
from plan.schemas.plan_shema import LessonPlan
from ui.components.open_doc import open_document
from ui.state.lesson_state import AppState, LessonItem, LessonStatus

_COLORS = {
    LessonStatus.CREATING: "grey",
    LessonStatus.GENERATED: "positive",
    LessonStatus.APPROVED: "blue",
    LessonStatus.READY: "positive",
    LessonStatus.ERROR: "negative",
}


def _short(text: str, limit: int = 100) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _card_title(item: LessonItem) -> str:
    base = item.summary or item.description or "Без описания"
    if " · " in base:
        base = base.split(" · ", 1)[0]
    base = _short(base, 120)
    if item.id is not None:
        return f"#{item.id} · {base}"
    return base


def make_lessons_panel(state: AppState, on_refresh: Callable[[], None]):
    @ui.refreshable
    def panel() -> None:
        ui.label("Уроки").classes("text-h6")
        if not state.lessons:
            ui.label("Пока пусто — сгенерируйте слева.").classes(
                "text-caption text-grey-6"
            )
            return

        with ui.scroll_area().classes("w-full").style(
            "height: calc(100vh - 140px); max-height: 80vh;"
        ):
            with ui.column().classes("w-full gap-2 pr-2"):
                for item in state.lessons:
                    selected = item.local_id == state.active_id
                    border = "border-primary" if selected else "border-grey-4"

                    def select(_e=None, lesson_key=item.local_id) -> None:
                        state.active_id = lesson_key
                        on_refresh()

                    with ui.card().classes(
                        f"w-full cursor-pointer {border}"
                    ).on("click", select):
                        ui.badge(item.status.value, color=_COLORS[item.status])
                        ui.label(_card_title(item)).classes(
                            "text-subtitle1 break-words whitespace-normal"
                        )
                        if item.description and item.description != item.summary:
                            ui.label(_short(item.description, 80)).classes(
                                "text-caption text-grey-7 break-words whitespace-normal"
                            )
                        if item.error:
                            ui.label(_short(item.error, 160)).classes(
                                "text-negative text-sm break-words whitespace-normal"
                            )

                        async def materialize(
                            _e=None, lesson=item
                        ) -> None:
                            if state.busy or lesson.id is None:
                                return
                            client = ui.context.client
                            state.busy = True
                            state.active_id = lesson.local_id
                            with client:
                                on_refresh()
                            try:
                                data = await asyncio.to_thread(
                                    fetch_lesson_data, lesson.id
                                )
                                out = create_file_name()
                                plan_json = data.get("plan_json")
                                if not isinstance(plan_json, dict):
                                    raise ValueError("Нет plan_json в ответе")
                                plan = LessonPlan.model_validate(plan_json)
                                await asyncio.to_thread(
                                    record_lesson_plan_to_word, plan, out
                                )
                                lesson.apply_remote_data(data, out)
                                with client:
                                    ui.notify(
                                        f"Документ готов: {out.name}",
                                        type="positive",
                                    )
                            except Exception as exc:
                                lesson.set_error(str(exc))
                                with client:
                                    ui.notify(str(exc), type="negative")
                            finally:
                                state.busy = False
                                with client:
                                    on_refresh()

                        def open_click(_e=None, path=item.file_path) -> None:
                            if path:
                                open_document(path)

                        if item.can_open:
                            ui.button(
                                "Открыть документ", on_click=open_click
                            ).props("dense outline")
                        elif item.can_materialize:
                            btn = ui.button(
                                "Сгенерировать документ",
                                on_click=materialize,
                            ).props("dense outline color=primary")
                            if state.busy:
                                btn.disable()

    return panel

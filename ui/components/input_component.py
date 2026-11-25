import asyncio
import tempfile
from collections.abc import Callable
from pathlib import Path

from nicegui import events, ui

from pipeline import create_file_name, run_generate_lesson, run_revise_lesson
from plan.rag import save_lesson
from ui.state.lesson_state import AppState, LessonItem, LessonStatus

_ALLOWED = {".docx", ".pdf", ".pptx"}


def make_input_panel(state: AppState, on_refresh: Callable[[], None]):
    temp_dir = Path(tempfile.mkdtemp(prefix="teacheragent_"))
    description_box: dict[str, ui.textarea | None] = {"el": None}

    async def on_upload(e: events.UploadEventArguments) -> None:
        client = ui.context.client
        name = Path(e.file.name or "file").name
        if Path(name).suffix.lower() not in _ALLOWED:
            with client:
                ui.notify("Нужен .docx / .pdf / .pptx", type="warning")
            return
        target = temp_dir / name
        await e.file.save(target)
        if target not in state.draft_paths:
            state.draft_paths.append(target)
        with client:
            on_refresh()

    async def generate() -> None:
        client = ui.context.client
        box = description_box["el"]
        text = (box.value or "").strip() if box is not None else ""
        if state.busy or (not text and not state.draft_paths):
            with client:
                ui.notify("Добавьте описание или файлы", type="warning")
            return

        item = LessonItem(
            description=text,
            materials=list(state.draft_paths),
            summary=(text[:80] + "…") if len(text) > 80 else (text or "Без описания"),
        )
        state.lessons.insert(0, item)
        state.active_id = item.local_id
        state.busy = True
        with client:
            on_refresh()

        message = ""
        kind = "positive"
        try:
            out = create_file_name()
            plan = await asyncio.to_thread(
                run_generate_lesson, list(state.draft_paths), text, out
            )
            item.set_plan(plan, out)
            message = f"Готово: {out.name}"
        except Exception as exc:
            item.set_error(str(exc))
            message = str(exc)
            kind = "negative"
        finally:
            state.busy = False
            with client:
                ui.notify(message, type=kind)
                on_refresh()

    async def revise() -> None:
        client = ui.context.client
        current = state.active
        box = description_box["el"]
        notes = (box.value or "").strip() if box is not None else ""
        if state.busy or not current or not current.plan:
            with client:
                ui.notify("Нет плана для доработки", type="warning")
            return
        if not notes:
            with client:
                ui.notify("Напишите замечания", type="warning")
            return

        state.busy = True
        with client:
            on_refresh()

        message = ""
        kind = "positive"
        try:
            out = current.file_path or create_file_name()
            materials = list(state.draft_paths) or list(current.materials)
            plan = await asyncio.to_thread(
                run_revise_lesson, current.plan, notes, out, materials
            )
            current.description = notes
            current.set_plan(plan, out)
            message = "План обновлён"
        except Exception as exc:
            current.set_error(str(exc))
            message = str(exc)
            kind = "negative"
        finally:
            state.busy = False
            with client:
                ui.notify(message, type=kind)
                on_refresh()

    def new_dialog() -> None:
        state.clear_draft()
        on_refresh()

    def approve() -> None:
        lesson_item = state.active
        if not lesson_item or not lesson_item.plan:
            ui.notify("Нет плана для апрува", type="warning")
            return
        try:
            save_lesson(lesson_item.get_plan_for_request())
        except Exception as exc:
            ui.notify(f"Апрув не удался: {exc}", type="negative")
            return
        lesson_item.mark_approved()
        ui.notify("Урок принят", type="positive")
        new_dialog()

    @ui.refreshable
    def panel() -> None:
        active = state.active
        approved = active is not None and active.is_approved
        ready = (
            active is not None
            and active.status == LessonStatus.GENERATED
            and not state.busy
            and not approved
        )

        ui.label("Диалог урока").classes("text-h6")
        textarea = (
            ui.textarea(
                label="Описание / замечания",
                placeholder="Тема, уровень, что учесть…",
                value=(
                    active.description
                    if active and (ready or approved)
                    else ""
                ),
            )
            .classes("w-full")
            .props("outlined autogrow")
        )
        description_box["el"] = textarea
        if approved:
            textarea.props("readonly")

        if not approved:
            ui.upload(
                label="Прикрепить файлы",
                multiple=True,
                auto_upload=True,
                on_upload=on_upload,
            ).props("accept=.docx,.pdf,.pptx").classes("w-full")

            if state.draft_paths:
                for path in state.draft_paths:
                    ui.label(f"• {path.name}").classes("text-sm")
            else:
                ui.label("Файлы не выбраны").classes("text-caption text-grey-6")

        if state.busy:
            with ui.row().classes("items-center gap-2"):
                ui.spinner(size="sm")
                ui.label("Идёт генерация…")

        with ui.row().classes("gap-2 flex-wrap"):
            if ready:
                ui.button("Апрув", on_click=approve).props("color=positive")
                ui.button("На доработку", on_click=revise).props("outline")
                ui.button("Новый диалог", on_click=new_dialog).props("flat")
            elif approved:
                ui.label("Урок уже в истории").classes("text-caption text-grey-7")
                ui.button("Новый диалог", on_click=new_dialog).props("flat")
            else:
                btn = ui.button("Сгенерировать", on_click=generate).props(
                    "color=primary"
                )
                if state.busy:
                    btn.disable()

    return panel

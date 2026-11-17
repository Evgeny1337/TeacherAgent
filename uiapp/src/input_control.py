import asyncio
from collections.abc import Callable
from pathlib import Path

import flet as ft

from layout_utils import actions_bar
from pipeline import create_file_name, run_generate_lesson, run_revise_lesson
from schemas.lesson_session import LessonStatus
from schemas.ui_events import LessonGenerateEvent

_FILES_LIST_HEIGHT = 96


def build_input_control(
    page: ft.Page,
    on_lesson_generate: Callable[[LessonGenerateEvent], bool],
    on_lesson_ready: Callable[[LessonGenerateEvent], bool],
    on_lesson_failed: Callable[[LessonGenerateEvent, Exception], bool],
) -> ft.Control:
    description = ft.TextField(
        label="Задайте описание урока",
        expand=True,
        multiline=True,
        min_lines=3,
        shift_enter=True,
    )
    selected_paths: list[Path] = []
    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    files_list = ft.ListView(expand=True, spacing=4, auto_scroll=True)
    files_count = ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
    clear_all_btn = ft.TextButton("Очистить", visible=False)

    def _session_busy() -> bool:
        session = page.app_state.active
        return session is not None and session.status in (
            LessonStatus.GENERATING,
            LessonStatus.REVISING,
        )

    def _sync_own_btn() -> None:
        own_btn = (getattr(page, "ui", {}) or {}).get("own_btn")
        session = page.app_state.active
        if own_btn is None or session is None:
            return
        if session.status is LessonStatus.READY:
            own_btn.disabled = len(selected_paths) != 1
        page.update()

    def _reset_input() -> None:
        page.app_state.active = None
        description.value = ""
        selected_paths.clear()
        _refresh_files_view()
        sync = getattr(page, "sync_actions", None)
        if sync is not None:
            sync(None)
        else:
            page.update()

    def _remove_file(path: Path):
        def handler(e: ft.Event[ft.IconButton]):
            if _session_busy():
                return
            if path not in selected_paths:
                return
            selected_paths.remove(path)
            _refresh_files_view()
            _sync_own_btn()

        return handler

    def _clear_all(e: ft.Event[ft.TextButton]):
        if _session_busy():
            return
        selected_paths.clear()
        _refresh_files_view()
        _sync_own_btn()

    clear_all_btn.on_click = _clear_all

    def _empty_files_placeholder() -> ft.Control:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER_LEFT,
            content=ft.Text(
                "Файлы не выбраны",
                size=13,
                color=ft.Colors.ON_SURFACE_VARIANT,
                italic=True,
            ),
        )

    def _file_row(path: Path) -> ft.Control:
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=ft.BorderRadius.all(6),
            bgcolor=ft.Colors.SURFACE,
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=16),
                    ft.Text(
                        path.name,
                        size=12,
                        expand=True,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=16,
                        tooltip="Открепить",
                        disabled=_session_busy(),
                        on_click=_remove_file(path),
                    ),
                ],
            ),
        )

    def _refresh_files_view() -> None:
        count = len(selected_paths)
        if count == 0:
            files_count.value = ""
            clear_all_btn.visible = False
            files_list.controls = [_empty_files_placeholder()]
            return

        files_count.value = f"{count} файл(ов)"
        clear_all_btn.visible = True
        files_list.controls = [_file_row(path) for path in selected_paths]

    files_box = ft.Container(
        height=_FILES_LIST_HEIGHT + 48,
        padding=12,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=ft.BorderRadius.all(8),
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        content=ft.Column(
            expand=True,
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.ATTACH_FILE, size=18),
                        ft.Text(
                            "Материалы",
                            weight=ft.FontWeight.BOLD,
                            size=13,
                            expand=True,
                        ),
                        files_count,
                        clear_all_btn,
                    ],
                ),
                ft.Container(expand=True, content=files_list),
            ],
        ),
    )

    async def on_pick_files(e: ft.Event[ft.Button]):
        if _session_busy():
            return
        files = await file_picker.pick_files(
            allow_multiple=True,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["docx", "pdf", "pptx"],
        )
        if files:
            for f in files:
                if not f.path:
                    continue
                path = Path(f.path)
                if path in selected_paths:
                    continue
                selected_paths.append(path)
            _refresh_files_view()
            _sync_own_btn()
        page.update()

    async def on_send_request(e: ft.Event[ft.Button]):
        if page.app_state.active is not None:
            return
        file_name = create_file_name()
        event = LessonGenerateEvent(
            file_path=file_name,
            teacher_description=description.value or "",
            materials=list(selected_paths),
        )
        selected_paths.clear()
        _refresh_files_view()
        on_lesson_generate(event)
        try:
            plan = await asyncio.to_thread(
                run_generate_lesson,
                file_name=file_name,
                teacher_description=event.teacher_description,
                materials=event.materials,
            )
            on_lesson_ready(
                event.model_copy(
                    update={"status": LessonStatus.READY, "plan": plan}
                )
            )
        except Exception as exc:
            on_lesson_failed(
                event.model_copy(update={"status": LessonStatus.ERROR}),
                exc,
            )
        page.update()

    async def on_revise(e: ft.Event[ft.Button]):
        session = page.app_state.active
        if session is None or session.status is not LessonStatus.READY:
            return
        if session.plan is None:
            page.show_dialog(ft.SnackBar(ft.Text("Нет плана для доработки")))
            return
        notes = (description.value or "").strip()
        if not notes:
            page.show_dialog(ft.SnackBar(ft.Text("Опишите, что доработать")))
            return
        session.revision_notes = notes
        previous_plan = session.plan
        file_path = session.file_path
        materials = list(session.materials)
        event = LessonGenerateEvent(
            file_path=file_path,
            teacher_description=notes,
            materials=materials,
            status=LessonStatus.REVISING,
            plan=previous_plan,
        )
        on_lesson_generate(event)
        try:
            plan = await asyncio.to_thread(
                run_revise_lesson,
                previous_plan=previous_plan,
                revision_notes=notes,
                file_name=file_path,
                materials=materials,
            )
            on_lesson_ready(
                event.model_copy(
                    update={"status": LessonStatus.READY, "plan": plan}
                )
            )
        except Exception as exc:
            on_lesson_failed(
                event.model_copy(update={"status": LessonStatus.ERROR}),
                exc,
            )
        page.update()

    def on_own_file(e: ft.Event[ft.Button]):
        session = page.app_state.active
        if session is None or session.status is not LessonStatus.READY:
            return
        if len(selected_paths) == 0:
            page.show_dialog(ft.SnackBar(ft.Text("Приложите один свой файл")))
            return
        if len(selected_paths) > 1:
            page.show_dialog(
                ft.SnackBar(ft.Text("Для подтверждения нужен ровно один файл"))
            )
            return
        own_path = selected_paths[0]
        confirm_active = getattr(page, "confirm_active", None)
        if confirm_active is None or not confirm_active(own_path):
            return
        page.show_dialog(
            ft.SnackBar(ft.Text(f"Подтверждён свой файл: {own_path.name}"))
        )
        description.value = ""
        selected_paths.clear()
        _refresh_files_view()
        sync = getattr(page, "sync_actions", None)
        if sync is not None:
            sync(None)
        else:
            page.update()

    def on_new_request(e: ft.Event[ft.Button]):
        _reset_input()

    _refresh_files_view()

    attach_btn = ft.OutlinedButton("Прикрепить", on_click=on_pick_files)
    generate_btn = ft.Button("Сгенерировать", on_click=on_send_request)
    revise_btn = ft.OutlinedButton("На доработку", on_click=on_revise, visible=False)
    own_btn = ft.OutlinedButton("Свой файл", on_click=on_own_file, visible=False)
    new_btn = ft.OutlinedButton("Новый запрос", on_click=on_new_request, visible=False)

    page.ui = {
        "description": description,
        "attach_btn": attach_btn,
        "clear_all_btn": clear_all_btn,
        "generate_btn": generate_btn,
        "revise_btn": revise_btn,
        "own_btn": own_btn,
        "new_btn": new_btn,
        "refresh_files": _refresh_files_view,
        "selected_paths": selected_paths,
        "sync_own_btn": _sync_own_btn,
    }
    sync_actions = getattr(page, "sync_actions", None)
    if sync_actions is not None:
        active = page.app_state.active
        sync_actions(active.status if active is not None else None)

    return ft.Column(
        expand=True,
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Text("Вход", weight=ft.FontWeight.BOLD),
            ft.Container(expand=True, content=description),
            files_box,
            actions_bar(attach_btn, generate_btn, revise_btn, own_btn, new_btn),
        ],
    )

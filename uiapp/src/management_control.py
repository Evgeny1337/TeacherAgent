import asyncio
from collections.abc import Callable
from pathlib import Path

import flet as ft

from layout_utils import actions_bar
from plan.recordWord.record_word import record_lesson_plan_to_word
from plan.schemas.plan_shema import LessonPlan
from schemas.ui_events import LessonGenerateEvent, LessonPreviewEvent


def build_management_control(
    page: ft.Page,
) -> tuple[
    ft.Control,
    Callable[[LessonPreviewEvent], None],
    Callable[[LessonGenerateEvent], bool],
    Callable[[LessonGenerateEvent], bool],
    Callable[[LessonGenerateEvent, Exception], bool],
]:
    cards_list = ft.ListView(expand=True, spacing=8, auto_scroll=True)
    progress_bar = ft.ProgressBar()
    status_text = ft.Text("Статус: —", size=13)

    async def on_download(e: ft.Event[ft.OutlinedButton]):
        payload = e.control.data
        if not isinstance(payload, dict):
            page.show_dialog(ft.SnackBar(ft.Text("Нет данных для сохранения")))
            return
        plan = payload.get("plan")
        file_path = payload.get("file_path")
        if not isinstance(plan, LessonPlan) or not isinstance(file_path, Path):
            page.show_dialog(ft.SnackBar(ft.Text("Некорректные данные плана")))
            return
        try:
            saved = await asyncio.to_thread(
                record_lesson_plan_to_word,
                plan,
                file_path,
            )
            page.show_dialog(
                ft.SnackBar(ft.Text(f"Файл сохранён: {saved}"))
            )
        except Exception as exc:
            page.show_dialog(
                ft.SnackBar(ft.Text(f"Ошибка сохранения: {exc}"))
            )

    def on_confirm(e: ft.Event[ft.Button]):
        pass

    def on_confirm_own_file(e: ft.Event[ft.Button]):
        pass

    def on_send_revise(e: ft.Event[ft.Button]):
        pass

    def _make_card(event: LessonPreviewEvent) -> ft.Card:
        return ft.Card(
            data={"card_id": event.card_id},
            content=ft.Container(
                padding=10,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED),
                            title=ft.Text(event.title, weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(event.subtitle, size=13),
                            trailing=ft.Text(event.status, size=12),
                        ),
                    ],
                ),
            ),
        )

    def _find_card(card_id: str) -> ft.Card | None:
        for control in cards_list.controls:
            if (
                isinstance(control, ft.Card)
                and isinstance(control.data, dict)
                and control.data.get("card_id") == card_id
            ):
                return control
        return None

    def _set_card_status(
        card: ft.Card,
        status: str,
        subtitle: str | None = None,
    ) -> None:
        tile = card.content.content.controls[0]
        tile.trailing = ft.Text(status, size=12)
        if subtitle is not None:
            tile.subtitle = ft.Text(subtitle, size=13)
        status_text.value = f"Статус: {status}"
        page.update()

    def add_preview(event: LessonPreviewEvent) -> None:
        title = (event.title or "").strip()
        if not title:
            return
        cards_list.controls.append(
            _make_card(
                LessonPreviewEvent(
                    title=title,
                    subtitle=event.subtitle,
                    status=event.status,
                    card_id=event.card_id,
                )
            )
        )
        status_text.value = f"Статус: {event.status}"
        page.update()

    def on_lesson_generate(event: LessonGenerateEvent) -> bool:
        title = (event.title or "").strip()
        if not title:
            raise ValueError("Пустой заголовок")
        if not event.card_id:
            raise ValueError("Ошибка получения id для каточки")
        cards_list.controls.append(
            _make_card(
                LessonPreviewEvent(
                    title=title,
                    subtitle=event.subtitle,
                    status=event.status,
                    card_id=event.card_id,
                )
            )
        )
        status_text.value = f"Статус: {event.status}"
        page.update()
        return True

    def on_lesson_ready(event: LessonGenerateEvent) -> bool:
        card = _find_card(event.card_id)
        if card is None or event.plan is None:
            return False
        _set_card_status(card, event.status or "ready")
        column = card.content.content
        column.controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.OutlinedButton(
                        "Скачать",
                        data={
                            "plan": event.plan,
                            "file_path": event.file_path,
                        },
                        on_click=on_download,
                    ),
                ],
            )
        )
        page.update()
        return True

    def on_lesson_failed(event: LessonGenerateEvent, error: Exception) -> bool:
        card = _find_card(event.card_id)
        if card is None:
            return False
        message = str(error).strip() or type(error).__name__
        if len(message) > 80:
            message = f"{message[:77]}..."
        _set_card_status(card, event.status or "error", subtitle=message)
        return True

    add_preview(
        LessonPreviewEvent(
            title="v1 · черновик плана",
            subtitle="Aim / stages появятся после генерации",
            status="preview",
            card_id="preview",
        )
    )

    panel = ft.Column(
        expand=True,
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Text("Результат / превью", weight=ft.FontWeight.BOLD),
            status_text,
            progress_bar,
            cards_list,
            actions_bar(
                ft.Button("Подтвердить", on_click=on_confirm),
                ft.OutlinedButton("Свой файл", on_click=on_confirm_own_file),
                ft.OutlinedButton("На доработку", on_click=on_send_revise),
            ),
        ],
    )
    return panel, add_preview, on_lesson_generate, on_lesson_ready, on_lesson_failed

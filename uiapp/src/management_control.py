from pathlib import Path

import flet as ft

from layout_utils import actions_bar
from schemas.lesson_session import LessonSession, LessonStatus
from schemas.ui_events import LessonGenerateEvent, ManagementControl
from session_store import clear as clear_session
from session_store import save as save_session


def build_management_control(page: ft.Page) -> ManagementControl:
    cards_list = ft.ListView(expand=True, spacing=8, auto_scroll=True)
    status_text = ft.Text("Статус: —", size=13)

    def _confirm_active(file_path: Path | None = None) -> bool:
        session = page.app_state.active
        if session is None or session.status != LessonStatus.READY:
            return False
        card = _find_card(session.id)
        if card is None:
            return False
        path = file_path or session.file_path
        session.status = LessonStatus.CONFIRMED
        session.file_path = path
        _update_card(
            card,
            LessonStatus.CONFIRMED,
            subtitle=str(path),
            file_path=str(path),
        )
        page.app_state.active = None
        clear_session()
        _sync_actions(None)
        return True

    def on_confirm(e: ft.Event[ft.Button]):
        if _confirm_active():
            page.show_dialog(ft.SnackBar(ft.Text("Урок подтверждён")))

    confirm_btn = ft.Button("Подтвердить", on_click=on_confirm, disabled=True)
    page.confirm_active = _confirm_active

    def _sync_actions(status: LessonStatus | None) -> None:
        ui = getattr(page, "ui", {}) or {}
        idle = status is None
        busy = status in (LessonStatus.GENERATING, LessonStatus.REVISING)
        ready = status is LessonStatus.READY
        has_session = status is not None

        description = ui.get("description")
        if description is not None:
            description.disabled = busy

        for key in ("attach_btn", "clear_all_btn"):
            control = ui.get(key)
            if control is not None:
                control.disabled = busy

        generate_btn = ui.get("generate_btn")
        revise_btn = ui.get("revise_btn")
        own_btn = ui.get("own_btn")
        new_btn = ui.get("new_btn")
        if generate_btn is not None:
            generate_btn.visible = idle
            generate_btn.disabled = False
        if revise_btn is not None:
            revise_btn.visible = has_session
            revise_btn.disabled = not ready
        if own_btn is not None:
            own_btn.visible = has_session
            if ready:
                paths = ui.get("selected_paths") or []
                own_btn.disabled = len(paths) != 1
            else:
                own_btn.disabled = True
        if new_btn is not None:
            new_btn.visible = has_session
            new_btn.disabled = busy

        refresh_files = ui.get("refresh_files")
        if callable(refresh_files):
            refresh_files()

        confirm_btn.disabled = not ready
        page.update()

    page.sync_actions = _sync_actions

    def _make_card(
        card_id: str,
        title: str,
        subtitle: str,
        status: LessonStatus,
        file_path: str | None = None,
    ) -> ft.Card:
        return ft.Card(
            data={"card_id": card_id, "file_path": file_path},
            content=ft.Container(
                padding=10,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED),
                            title=ft.Text(title, weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(subtitle, size=13),
                            trailing=ft.Text(str(status), size=12),
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

    def _update_card(
        card: ft.Card,
        status: LessonStatus,
        subtitle: str | None = None,
        file_path: str | None = None,
    ) -> None:
        tile = card.content.content.controls[0]
        tile.trailing = ft.Text(str(status), size=12)
        if subtitle is not None:
            tile.subtitle = ft.Text(subtitle, size=13)
        if file_path is not None and isinstance(card.data, dict):
            card.data["file_path"] = file_path
        status_text.value = f"Статус: {status}"
        page.update()

    def restore_active_session() -> None:
        session: LessonSession | None = page.app_state.active
        if session is None:
            return
        if _find_card(session.id) is not None:
            return
        event = LessonGenerateEvent(
            file_path=session.file_path,
            teacher_description=session.teacher_description,
            materials=session.materials,
            status=session.status,
            plan=session.plan,
        )
        path_text = str(session.file_path)
        subtitle = (
            path_text if session.status is LessonStatus.READY else event.subtitle
        )
        cards_list.controls.append(
            _make_card(
                session.id,
                event.title,
                subtitle,
                session.status,
                file_path=path_text,
            )
        )
        status_text.value = f"Статус: {session.status}"
        _sync_actions(session.status)

    def on_lesson_generate(event: LessonGenerateEvent) -> bool:
        title = (event.title or "").strip()
        if not title and event.status is not LessonStatus.REVISING:
            raise ValueError("Пустой заголовок")
        status = event.status or LessonStatus.GENERATING

        if status is LessonStatus.REVISING:
            session = page.app_state.active
            if session is None or session.id != event.card_id:
                return False
            session.status = status
            session.revision_notes = event.teacher_description
            save_session(session)
            card = _find_card(event.card_id)
            if card is not None:
                _update_card(card, status)
            _sync_actions(status)
            return True

        _sync_actions(status)
        cards_list.controls.append(
            _make_card(
                event.card_id,
                title,
                event.subtitle,
                status,
            )
        )
        session = LessonSession(
            id=event.card_id,
            file_path=event.file_path,
            teacher_description=event.teacher_description,
            materials=event.materials,
            plan=event.plan,
            status=status,
        )
        page.app_state.active = session
        save_session(session)
        status_text.value = f"Статус: {status}"
        page.update()
        return True

    def on_lesson_ready(event: LessonGenerateEvent) -> bool:
        if event.plan is None:
            return False
        status = event.status or LessonStatus.READY
        path_text = str(event.file_path)
        session = page.app_state.active
        if session and session.id == event.card_id:
            session.plan = event.plan
            session.status = status
            session.file_path = event.file_path
            save_session(session)
        card = _find_card(event.card_id)
        if card is None:
            return False
        _update_card(card, status, subtitle=path_text, file_path=path_text)
        _sync_actions(status)
        page.show_dialog(ft.SnackBar(ft.Text(f"Файл готов: {event.file_path.name}")))
        return True

    def on_lesson_failed(event: LessonGenerateEvent, error: Exception) -> bool:
        status = event.status or LessonStatus.ERROR
        session = page.app_state.active
        if session and session.id == event.card_id:
            session.status = status
            save_session(session)
        card = _find_card(event.card_id)
        if card is None:
            return False
        message = str(error).strip() or type(error).__name__
        if len(message) > 80:
            message = f"{message[:77]}..."
        _update_card(card, status, subtitle=message)
        _sync_actions(status)
        return True

    panel = ft.Column(
        expand=True,
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Text("Результат / превью", weight=ft.FontWeight.BOLD),
            status_text,
            cards_list,
            actions_bar(confirm_btn),
        ],
    )
    _sync_actions(None)
    return ManagementControl(
        panel=panel,
        on_lesson_generate=on_lesson_generate,
        on_lesson_ready=on_lesson_ready,
        on_lesson_failed=on_lesson_failed,
        restore_active_session=restore_active_session,
    )

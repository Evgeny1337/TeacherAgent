import flet as ft

from history_control import build_history_control
from input_control import build_input_control
from management_control import build_management_control
from schemas.lesson_session import AppState
from session_store import clear as clear_session
from session_store import load as load_session
from session_store import save as save_session


def _section(content: ft.Control, *, expand: bool = False) -> ft.Container:
    return ft.Container(
        content=content,
        expand=expand,
        padding=12,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=ft.BorderRadius.all(8),
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
    )


async def _on_window_event(e: ft.WindowEvent) -> None:
    if e.type != ft.WindowEventType.CLOSE:
        return
    session = e.page.app_state.active
    if session is not None:
        save_session(session)
    else:
        clear_session()
    await e.page.window.destroy()


def main(page: ft.Page):
    page.title = "TeacherAgent"
    page.padding = 16
    page.app_state = AppState()
    page.window.prevent_close = True
    page.window.on_event = _on_window_event

    page.app_state.active = load_session()

    management = build_management_control(page)
    input_panel = build_input_control(
        page,
        management.on_lesson_generate,
        management.on_lesson_ready,
        management.on_lesson_failed,
    )
    management.restore_active_session()
    history_panel, _add_entry = build_history_control(page)

    page.add(
        ft.Column(
            expand=True,
            spacing=12,
            controls=[
                ft.Row(
                    expand=True,
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        _section(input_panel, expand=True),
                        ft.VerticalDivider(width=1, color=ft.Colors.OUTLINE_VARIANT),
                        _section(management.panel, expand=True),
                    ],
                ),
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                _section(history_panel),
            ],
        )
    )


if __name__ == "__main__":
    ft.run(main)

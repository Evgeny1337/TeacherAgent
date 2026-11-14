import flet as ft

from history_control import build_history_control
from input_control import build_input_control
from management_control import build_management_control


def _section(content: ft.Control, *, expand: bool = False) -> ft.Container:
    return ft.Container(
        content=content,
        expand=expand,
        padding=12,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=ft.BorderRadius.all(8),
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
    )


def main(page: ft.Page):
    page.title = "TeacherAgent"
    page.padding = 16

    input_panel = build_input_control(page)
    result_panel, _add_preview = build_management_control(page)
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
                        _section(result_panel, expand=True),
                    ],
                ),
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                _section(history_panel),
            ],
        )
    )


if __name__ == "__main__":
    ft.run(main)

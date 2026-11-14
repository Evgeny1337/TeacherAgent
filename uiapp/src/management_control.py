import flet as ft
from collections.abc import Callable


def add_management_control(page: ft.Page) -> Callable[[str, str, str], None]:
    cards_list = ft.ListView(height=160, spacing=8, auto_scroll=True)
    progress_bar = ft.ProgressBar()
    status_text = ft.Text("Статус: —", size=13)

    def on_download(e: ft.Event[ft.Button]):
        pass

    def on_confirm(e: ft.Event[ft.Button]):
        pass

    def on_confirm_own_file(e: ft.Event[ft.Button]):
        pass

    def on_send_revise(e: ft.Event[ft.Button]):
        pass

    def _make_card(title: str, subtitle: str, status: str) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                padding=10,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED),
                            title=ft.Text(title, weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(subtitle, size=13),
                            trailing=ft.Text(status, size=12),
                        ),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.Button("Скачать", on_click=on_download),
                            ],
                        ),
                    ],
                ),
            )
        )

    def add_preview(title: str, subtitle: str, status: str = "preview") -> None:
        title = (title or "").strip()
        if not title:
            return
        cards_list.controls.append(_make_card(title, subtitle, status))
        status_text.value = f"Статус: {status}"
        page.update()

    add_preview(
        "v1 · черновик плана",
        "Aim / stages появятся после генерации",
        "preview",
    )

    page.add(
        ft.Text("Результат / превью", weight=ft.FontWeight.BOLD),
        status_text,
        progress_bar,
        cards_list,
        ft.Row(
            controls=[
                ft.Button("Подтвердить", on_click=on_confirm),
                ft.Button("Подтвердить своим файлом", on_click=on_confirm_own_file),
                ft.Button("Отправить на доработку", on_click=on_send_revise),
            ],
        ),
    )
    return add_preview

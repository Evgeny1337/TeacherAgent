import flet as ft
from collections import deque
from collections.abc import Callable


def build_history_control(
    page: ft.Page,
) -> tuple[ft.Control, Callable[[str], None]]:
    entries: deque[str] = deque(maxlen=20)
    list_view = ft.ListView(height=100, spacing=2, auto_scroll=True)

    def add_entry(text: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        entries.append(text)
        list_view.controls = [ft.Text(f"• {item}", size=13) for item in entries]
        page.update()

    panel = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Text("История", weight=ft.FontWeight.BOLD),
            list_view,
        ],
    )
    return panel, add_entry

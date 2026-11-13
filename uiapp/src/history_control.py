import flet as ft
from collections import deque
from collections.abc import Callable


def add_history_control(page: ft.Page) -> Callable[[str], None]:
    entries: deque[str] = deque(maxlen=20)
    list_view = ft.ListView(height=160, spacing=2, auto_scroll=True)

    def add_entry(text: str) -> None:
        text = (text or "").strip()
        if not text:
            return
        entries.append(text)
        list_view.controls = [ft.Text(f"• {item}", size=13) for item in entries]
        page.update()

    page.add(
        ft.Text("История", weight=ft.FontWeight.BOLD),
        list_view,
    )
    return add_entry

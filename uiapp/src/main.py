import flet as ft

from history_control import add_history_control


def main(page: ft.Page):
    page.title = "TeacherAgent"
    add_entry = add_history_control(page)

    def on_demo_click(e: ft.Event[ft.Button]):
        add_entry("Сгенерирован черновик плана")
        add_entry("Открыт out.docx")

    page.add(ft.Button("Демо: событие", on_click=on_demo_click))


if __name__ == "__main__":
    ft.run(main)

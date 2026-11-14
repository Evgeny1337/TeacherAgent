import flet as ft

from management_control import add_management_control


def main(page: ft.Page):
    page.title = "TeacherAgent"
    add_management_control(page)


if __name__ == "__main__":
    ft.run(main)

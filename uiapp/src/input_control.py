import flet as ft


def add_input_control(page: ft.Page) -> None:
    description = ft.TextField(
        label="Задайте описание урока",
        expand=True,
        multiline=True,
        min_lines=3,
    )
    file_label = ft.Text("файл: —", size=13)
    selected_paths: list[str] = []
    file_picker = ft.FilePicker()

    async def on_pick_files(e: ft.Event[ft.Button]):
        files = await file_picker.pick_files(
            allow_multiple=True,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["docx", "pdf", "pptx"],
        )
        if not files:
            return
        selected_paths.clear()
        selected_paths.extend(f.path for f in files if f.path)
        file_label.value = "файл: " + ", ".join(f.name for f in files)
        page.update()

    def on_send_request(e: ft.Event[ft.Button]):
        description.value = ""
        page.update()

    page.add(
        ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.END,
            controls=[
                description,
                file_label,
                ft.Row(
                    controls=[
                        ft.Button("Прикрепить материалы", on_click=on_pick_files),
                        ft.Button("Сгенерировать", on_click=on_send_request),
                    ],
                ),
            ],
        )
    )

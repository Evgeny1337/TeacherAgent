import flet as ft

from layout_utils import actions_bar

_FILES_LIST_HEIGHT = 96


def build_input_control(page: ft.Page) -> ft.Control:
    """
    Layout (top → bottom, fixed footer):
      header
      description  (expands, fills free space)
      materials    (fixed height + scroll)
      actions_bar  (always pinned at bottom)
    """
    description = ft.TextField(
        label="Задайте описание урока",
        expand=True,
        multiline=True,
        min_lines=3,
        shift_enter=True,
    )
    selected_paths: list[str] = []
    selected_names: list[str] = []
    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    files_list = ft.ListView(expand=True, spacing=4, auto_scroll=True)
    files_count = ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
    clear_all_btn = ft.TextButton("Очистить", visible=False)

    def _remove_file(path: str):
        def handler(e: ft.Event[ft.IconButton]):
            if path not in selected_paths:
                return
            index = selected_paths.index(path)
            selected_paths.pop(index)
            selected_names.pop(index)
            _refresh_files_view()
            page.update()

        return handler

    def _clear_all(e: ft.Event[ft.TextButton]):
        selected_paths.clear()
        selected_names.clear()
        _refresh_files_view()
        page.update()

    clear_all_btn.on_click = _clear_all

    def _empty_files_placeholder() -> ft.Control:
        return ft.Container(
            expand=True,
            alignment=ft.Alignment.CENTER_LEFT,
            content=ft.Text(
                "Файлы не выбраны",
                size=13,
                color=ft.Colors.ON_SURFACE_VARIANT,
                italic=True,
            ),
        )

    def _file_row(path: str, name: str) -> ft.Control:
        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=ft.BorderRadius.all(6),
            bgcolor=ft.Colors.SURFACE,
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, size=16),
                    ft.Text(
                        name,
                        size=12,
                        expand=True,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=16,
                        tooltip="Открепить",
                        on_click=_remove_file(path),
                    ),
                ],
            ),
        )

    def _refresh_files_view() -> None:
        count = len(selected_names)
        if count == 0:
            files_count.value = ""
            clear_all_btn.visible = False
            files_list.controls = [_empty_files_placeholder()]
            return

        files_count.value = f"{count} файл(ов)"
        clear_all_btn.visible = True
        files_list.controls = [
            _file_row(path, name)
            for path, name in zip(selected_paths, selected_names)
        ]

    # Fixed-height materials block — attaching files must not push actions away.
    files_box = ft.Container(
        height=_FILES_LIST_HEIGHT + 48,
        padding=12,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=ft.BorderRadius.all(8),
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        content=ft.Column(
            expand=True,
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.ATTACH_FILE, size=18),
                        ft.Text(
                            "Материалы",
                            weight=ft.FontWeight.BOLD,
                            size=13,
                            expand=True,
                        ),
                        files_count,
                        clear_all_btn,
                    ],
                ),
                ft.Container(expand=True, content=files_list),
            ],
        ),
    )

    async def on_pick_files(e: ft.Event[ft.Button]):
        saved_description = description.value or ""
        files = await file_picker.pick_files(
            allow_multiple=True,
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["docx", "pdf", "pptx"],
        )
        description.value = saved_description
        if files:
            for f in files:
                if not f.path or f.path in selected_paths:
                    continue
                selected_paths.append(f.path)
                selected_names.append(f.name)
            _refresh_files_view()
        page.update()

    def on_send_request(e: ft.Event[ft.Button]):
        description.value = ""
        page.update()

    _refresh_files_view()

    return ft.Column(
        expand=True,
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Text("Вход", weight=ft.FontWeight.BOLD),
            ft.Container(expand=True, content=description),
            files_box,
            actions_bar(
                ft.OutlinedButton("Прикрепить", on_click=on_pick_files),
                ft.Button("Сгенерировать", on_click=on_send_request),
            ),
        ],
    )

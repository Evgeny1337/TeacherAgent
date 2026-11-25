import os
import platform
import subprocess
from pathlib import Path

from nicegui import ui


def open_document(path: Path) -> None:
    if not path.is_file():
        ui.notify(f"Файл не найден: {path.name}", type="warning")
        return
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["open", str(path)], check=False)
    elif system == "Windows":
        os.startfile(str(path))  # type: ignore[attr-defined]
    else:
        subprocess.run(["xdg-open", str(path)], check=False)

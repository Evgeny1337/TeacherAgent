from pathlib import Path

from schemas.lesson_session import LessonSession

LAST_SESSION_FILE = Path(__file__).parent / "last_session.json"


def save(session: LessonSession) -> None:
    LAST_SESSION_FILE.write_text(session.model_dump_json())


def clear() -> None:
    if LAST_SESSION_FILE.exists():
        LAST_SESSION_FILE.unlink()


def load() -> LessonSession | None:
    if not LAST_SESSION_FILE.exists():
        return None
    return LessonSession.model_validate_json(LAST_SESSION_FILE.read_text())

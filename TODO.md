# TODO — intake / DeepSeek

## Pending

- [ ] **Хрупкость ответа модели**  
  Pydantic жёстко валидирует enum’ы (`cefr_level`, `lesson_type`, `readiness`).  
  Любой `"B1.2"` / `"Grammar"` / неожиданный формат → `ValidationError`.  
  Сделать позже: retry / нормализация / более мягкий parse.

- [ ] **Один OpenAI-клиент**  
  Сейчас `OpenAI(...)` создаётся на каждый вызов в `fetch_lesson_info`.  
  Вынести наружу или сделать ленивый singleton.

- [ ] **`LessonInfoRequest` почти не используется**  
  В пайплайне живёт `TeacherRequest` → `fetch_lesson_info(...)`.  
  Либо внедрить request-схему в LLM-слой, либо убрать, чтобы не плодить две правды.

## Done

- [x] Выровнять `missing_info` между комментарием, моделью и `SYSTEM_PROMPT`

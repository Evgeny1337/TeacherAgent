import json
from typing import Any

from plan.generate.llm import (
    REVISE_PATCH_PROMPT,
    REVISE_ROUTER_PROMPT,
    SYSTEM_PROMPT,
    chat_json,
)
from plan.schemas.plan_shema import LessonPlan
from plan.schemas.revise_schema import LessonPlanPatch, ReviseRoute, ReviseScope

_HEADER_FIELDS = {
    "lesson.date",
    "lesson.level",
    "lesson.teacher",
    "lesson.aim",
    "lesson.sub_aim",
    "lesson.homework_summary",
}


def _dump(data: Any) -> str:
    return data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)


def _block(name: str, data: Any) -> str:
    return f"{name}:\n{_dump(data)}\n"


def _parse_index(target: str, prefix: str) -> int | None:
    if not target.startswith(prefix):
        return None
    head = target.removeprefix(prefix).split(".", 1)[0]
    return int(head) if head.isdigit() else None


def build_outline(plan: LessonPlan) -> dict[str, Any]:
    return {
        "lesson": plan.lesson.model_dump(),
        "stages": [
            {"i": i, **s.model_dump(include={"title", "time_interaction"})}
            for i, s in enumerate(plan.stages)
        ],
        "handouts": [
            {"i": i, **h.model_dump(include={"title", "mode"})}
            for i, h in enumerate(plan.handouts or [])
        ],
        "worksheet": (
            plan.worksheet.model_dump(include={"title"}) if plan.worksheet else None
        ),
    }


def build_context(plan: LessonPlan, targets: list[str]) -> dict[str, Any]:
    context: dict[str, Any] = {
        "lesson.level": plan.lesson.level,
        "lesson.aim": plan.lesson.aim,
        "lesson.sub_aim": plan.lesson.sub_aim,
    }
    indexes = {
        i
        for t in targets
        if (i := _parse_index(t, "stages.")) is not None
    }
    for idx in sorted(indexes):
        context[f"stages.{idx}.neighbors"] = [
            {"i": j, "title": plan.stages[j].title}
            for j in (idx - 1, idx + 1)
            if 0 <= j < len(plan.stages)
        ]
    return context


def build_fragments(plan: LessonPlan, targets: list[str]) -> dict[str, Any]:
    fragments: dict[str, Any] = {}
    handouts = plan.handouts or []

    for target in dict.fromkeys(targets):
        if target.startswith("lesson."):
            field = target.split(".", 1)[1]
            fragments.setdefault("lesson", {})[field] = getattr(plan.lesson, field)
            continue

        if (idx := _parse_index(target, "stages.")) is not None:
            key = f"stages.{idx}"
            if key not in fragments and 0 <= idx < len(plan.stages):
                fragments[key] = plan.stages[idx].model_dump()
            continue

        if (idx := _parse_index(target, "handouts.")) is not None:
            key = f"handouts.{idx}"
            if key not in fragments and 0 <= idx < len(handouts):
                fragments[key] = handouts[idx].model_dump()
            continue

        if target.startswith("worksheet") and "worksheet" not in fragments:
            fragments["worksheet"] = (
                plan.worksheet.model_dump() if plan.worksheet else None
            )

    return fragments


def apply_patch(plan: LessonPlan, patch: LessonPlanPatch) -> LessonPlan:
    data = plan.model_dump()
    raw = patch.model_dump(exclude_unset=True)

    for path, value in raw.pop("set", {}).items():
        section, field = path.split(".", 1)
        data[section][field] = value

    for key, row in raw.pop("stages", {}).items():
        idx = int(key)
        if not 0 <= idx < len(data["stages"]):
            raise ValueError(f"stages.{key} out of range")
        data["stages"][idx] = row

    handout_rows = raw.pop("handouts", None)
    if handout_rows:
        handouts = list(data.get("handouts") or [])
        for key, row in sorted(handout_rows.items(), key=lambda item: int(item[0])):
            idx = int(key)
            if idx < len(handouts):
                handouts[idx] = row
            else:
                handouts.append(row)
        data["handouts"] = handouts

    if "worksheet" in raw:
        data["worksheet"] = raw["worksheet"]

    return LessonPlan.model_validate(data)


def _normalize_route(plan: LessonPlan, route: ReviseRoute) -> ReviseRoute:
    handouts_len = len(plan.handouts or [])
    stages_len = len(plan.stages)
    targets: list[str] = []

    for target in route.targets:
        if (idx := _parse_index(target, "handouts.")) is not None:
            if idx < handouts_len:
                targets.append(target)
            elif plan.worksheet is None:
                targets.append("worksheet")
            continue

        if (idx := _parse_index(target, "stages.")) is not None:
            if idx < stages_len:
                targets.append(target)
            continue

        targets.append(target)

    return route.model_copy(update={"targets": list(dict.fromkeys(targets))})


def _needs_patch(route: ReviseRoute) -> bool:
    if route.scope is ReviseScope.RIPPLE:
        return True
    return any(
        t.split(".", 1)[0] in {"stages", "handouts", "worksheet"}
        or (t in _HEADER_FIELDS and t not in route.set)
        for t in route.targets
    )


def _route_plan(api_key: str, plan: LessonPlan, revision_notes: str) -> ReviseRoute:
    user_prompt = (
        "Route the revision. Return ReviseRoute JSON only.\n\n"
        + _block("revision_notes", revision_notes)
        + _block("outline", build_outline(plan))
    )
    return chat_json(
        api_key,
        user_prompt,
        ReviseRoute,
        system_prompt=REVISE_ROUTER_PROMPT,
        max_tokens=1024,
    )


def _patch_plan(
    api_key: str,
    plan: LessonPlan,
    route: ReviseRoute,
    revision_notes: str,
    materials: str,
    format_preferences: str,
) -> LessonPlanPatch:
    user_prompt = (
        "Patch only the requested targets. Return LessonPlanPatch JSON only.\n\n"
        + _block("revision_notes", revision_notes)
        + _block("targets", route.targets)
        + _block("scope", route.scope)
        + _block("context", build_context(plan, route.targets))
        + _block("fragments", build_fragments(plan, route.targets))
        + _block("format_preferences", format_preferences or "none")
        + _block("materials", materials or "None")
    )
    return chat_json(
        api_key,
        user_prompt,
        LessonPlanPatch,
        system_prompt=REVISE_PATCH_PROMPT,
        max_tokens=4096,
    )


def _full_revise(
    api_key: str,
    plan: LessonPlan,
    revision_notes: str,
    materials: str,
    format_preferences: str,
) -> LessonPlan:
    user_prompt = (
        "Revise the existing lesson plan JSON using revision_notes. "
        "Keep the same JSON shape and return the full updated LessonPlan.\n\n"
        + _block("revision_notes", revision_notes)
        + _block("format_preferences", format_preferences or "none")
        + _block("previous_plan", plan.model_dump_json())
        + _block("materials", materials or "None")
    )
    return chat_json(
        api_key,
        user_prompt,
        LessonPlan,
        system_prompt=SYSTEM_PROMPT,
    )


def revise_lesson_plan(
    api_key: str,
    previous_plan: LessonPlan,
    revision_notes: str,
    materials: str = "",
    format_preferences: str = "none",
) -> LessonPlan:
    route = _normalize_route(
        previous_plan,
        _route_plan(api_key, previous_plan, revision_notes),
    )
    use_full = route.scope is ReviseScope.FULL or (
        not route.set and not route.targets
    )
    if use_full:
        return _full_revise(
            api_key,
            previous_plan,
            revision_notes,
            materials,
            format_preferences,
        )

    plan = apply_patch(previous_plan, LessonPlanPatch(set=route.set))
    if not _needs_patch(route):
        return plan

    return apply_patch(
        plan,
        _patch_plan(
            api_key,
            plan,
            route,
            revision_notes,
            materials,
            format_preferences,
        ),
    )

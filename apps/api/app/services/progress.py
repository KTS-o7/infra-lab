import json
from datetime import datetime
from uuid import uuid4

from sqlmodel import select

from app.models import (
    CourseCompletion,
    HintUsage,
    MissionProgress,
    Profile,
    StepProgress,
    ValidationAttempt,
)


def _now() -> datetime:
    return datetime.utcnow()


def _mission_progress_id(mission_id: str) -> str:
    return f"local:{mission_id}"


def _step_progress_id(mission_id: str, step_id: str) -> str:
    return f"{mission_id}:{step_id}"


def _hint_usage_id(mission_id: str, hint_id: str) -> str:
    return f"{mission_id}:{hint_id}"


def _serialize_dt(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def ensure_local_profile(session) -> Profile:
    profile = session.get(Profile, "local")
    if profile:
        return profile
    profile = Profile(id="local", display_name="Local Learner", total_xp=0)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def get_progress(session, mission_id: str) -> MissionProgress | None:
    return session.exec(
        select(MissionProgress).where(MissionProgress.mission_id == mission_id)
    ).first()


def get_or_create_progress(session, mission_id: str) -> MissionProgress:
    progress = get_progress(session, mission_id)
    if progress:
        return progress
    progress = MissionProgress(
        id=_mission_progress_id(mission_id),
        mission_id=mission_id,
        status="not_started",
    )
    session.add(progress)
    session.commit()
    session.refresh(progress)
    return progress


def list_progress(session) -> list[MissionProgress]:
    return list(session.exec(select(MissionProgress)).all())


def progress_by_mission(session) -> dict[str, MissionProgress]:
    return {row.mission_id: row for row in list_progress(session)}


def completed_mission_ids(session) -> set[str]:
    return {p.mission_id for p in list_progress(session) if p.status == "completed"}


def derive_mission_status(mission, progress: MissionProgress | None, completed_ids: set[str]) -> str:
    if progress and progress.status == "completed":
        return "completed"
    if progress and progress.status == "started":
        return "started"

    if any(prereq not in completed_ids for prereq in mission.prerequisites):
        return "locked"
    return "available"


def progress_payload(progress: MissionProgress | None, status: str) -> dict:
    return {
        "status": status,
        "attempts": progress.attempts if progress else 0,
        "xpAwarded": progress.xp_awarded if progress else 0,
        "startedAt": _serialize_dt(progress.started_at if progress else None),
        "completedAt": _serialize_dt(progress.completed_at if progress else None),
    }


def step_progress_payloads(session, mission_id: str) -> list[dict]:
    rows = session.exec(
        select(StepProgress).where(StepProgress.mission_id == mission_id)
    ).all()
    payloads = []
    for row in rows:
        latest_checks = json.loads(row.latest_checks_json) if row.latest_checks_json else []
        payloads.append(
            {
                "stepId": row.step_id,
                "status": row.status,
                "lastValidatedAt": _serialize_dt(row.last_validated_at),
                "attempts": row.attempts,
                "latestChecks": latest_checks,
            }
        )
    return payloads


def step_progress_for_mission(session, mission) -> list[dict]:
    existing = {row["stepId"]: row for row in step_progress_payloads(session, mission.id)}
    payloads = []
    for step in mission.steps:
        if step.id in existing:
            payloads.append(existing[step.id])
            continue
        payloads.append(
            {
                "stepId": step.id,
                "status": "no_checks" if not step.check_ids else "not_started",
                "lastValidatedAt": None,
                "attempts": 0,
                "latestChecks": [],
            }
        )
    return payloads


def help_usage_payloads(session, mission_id: str) -> list[dict]:
    rows = session.exec(select(HintUsage).where(HintUsage.mission_id == mission_id)).all()
    return [
        {
            "hintId": row.hint_id,
            "level": row.level,
            "usedAt": _serialize_dt(row.used_at),
        }
        for row in rows
    ]


def hint_usage_for_mission(session, mission_id: str) -> list[HintUsage]:
    return list(session.exec(select(HintUsage).where(HintUsage.mission_id == mission_id)).all())


def start_mission(session, mission) -> dict:
    ensure_local_profile(session)
    completed = completed_mission_ids(session)
    if any(prereq not in completed for prereq in mission.prerequisites):
        return {"error": {"code": "MISSION_LOCKED", "message": "Mission is locked.", "details": {"missionId": mission.id}}}

    progress = get_or_create_progress(session, mission.id)
    if progress.status == "completed":
        return {"missionId": mission.id, "status": "completed"}
    if progress.status != "started":
        progress.status = "started"
        progress.started_at = progress.started_at or _now()
        progress.updated_at = _now()
        session.add(progress)
        session.commit()
    return {"missionId": mission.id, "status": "started"}


def _hint_penalty(session, mission) -> int:
    penalties = {hint.id: hint.penalty_xp for hint in mission.hints}
    rows = session.exec(select(HintUsage).where(HintUsage.mission_id == mission.id)).all()
    return sum(penalties.get(row.hint_id, 0) for row in rows)


def validate_mission(
    session,
    mission,
    checks: list,
    *,
    scope: str = "mission",
    step_id: str | None = None,
    empty_step_message: str | None = None,
) -> dict:
    ensure_local_profile(session)
    mission_id = mission.id
    progress = get_or_create_progress(session, mission_id)
    if progress.status == "not_started":
        progress.status = "started"
        progress.started_at = progress.started_at or _now()

    progress.attempts += 1
    progress.updated_at = _now()
    attempt_number = progress.attempts

    if scope == "step" and not checks:
        check_results = []
        all_passed = True
    else:
        from app.validators import run_check

        check_results = []
        all_passed = True
        for check in checks:
            result = run_check(check)
            check_results.append(result)
            if not result.get("passed"):
                all_passed = False

    session.add(
        ValidationAttempt(
            id=str(uuid4()),
            mission_id=mission_id,
            scope=scope,
            step_id=step_id,
            passed=all_passed,
            checks_json=json.dumps(check_results),
        )
    )

    if scope == "step" and step_id:
        row = session.get(StepProgress, _step_progress_id(mission_id, step_id))
        if not row:
            row = StepProgress(id=_step_progress_id(mission_id, step_id), mission_id=mission_id, step_id=step_id)
        row.attempts += 1
        if checks:
            row.status = "passed" if all_passed else "failed"
            row.latest_checks_json = json.dumps(check_results)
            row.last_validated_at = _now()
        else:
            row.status = "no_checks"
            row.latest_checks_json = json.dumps([])
            row.last_validated_at = _now()
        row.updated_at = _now()
        session.add(row)

    xp_awarded = 0
    if scope == "mission" and all_passed and progress.status != "completed":
        progress.status = "completed"
        progress.completed_at = _now()
        xp_awarded = max(0, mission.xp - _hint_penalty(session, mission))
        progress.xp_awarded = xp_awarded
        profile = ensure_local_profile(session)
        profile.total_xp = sum(p.xp_awarded for p in list_progress(session))
        profile.updated_at = _now()
        session.add(profile)

    session.add(progress)
    session.commit()

    return {
        "missionId": mission_id,
        "passed": all_passed,
        "status": progress.status,
        "xpAwarded": xp_awarded,
        "attemptNumber": attempt_number,
        "checks": check_results,
        "unlockedMissionIds": [],
        "scope": scope,
        "stepId": step_id,
    }


def reset_mission(session, mission, mode: str) -> dict:
    from app.services.reset import reset_owned_resources

    if mode not in {"resources", "progress", "resources_and_progress"}:
        return {
            "error": {
                "code": "INVALID_RESET_MODE",
                "message": "Reset mode is invalid.",
                "details": {"validModes": ["resources", "progress", "resources_and_progress"]},
            }
        }

    mission_id = mission.id
    deleted = []
    if mode in {"resources", "resources_and_progress"}:
        deleted = reset_owned_resources([resource.model_dump() for resource in mission.owned_resources])
        for step in session.exec(select(StepProgress).where(StepProgress.mission_id == mission_id)).all():
            if step.status == "passed":
                step.status = "stale"
                step.updated_at = _now()
                session.add(step)

    if mode in {"progress", "resources_and_progress"}:
        for step in session.exec(select(StepProgress).where(StepProgress.mission_id == mission_id)).all():
            session.delete(step)
        for hint in session.exec(select(HintUsage).where(HintUsage.mission_id == mission_id)).all():
            session.delete(hint)

    session.commit()
    return {"missionId": mission_id, "mode": mode, "deleted": deleted, "skipped": [], "failed": []}


def use_hint(session, mission, hint) -> dict:
    ensure_local_profile(session)
    usage = session.get(HintUsage, _hint_usage_id(mission.id, hint.id))
    if not usage:
        usage = HintUsage(
            id=_hint_usage_id(mission.id, hint.id),
            mission_id=mission.id,
            hint_id=hint.id,
            level=hint.level,
            penalty_xp=hint.penalty_xp,
        )
        session.add(usage)
        session.commit()
        session.refresh(usage)

    return {
        "hintId": hint.id,
        "title": hint.title,
        "level": hint.level,
        "text": hint.text,
        "appliesToChecks": hint.applies_to_checks,
        "penaltyXp": hint.penalty_xp,
        "usedAt": _serialize_dt(usage.used_at),
    }


def get_profile_with_progress(session) -> dict:
    profile = ensure_local_profile(session)
    progress_rows = list_progress(session)
    live_xp = sum(row.xp_awarded for row in progress_rows)
    if profile.total_xp != live_xp:
        profile.total_xp = live_xp
        profile.updated_at = _now()
        session.add(profile)
        session.commit()
    return {
        "id": profile.id,
        "displayName": profile.display_name,
        "totalXp": live_xp,
        "completedMissionIds": [row.mission_id for row in progress_rows if row.status == "completed"],
        "badges": [],
    }


def total_xp(session) -> int:
    return sum(row.xp_awarded for row in list_progress(session))


def update_course_completion_cache(session, course, progress: dict) -> None:
    row = session.exec(select(CourseCompletion).where(CourseCompletion.course_id == course.id)).first()
    if not row:
        row = CourseCompletion(id=f"course:{course.id}", course_id=course.id)
    row.status = progress["status"]
    row.required_lessons_completed = progress["requiredLessonsCompleted"]
    row.required_lessons_total = progress["requiredLessonsTotal"]
    row.required_capstones_completed = progress["requiredCapstonesCompleted"]
    row.required_capstones_total = progress["requiredCapstonesTotal"]
    row.completed_at = datetime.fromisoformat(progress["completedAt"].replace("Z", "")) if progress["completedAt"] else None
    row.updated_at = _now()
    session.add(row)
    session.commit()

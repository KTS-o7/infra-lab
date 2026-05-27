import json
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from sqlmodel import select

from app.models import (
    CapstoneScore,
    ChatMessage,
    CourseCompletion,
    HintUsage,
    LearnMoreUsage,
    MissionProgress,
    Profile,
    StepProgress,
    ValidationAttempt,
)


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _mission_progress_id(mission_id: str) -> str:
    return f"local:{mission_id}"


def _step_progress_id(mission_id: str, step_id: str) -> str:
    return f"{mission_id}:{step_id}"


def _hint_usage_id(mission_id: str, hint_id: str) -> str:
    return f"{mission_id}:{hint_id}"


def _serialize_dt(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def course_yml_hash(missions_dir: str) -> str | None:
    path = Path(missions_dir) / "course.yml"
    if not path.exists():
        return None
    return sha256(path.read_bytes()).hexdigest()


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


# REVIEW FIX (Sarang): Added learn_more_usage_for_mission to mirror hint_usage_for_mission;
# used by get_mission to populate isUsed flags without duplicating the query inline.
def learn_more_usage_for_mission(session, mission_id: str) -> list[LearnMoreUsage]:
    return list(session.exec(select(LearnMoreUsage).where(LearnMoreUsage.mission_id == mission_id)).all())


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


def _capstone_level(score: int) -> str:
    if score >= 90:
        return "production_minded"
    if score >= 75:
        return "strong"
    if score >= 60:
        return "complete"
    return "needs_repair"


def _capstone_score(session, mission, checks: list[dict], all_passed: bool, attempt_number: int) -> dict:
    check_count = len(checks)
    passed_count = sum(1 for check in checks if check.get("passed"))
    completeness = 30 if all_passed else round(30 * (passed_count / check_count)) if check_count else 0
    end_to_end = 40 if all_passed else round(40 * (passed_count / check_count)) if check_count else 0
    hints_used = len(hint_usage_for_mission(session, mission.id))
    independence = max(0, 15 - (hints_used * 3) - max(0, attempt_number - 1) * 2)
    prior_failures = session.exec(
        select(ValidationAttempt).where(
            ValidationAttempt.mission_id == mission.id,
            ValidationAttempt.scope == "mission",
            ValidationAttempt.passed == False,  # noqa: E712
        )
    ).all()
    recovery = 10 if all_passed and prior_failures else 5 if all_passed else 0
    runtime_checks = [check for check in checks if check.get("type") == "runtime_floci_available"]
    local_safety_passed = bool(runtime_checks) and all(check.get("passed") for check in runtime_checks)

    score = 0 if not local_safety_passed else min(95, completeness + end_to_end + independence + recovery)
    if not all_passed:
        score = min(score, 59)
    level = _capstone_level(score)
    dimensions = [
        {"id": "infrastructure_completeness", "label": "Infrastructure completeness", "score": completeness, "maxScore": 30},
        {"id": "end_to_end_behavior", "label": "End-to-end behavior", "score": end_to_end, "maxScore": 40},
        {"id": "independence", "label": "Independence", "score": independence, "maxScore": 15},
        {"id": "recovery", "label": "Recovery", "score": recovery, "maxScore": 10},
    ]
    return {
        "score": score,
        "level": level,
        "dimensions": dimensions,
        "localSafetyPassed": local_safety_passed,
    }


def _capstone_local_safety_passed(checks: list[dict]) -> bool:
    runtime_checks = [check for check in checks if check.get("type") == "runtime_floci_available"]
    return bool(runtime_checks) and all(check.get("passed") for check in runtime_checks)


def _persist_capstone_score(session, mission_id: str, score: dict) -> dict:
    row = session.exec(select(CapstoneScore).where(CapstoneScore.mission_id == mission_id)).first()
    if not row:
        row = CapstoneScore(id=f"capstone:{mission_id}", mission_id=mission_id)
    row.latest_score = score["score"]
    row.latest_level = score["level"]
    row.dimensions_json = json.dumps(score["dimensions"])
    row.latest_local_safety_passed = score["localSafetyPassed"]
    if row.best_score is None or score["score"] > row.best_score:
        row.best_score = score["score"]
        row.best_level = score["level"]
        row.best_local_safety_passed = score["localSafetyPassed"]
    row.updated_at = _now()
    session.add(row)
    session.flush()
    score["bestScore"] = row.best_score
    score["bestLevel"] = row.best_level
    return score


def capstone_score_payload(session, mission_id: str) -> dict | None:
    row = session.exec(select(CapstoneScore).where(CapstoneScore.mission_id == mission_id)).first()
    if not row:
        return None
    return {
        "latestScore": row.latest_score,
        "bestScore": row.best_score,
        "latestLevel": row.latest_level,
        "bestLevel": row.best_level,
        "dimensions": json.loads(row.dimensions_json) if row.dimensions_json else [],
        "localSafetyPassed": row.latest_local_safety_passed,
        "bestLocalSafetyPassed": row.best_local_safety_passed,
        "updatedAt": _serialize_dt(row.updated_at),
    }


def validate_mission(
    session,
    mission,
    checks: list,
    *,
    scope: str = "mission",
    step_id: str | None = None,
    empty_step_message: str | None = None,
    all_missions: list | None = None,
) -> dict:
    ensure_local_profile(session)
    mission_id = mission.id
    progress = get_or_create_progress(session, mission_id)
    was_completed = progress.status == "completed"
    if progress.status == "not_started":
        progress.status = "started"
        progress.started_at = progress.started_at or _now()

    progress.attempts += 1
    progress.updated_at = _now()
    attempt_number = progress.attempts

    if scope == "step" and not checks:
        check_results = []
        all_passed = True
        message = "This step has no direct proof check. Full mission validation proves it with the rest of the workflow."
    else:
        from app.validators import run_check

        check_results = []
        all_passed = True
        message = None
        for check in checks:
            result = run_check(check)
            check_results.append(result)
            if not result.get("passed"):
                all_passed = False

    is_capstone = mission.mission_type in {"module_capstone", "final_capstone"}
    capstone_gate_passed = True
    if scope == "mission" and is_capstone:
        capstone_gate_passed = _capstone_local_safety_passed(check_results)
    effective_passed = all_passed and capstone_gate_passed

    session.add(
        ValidationAttempt(
            id=str(uuid4()),
            mission_id=mission_id,
            scope=scope,
            step_id=step_id,
            passed=effective_passed,
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
    if scope == "mission" and effective_passed and progress.status != "completed":
        progress.status = "completed"
        progress.completed_at = _now()
        xp_awarded = max(0, mission.xp - _hint_penalty(session, mission))
        progress.xp_awarded = xp_awarded
        profile = ensure_local_profile(session)
        profile.total_xp = sum(p.xp_awarded for p in list_progress(session))
        profile.updated_at = _now()
        session.add(profile)

    capstone_score = None
    if scope == "mission" and is_capstone:
        capstone_score = _persist_capstone_score(
            session,
            mission_id,
            _capstone_score(session, mission, check_results, all_passed, attempt_number),
        )

    session.add(progress)
    session.commit()

    unlocked_mission_ids = []
    if scope == "mission" and effective_passed and not was_completed and all_missions:
        completed_ids = completed_mission_ids(session)
        for candidate in sorted(all_missions, key=lambda item: (item.order, item.id)):
            if candidate.id == mission_id or candidate.id in completed_ids:
                continue
            if mission_id in candidate.prerequisites and all(prereq in completed_ids for prereq in candidate.prerequisites):
                unlocked_mission_ids.append(candidate.id)

    return {
        "missionId": mission_id,
        "passed": effective_passed,
        "status": progress.status,
        "xpAwarded": xp_awarded,
        "attemptNumber": attempt_number,
        "checks": check_results,
        "unlockedMissionIds": unlocked_mission_ids,
        "scope": scope,
        "stepId": step_id,
        "message": message,
        "capstoneScore": capstone_score,
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
    summary = {"deleted": [], "skipped": [], "failed": []}
    if mode in {"resources", "resources_and_progress"}:
        summary = reset_owned_resources([resource.model_dump() for resource in mission.owned_resources])
        for step in session.exec(select(StepProgress).where(StepProgress.mission_id == mission_id)).all():
            if step.status == "passed":
                step.status = "stale"
                step.updated_at = _now()
                session.add(step)

    if mode in {"progress", "resources_and_progress"}:
        for step in session.exec(select(StepProgress).where(StepProgress.mission_id == mission_id)).all():
            if mode == "progress":
                session.delete(step)
            else:
                step.status = "stale"
                step.updated_at = _now()
                session.add(step)
        for hint in session.exec(select(HintUsage).where(HintUsage.mission_id == mission_id)).all():
            session.delete(hint)

    session.commit()
    return {"missionId": mission_id, "mode": mode, **summary}


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


def update_course_completion_cache(session, course, progress: dict, course_hash: str | None = None) -> None:
    row = session.exec(select(CourseCompletion).where(CourseCompletion.course_id == course.id)).first()
    if not row:
        row = CourseCompletion(id=f"course:{course.id}", course_id=course.id)
    row.status = progress["status"]
    row.required_lessons_completed = progress["requiredLessonsCompleted"]
    row.required_lessons_total = progress["requiredLessonsTotal"]
    row.required_capstones_completed = progress["requiredCapstonesCompleted"]
    row.required_capstones_total = progress["requiredCapstonesTotal"]
    row.course_yml_hash = course_hash
    row.completed_at = datetime.fromisoformat(progress["completedAt"].replace("Z", "")) if progress["completedAt"] else None
    row.updated_at = _now()
    session.add(row)
    session.commit()


def use_learn_more(session, mission_id: str, item_id: str, xp: int) -> dict:
    ensure_local_profile(session)
    existing = session.exec(
        select(LearnMoreUsage).where(
            LearnMoreUsage.mission_id == mission_id,
            LearnMoreUsage.item_id == item_id,
        )
    ).first()
    if existing:
        return {"missionId": mission_id, "itemId": item_id, "alreadyUsed": True, "xpAwarded": 0}

    usage = LearnMoreUsage(
        profile_id="local",
        mission_id=mission_id,
        item_id=item_id,
        xp=xp,
    )
    session.add(usage)
    session.commit()
    return {"missionId": mission_id, "itemId": item_id, "alreadyUsed": False, "xpAwarded": xp}

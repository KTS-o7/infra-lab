from app.db import get_session
from app.models import Profile, MissionProgress, HintUsage
from sqlmodel import select
from datetime import datetime

def ensure_local_profile(session) -> Profile:
    profile = session.get(Profile, "local")
    if not profile:
        profile = Profile(id="local", display_name="Local Learner", total_xp=0)
        session.add(profile)
        try:
            session.commit()
            session.refresh(profile)
        except Exception:
            session.rollback()
            profile = session.get(Profile, "local")
    return profile

def get_or_create_progress(session, mission_id: str) -> MissionProgress:
    progress = session.get(MissionProgress, ("local", mission_id))
    if not progress:
        progress = MissionProgress(profile_id="local", mission_id=mission_id, status="available")
        session.add(progress)
        session.commit()
        session.refresh(progress)
    return progress

def get_profile_with_progress(session) -> dict:
    profile = ensure_local_profile(session)
    results = session.exec(select(MissionProgress).where(MissionProgress.profile_id == "local")).all()
    completed_ids = [p.mission_id for p in results if p.status == "completed"]
    return {
        "id": profile.id,
        "display_name": profile.display_name,
        "total_xp": profile.total_xp,
        "completed_mission_ids": completed_ids,
        "badges": [],
    }

def start_mission(session, mission_id: str, mission_xp: int, prerequisites: list) -> dict:
    profile = ensure_local_profile(session)
    progress = get_or_create_progress(session, mission_id)

    if progress.status == "locked":
        return {"error": {"code": "MISSION_LOCKED", "message": "Mission is locked.", "details": {}}}

    if progress.status == "started":
        return {"missionId": mission_id, "status": "started", "startedAt": str(progress.started_at)}

    if progress.status == "completed":
        return {"missionId": mission_id, "status": "completed", "startedAt": str(progress.started_at)}

    progress.status = "started"
    progress.started_at = datetime.utcnow()
    progress.attempts = 0
    session.commit()
    return {"missionId": mission_id, "status": "started", "startedAt": str(progress.started_at)}

def validate_mission(session, mission_id: str, mission_xp: int, checks: list) -> dict:
    profile = ensure_local_profile(session)
    progress = session.get(MissionProgress, ("local", mission_id))

    if not progress or progress.status not in ("started", "completed"):
        return {"error": {"code": "MISSION_NOT_STARTED", "message": "Start this mission before validating it.", "details": {}}}

    progress.attempts += 1
    attempt_number = progress.attempts

    from app.validators import run_check
    check_results = []
    all_passed = True
    for check in checks:
        result = run_check(check)
        check_results.append(result)
        if not result.get("passed"):
            all_passed = False

    from datetime import datetime
    xp_awarded = 0
    unlocked = []

    if all_passed and progress.status != "completed":
        progress.status = "completed"
        progress.completed_at = datetime.utcnow()
        xp_awarded = mission_xp
        progress.xp_awarded = xp_awarded
        profile.total_xp += xp_awarded

    session.commit()

    return {
        "missionId": mission_id,
        "passed": all_passed,
        "status": progress.status,
        "xpAwarded": xp_awarded,
        "attemptNumber": attempt_number,
        "checks": check_results,
        "unlockedMissionIds": unlocked,
    }

def reset_mission(session, mission_id: str, mode: str, prerequisites: list) -> dict:
    from app.services.reset import reset_owned_resources
    from app.mission_loader import MissionLoader

    progress = session.get(MissionProgress, ("local", mission_id))
    if not progress:
        return {"error": {"code": "MISSION_NOT_FOUND", "message": f"Mission {mission_id} not found.", "details": {}}}

    owned = []
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)
    if mission_id in instances:
        mission_def = instances[mission_id]
        for res in mission_def.owned_resources:
            owned.append(res.model_dump())

    deleted = reset_owned_resources(owned)

    if mode == "practice":
        pass
    elif mode == "restart":
        if progress.status == "completed":
            unmet = [p for p in prerequisites if True]
            progress.status = "available"

    session.commit()
    return {"missionId": mission_id, "status": progress.status, "resourcesRemoved": deleted}

def use_hint(session, mission_id: str, hint_id: str, penalty_xp: int) -> dict:
    profile = ensure_local_profile(session)
    progress = get_or_create_progress(session, mission_id)

    existing = session.get(HintUsage, ("local", mission_id, hint_id))
    if existing:
        from app.mission_loader import MissionLoader
        instances = MissionLoader.load_missions(config.MISSIONS_DIR)
        mission = instances.get(mission_id)
        hint = next((h for h in mission.hints if h.id == hint_id), None) if mission else None
        return {
            "missionId": mission_id,
            "hint": {"id": hint_id, "title": hint.title if hint else "", "text": hint.text if hint else "", "penaltyXp": penalty_xp, "isUsed": True},
            "possibleXp": max(0, mission.xp - penalty_xp) if mission else 0,
        }

    usage = HintUsage(profile_id="local", mission_id=mission_id, hint_id=hint_id, penalty_xp=penalty_xp)
    session.add(usage)
    session.commit()

    from app.mission_loader import MissionLoader
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)
    mission = instances.get(mission_id)
    possible_xp = max(0, mission.xp - penalty_xp) if mission else 0

    return {
        "missionId": mission_id,
        "hint": {"id": hint_id, "title": "", "text": "", "penaltyXp": penalty_xp, "isUsed": True},
        "possibleXp": possible_xp,
    }
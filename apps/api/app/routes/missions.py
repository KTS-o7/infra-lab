
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

import app.config as config
from app.db import get_session
from app.mission_loader import MissionLoader
from app.models import MissionProgress, Profile
from app.services import progress as progress_service

router = APIRouter()


def _error_response(code: str, message: str, details: dict = None):
    return {"error": {"code": code, "message": message, "details": details or {}}}


def _serialize_step(step):
    return {
        "id": step.id,
        "title": step.title,
        "goal": step.goal,
        "why": step.why,
        "targetState": [
            {"label": item.label, "value": item.value} for item in step.target_state
        ],
        "action": step.action,
        "commandId": step.command_id,
        "checkIds": step.check_ids,
        "success": step.success,
        "notes": step.notes,
    }


def _mission_steps(mission):
    if mission.steps:
        return [_serialize_step(step) for step in mission.steps]

    return [
        {
            "id": command.id,
            "title": command.label,
            "goal": command.label,
            "why": None,
            "targetState": [],
            "action": "Run this command in your terminal against the local AWS sandbox.",
            "commandId": command.id,
            "checkIds": [],
            "success": None,
            "notes": None,
        }
        for command in mission.commands
    ]


@router.get("/missions")
def list_missions(session: Session = Depends(get_session)):
    progress_service.ensure_local_profile(session)
    missions = MissionLoader.get_sorted_missions()

    progress_map = {}
    results = (
        session.query(MissionProgress)
        .filter(MissionProgress.profile_id == "local")
        .all()
    )
    for p in results:
        progress_map[p.mission_id] = p

    completed_ids = set(p.mission_id for p in results if p.status == "completed")
    completed_set = completed_ids

    mission_list = []
    for m in missions:
        prog = progress_map.get(m.id)
        status = prog.status if prog else "available"

        if status == "available" and m.prerequisites:
            all_done = all(prereq in completed_set for prereq in m.prerequisites)
            if not all_done:
                status = "locked"

        mission_list.append(
            {
                "id": m.id,
                "title": m.title,
                "summary": m.summary,
                "difficulty": m.difficulty,
                "services": m.services,
                "xp": m.xp,
                "status": status,
                "prerequisites": m.prerequisites,
                "estimatedMinutes": m.estimated_minutes,
            }
        )

    return {"missions": mission_list}


@router.get("/missions/{mission_id}")
def get_mission(mission_id: str, session: Session = Depends(get_session)):
    progress_service.ensure_local_profile(session)
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)

    if mission_id not in instances:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission = instances[mission_id]
    prog = session.get(MissionProgress, ("local", mission_id))
    status = prog.status if prog else "available"

    completed_set = set(
        p.mission_id
        for p in session.query(MissionProgress)
        .filter(
            MissionProgress.profile_id == "local", MissionProgress.status == "completed"
        )
        .all()
    )

    if status == "available" and mission.prerequisites:
        all_done = all(p in completed_set for p in mission.prerequisites)
        if not all_done:
            status = "locked"

    hints_out = []
    for h in mission.hints:
        hints_out.append(
            {
                "id": h.id,
                "title": h.title,
                "isUsed": False,
                "penaltyXp": h.penalty_xp,
            }
        )

    commands_out = [
        {"id": c.id, "label": c.label, "command": c.command} for c in mission.commands
    ]
    steps_out = _mission_steps(mission)

    return {
        "mission": {
            "id": mission.id,
            "order": mission.order,
            "title": mission.title,
            "summary": mission.summary,
            "difficulty": mission.difficulty,
            "services": mission.services,
            "xp": mission.xp,
            "estimatedMinutes": mission.estimated_minutes,
            "status": status,
            "story": mission.story,
            "learningObjectives": mission.learning_objectives,
            "commands": commands_out,
            "steps": steps_out,
            "hints": hints_out,
            "progress": {
                "status": status,
                "attempts": prog.attempts if prog else 0,
                "hintsUsed": [],
                "xpAwarded": prog.xp_awarded if prog else 0,
                "startedAt": str(prog.started_at) if prog and prog.started_at else None,
                "completedAt": str(prog.completed_at)
                if prog and prog.completed_at
                else None,
            },
        }
    }

@router.post("/missions/{mission_id}/start")
def start_mission(mission_id: str, session: Session = Depends(get_session)):
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)
    if mission_id not in instances:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission = instances[mission_id]
    result = progress_service.start_mission(
        session, mission_id, mission.xp, mission.prerequisites
    )
    if "error" in result:
        raise HTTPException(status_code=409, detail=result)
    return result


@router.post("/missions/{mission_id}/validate")
def validate_mission(
    mission_id: str,
    body: dict = Body(default={}),
    session: Session = Depends(get_session),
):
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)
    if mission_id not in instances:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission = instances[mission_id]
    step_id = body.get("stepId") if body else None
    scope = "mission"

    if step_id:
        step = next((s for s in mission.steps if s.id == step_id), None)
        if not step:
            raise HTTPException(
                status_code=404,
                detail=_error_response("STEP_NOT_FOUND", "Step not found."),
            )
        selected_check_ids = set(step.check_ids)
        checks = [c.model_dump() for c in mission.checks if c.id in selected_check_ids]
        scope = "step"
        if not checks:
            result = progress_service.validate_mission(
                session,
                mission_id,
                mission.xp,
                [],
                scope=scope,
                step_id=step_id,
                empty_step_message="This step does not have validation checks yet.",
            )
            if "error" in result:
                raise HTTPException(status_code=409, detail=result)
            return result
    else:
        checks = [c.model_dump() for c in mission.checks]

    result = progress_service.validate_mission(
        session, mission_id, mission.xp, checks, scope=scope, step_id=step_id
    )
    if "error" in result:
        raise HTTPException(status_code=409, detail=result)
    return result


@router.post("/missions/{mission_id}/reset")
def reset_mission(
    mission_id: str,
    body: dict = Body(default={}),
    session: Session = Depends(get_session),
):
    mode = body.get("mode", "practice")
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)
    if mission_id not in instances:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission = instances[mission_id]
    result = progress_service.reset_mission(
        session, mission_id, mode, mission.prerequisites
    )
    if "error" in result:
        raise HTTPException(status_code=409, detail=result)
    return result


@router.post("/missions/{mission_id}/hints/{hint_id}/use")
def use_hint(mission_id: str, hint_id: str, session: Session = Depends(get_session)):
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)
    if mission_id not in instances:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission = instances[mission_id]
    hint = next((h for h in mission.hints if h.id == hint_id), None)
    if not hint:
        raise HTTPException(status_code=404, detail="Hint not found")

    result = progress_service.use_hint(session, mission_id, hint_id, hint.penalty_xp)
    return result



@router.get("/profile")
def get_profile(session: Session = Depends(get_session)):
    profile_data = progress_service.get_profile_with_progress(session)
    return {"profile": profile_data}

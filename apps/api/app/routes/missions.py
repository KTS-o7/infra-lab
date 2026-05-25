from fastapi import APIRouter, Body, Depends, HTTPException
from sqlmodel import Session
import logging

from app.db import get_session
from app.mission_loader import MissionLoader
from app.services import progress as progress_service
import app.config as config

router = APIRouter()
logger = logging.getLogger("infra_quest.missions")


def _error_response(code: str, message: str, details: dict = None):
    return {"error": {"code": code, "message": message, "details": details or {}}}


def _serialize_step(step):
    return {
        "id": step.id,
        "title": step.title,
        "goal": step.goal,
        "why": step.why,
        "targetState": [{"label": item.label, "value": item.value} for item in step.target_state],
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


def _mission_summary(mission, status: str):
    return {
        "id": mission.id,
        "order": mission.order,
        "module": mission.module,
        "submodule": mission.submodule,
        "missionType": mission.mission_type,
        "capability": mission.capability,
        "title": mission.title,
        "summary": mission.summary,
        "difficulty": mission.difficulty,
        "services": mission.services,
        "xp": mission.xp,
        "status": status,
        "required": mission.required,
        "prerequisites": mission.prerequisites,
        "estimatedMinutes": mission.estimated_minutes,
    }


def _progress_maps(session):
    progress_service.ensure_local_profile(session)
    progress_map = progress_service.progress_by_mission(session)
    completed = {mission_id for mission_id, row in progress_map.items() if row.status == "completed"}
    return progress_map, completed


def _course_payload(session):
    MissionLoader.load_missions(config.MISSIONS_DIR)
    course = MissionLoader.load_course(config.MISSIONS_DIR)
    missions = MissionLoader.get_sorted_missions()
    progress_map, completed = _progress_maps(session)
    statuses = {
        mission.id: progress_service.derive_mission_status(mission, progress_map.get(mission.id), completed)
        for mission in missions
    }

    modules = []
    capabilities = []
    total_required_lessons = total_completed_lessons = 0
    total_required_capstones = total_completed_capstones = 0

    for module in sorted(course.modules, key=lambda item: item.order):
        module_missions = [mission for mission in missions if mission.module == module.id]
        required_lessons = [m for m in module_missions if m.mission_type == "lesson" and m.required]
        required_capstones = [
            m
            for m in module_missions
            if m.mission_type in {"module_capstone", "final_capstone"} and m.required
        ]
        lessons_completed = sum(1 for m in required_lessons if statuses[m.id] == "completed")
        capstones_completed = sum(1 for m in required_capstones if statuses[m.id] == "completed")
        total_required_lessons += len(required_lessons)
        total_completed_lessons += lessons_completed
        total_required_capstones += len(required_capstones)
        total_completed_capstones += capstones_completed

        required_done = lessons_completed == len(required_lessons) and capstones_completed == len(required_capstones)
        any_started = any(statuses[m.id] in {"started", "completed"} for m in module_missions)
        any_available = any(statuses[m.id] == "available" for m in module_missions)
        if required_done and (required_lessons or required_capstones):
            module_status = "completed"
        elif any_started:
            module_status = "started"
        elif any_available:
            module_status = "available"
        else:
            module_status = "locked"

        mission_ids_for_capability = [
            m.id for m in sorted(required_lessons + required_capstones, key=lambda item: (item.order, item.id))
            if m.capability == module.capability
        ]
        if required_done and (required_lessons or required_capstones):
            capability_status = "unlocked"
        elif lessons_completed or capstones_completed:
            capability_status = "in_progress"
        else:
            capability_status = "locked"

        modules.append(
            {
                "id": module.id,
                "order": module.order,
                "title": module.title,
                "summary": module.summary,
                "required": module.required,
                "capability": module.capability,
                "capabilityLabel": module.capability_label,
                "status": module_status,
                "requiredLessonsCompleted": lessons_completed,
                "requiredLessonsTotal": len(required_lessons),
                "requiredCapstonesCompleted": capstones_completed,
                "requiredCapstonesTotal": len(required_capstones),
                "capstoneMissionId": module.capstone_mission_id,
                "capstoneRequired": module.capstone_required,
                "missions": [
                    {
                        "id": mission.id,
                        "order": mission.order,
                        "title": mission.title,
                        "missionType": mission.mission_type,
                        "required": mission.required,
                        "status": statuses[mission.id],
                    }
                    for mission in module_missions
                ],
            }
        )
        capabilities.append(
            {
                "id": module.capability,
                "label": module.capability_label,
                "status": capability_status,
                "moduleId": module.id,
                "missionIds": mission_ids_for_capability,
            }
        )

    next_mission_id = next((mission.id for mission in missions if statuses[mission.id] == "available"), None)
    any_required_started = any(
        statuses[mission.id] in {"started", "completed"}
        for mission in missions
        if mission.required and mission.mission_type == "lesson"
    )
    course_complete = (
        total_completed_lessons == total_required_lessons
        and total_completed_capstones == total_required_capstones
        and (total_required_lessons or total_required_capstones)
    )
    if course_complete:
        status = "completed"
    elif any_required_started:
        status = "in_progress"
    else:
        status = "not_started"
    completed_at = None
    if course_complete:
        completed_times = [
            progress_map[mission.id].completed_at
            for mission in missions
            if mission.id in progress_map and mission.required and progress_map[mission.id].completed_at
        ]
        completed_at = max(completed_times).isoformat() + "Z" if completed_times else None

    progress = {
        "status": status,
        "requiredLessonsCompleted": total_completed_lessons,
        "requiredLessonsTotal": total_required_lessons,
        "requiredCapstonesCompleted": total_completed_capstones,
        "requiredCapstonesTotal": total_required_capstones,
        "xp": progress_service.total_xp(session),
        "nextMissionId": next_mission_id,
        "completedAt": completed_at,
    }
    progress_service.update_course_completion_cache(
        session,
        course,
        progress,
        progress_service.course_yml_hash(config.MISSIONS_DIR),
    )
    return {
        "id": course.id,
        "title": course.title,
        "summary": course.summary,
        "progress": progress,
        "modules": modules,
        "capabilities": capabilities,
    }


@router.get("/course")
def get_course(session: Session = Depends(get_session)):
    return {"course": _course_payload(session)}


@router.get("/missions")
def list_missions(session: Session = Depends(get_session)):
    missions = MissionLoader.get_sorted_missions()
    progress_map, completed = _progress_maps(session)
    return {
        "missions": [
            _mission_summary(mission, progress_service.derive_mission_status(mission, progress_map.get(mission.id), completed))
            for mission in missions
        ]
    }


@router.get("/missions/{mission_id}")
def get_mission(mission_id: str, session: Session = Depends(get_session)):
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)
    if mission_id not in instances:
        raise HTTPException(status_code=404, detail=_error_response("MISSION_NOT_FOUND", "Mission not found."))

    mission = instances[mission_id]
    progress_map, completed = _progress_maps(session)
    prog = progress_map.get(mission_id)
    status = progress_service.derive_mission_status(mission, prog, completed)
    usages = progress_service.hint_usage_for_mission(session, mission_id)
    used_hint_ids = {usage.hint_id for usage in usages}

    hints_out = []
    for hint in mission.hints:
        item = {
            "id": hint.id,
            "title": hint.title,
            "level": hint.level,
            "appliesToChecks": hint.applies_to_checks,
            "penaltyXp": hint.penalty_xp,
            "revealed": hint.id in used_hint_ids,
        }
        if item["revealed"]:
            item["text"] = hint.text
        hints_out.append(item)

    payload = _mission_summary(mission, status)
    payload.update(
        {
            "story": mission.story,
            "motivation": getattr(mission, "motivation", None),
            "theory": getattr(mission, "theory", None),
            "thoughtProcess": getattr(mission, "thought_process", None),
            "debrief": getattr(mission, "debrief", None),
            "learningObjectives": mission.learning_objectives,
            "commands": [{"id": c.id, "label": c.label, "command": c.command} for c in mission.commands],
            "steps": _mission_steps(mission),
            "hints": hints_out,
            "stepProgress": progress_service.step_progress_for_mission(session, mission),
            "helpUsage": [
                {"hintId": usage.hint_id, "level": usage.level, "usedAt": usage.used_at.isoformat() + "Z"}
                for usage in usages
            ],
            "progress": {
                "status": status,
                "attempts": prog.attempts if prog else 0,
                "xpAwarded": prog.xp_awarded if prog else 0,
                "startedAt": prog.started_at.isoformat() + "Z" if prog and prog.started_at else None,
                "completedAt": prog.completed_at.isoformat() + "Z" if prog and prog.completed_at else None,
            },
            "capstoneScore": progress_service.capstone_score_payload(session, mission_id)
            if mission.mission_type in {"module_capstone", "final_capstone"}
            else None,
        }
    )
    return {"mission": payload}


@router.post("/missions/{mission_id}/start")
def start_mission(mission_id: str, session: Session = Depends(get_session)):
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)
    if mission_id not in instances:
        raise HTTPException(status_code=404, detail=_error_response("MISSION_NOT_FOUND", "Mission not found."))
    result = progress_service.start_mission(session, instances[mission_id])
    logger.info(
        "mission_start",
        extra={
            "event": "mission_start",
            "mission_id": mission_id,
            "status": result.get("status"),
            "error_code": result.get("error", {}).get("code"),
        },
    )
    if "error" in result:
        raise HTTPException(status_code=409, detail=result)
    return result


@router.post("/missions/{mission_id}/validate")
def validate_mission(mission_id: str, body: dict = Body(default={}), session: Session = Depends(get_session)):
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)
    if mission_id not in instances:
        raise HTTPException(status_code=404, detail=_error_response("MISSION_NOT_FOUND", "Mission not found."))
    mission = instances[mission_id]
    step_id = body.get("stepId") if body else None
    scope = "mission"
    if step_id:
        step = next((s for s in mission.steps if s.id == step_id), None)
        if not step:
            raise HTTPException(status_code=404, detail=_error_response("STEP_NOT_FOUND", "Step not found."))
        selected_check_ids = set(step.check_ids)
        checks = [c.model_dump() for c in mission.checks if c.id in selected_check_ids]
        scope = "step"
    else:
        checks = [c.model_dump() for c in mission.checks]

    result = progress_service.validate_mission(session, mission, checks, scope=scope, step_id=step_id)
    logger.info(
        "mission_validate",
        extra={
            "event": "mission_validate",
            "mission_id": mission_id,
            "scope": scope,
            "step_id": step_id,
            "passed": result.get("passed"),
            "status": result.get("status"),
            "attempt_number": result.get("attemptNumber"),
            "check_count": len(result.get("checks", [])),
            "error_code": result.get("error", {}).get("code"),
        },
    )
    if "error" in result:
        raise HTTPException(status_code=409, detail=result)
    return result


@router.post("/missions/{mission_id}/reset")
def reset_mission(mission_id: str, body: dict = Body(default={}), session: Session = Depends(get_session)):
    mode = body.get("mode", "resources")
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)
    if mission_id not in instances:
        raise HTTPException(status_code=404, detail=_error_response("MISSION_NOT_FOUND", "Mission not found."))
    result = progress_service.reset_mission(session, instances[mission_id], mode)
    logger.info(
        "mission_reset",
        extra={
            "event": "mission_reset",
            "mission_id": mission_id,
            "mode": mode,
            "deleted_count": len(result.get("deleted", [])),
            "failed_count": len(result.get("failed", [])),
            "error_code": result.get("error", {}).get("code"),
        },
    )
    if "error" in result:
        raise HTTPException(status_code=422, detail=result)
    return result


@router.post("/missions/{mission_id}/hints/{hint_id}/use")
def use_hint(mission_id: str, hint_id: str, session: Session = Depends(get_session)):
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)
    if mission_id not in instances:
        raise HTTPException(status_code=404, detail=_error_response("MISSION_NOT_FOUND", "Mission not found."))
    mission = instances[mission_id]
    hint = next((h for h in mission.hints if h.id == hint_id), None)
    if not hint:
        raise HTTPException(status_code=404, detail=_error_response("HINT_NOT_FOUND", "Hint not found."))
    result = progress_service.use_hint(session, mission, hint)
    logger.info(
        "mission_hint_use",
        extra={
            "event": "mission_hint_use",
            "mission_id": mission_id,
            "hint_id": hint_id,
            "hint_level": getattr(hint, "level", None),
            "penalty_xp": getattr(hint, "penalty_xp", None),
            "error_code": result.get("error", {}).get("code"),
        },
    )
    if "error" in result:
        raise HTTPException(status_code=409, detail=result)
    return result


@router.get("/profile")
def get_profile(session: Session = Depends(get_session)):
    profile = progress_service.ensure_local_profile(session)
    course = _course_payload(session)
    progress_map = progress_service.progress_by_mission(session)
    badges = []
    for module, capability in zip(course["modules"], course["capabilities"]):
        if capability["status"] != "unlocked":
            continue
        completed_times = [
            progress_map[mission["id"]].completed_at
            for mission in module["missions"]
            if mission["required"] and mission["id"] in progress_map and progress_map[mission["id"]].completed_at
        ]
        badges.append(
            {
                "id": capability["id"],
                "label": capability["label"],
                "moduleId": module["id"],
                "earnedAt": max(completed_times).isoformat() + "Z" if completed_times else None,
            }
        )
    live_xp = progress_service.total_xp(session)
    if profile.total_xp != live_xp:
        profile.total_xp = live_xp
        session.commit()
    return {
        "profile": {
            "id": profile.id,
            "displayName": profile.display_name,
            "totalXp": live_xp,
            "badges": badges,
            "courseProgress": course["progress"],
        }
    }

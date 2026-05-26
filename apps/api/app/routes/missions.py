import os
import subprocess

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

import app.config as config
from app.db import get_session
from app.mission_loader import MissionLoader
from app.models import (
    ChatMessage,
    HintUsage,
    LearnMoreUsage,
    MissionProgress,
    Profile,
)
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

    hints_used = {
        h.hint_id
        for h in session.query(HintUsage)
        .filter(HintUsage.profile_id == "local", HintUsage.mission_id == mission_id)
        .all()
    }

    learn_more_used = {
        l.item_id
        for l in session.query(LearnMoreUsage)
        .filter(
            LearnMoreUsage.profile_id == "local",
            LearnMoreUsage.mission_id == mission_id,
        )
        .all()
    }

    hints_out = []
    for h in mission.hints:
        hints_out.append(
            {
                "id": h.id,
                "title": h.title,
                "text": h.text if h.id in hints_used else None,
                "isUsed": h.id in hints_used,
                "penaltyXp": h.penalty_xp,
            }
        )

    learn_more_out = []
    for l in mission.learn_more:
        learn_more_out.append(
            {
                "id": l.id,
                "question": l.question,
                "answer": l.answer if l.id in learn_more_used else "???",
                "docsUrl": l.docs_url if l.id in learn_more_used else None,
                "xp": l.xp,
                "isUsed": l.id in learn_more_used,
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
            "learnMore": learn_more_out,
            "progress": {
                "status": status,
                "attempts": prog.attempts if prog else 0,
                "hintsUsed": list(hints_used),
                "learnMoreUsed": list(learn_more_used),
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


@router.post("/missions/{mission_id}/learn/{item_id}")
def use_learn_more(
    mission_id: str, item_id: str, session: Session = Depends(get_session)
):
    instances = MissionLoader.load_missions(config.MISSIONS_DIR)
    if mission_id not in instances:
        raise HTTPException(status_code=404, detail="Mission not found")

    mission = instances[mission_id]
    item = next((i for i in mission.learn_more if i.id == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Learn more item not found")

    result = progress_service.use_learn_more(session, mission_id, item_id, item.xp)
    return result


@router.get("/missions/{mission_id}/chat")
def get_chat_history(mission_id: str, session: Session = Depends(get_session)):
    messages = (
        session.query(ChatMessage)
        .filter(ChatMessage.profile_id == "local", ChatMessage.mission_id == mission_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return {
        "messages": [
            {"role": m.role, "content": m.content, "createdAt": str(m.created_at)}
            for m in messages
        ]
    }


@router.post("/missions/{mission_id}/chat")
def send_chat_message(
    mission_id: str, body: dict = Body(...), session: Session = Depends(get_session)
):
    content = body.get("message")
    if not content:
        raise HTTPException(status_code=400, detail="Message is required")

    # 1. Save user message
    user_msg = ChatMessage(
        profile_id="local", mission_id=mission_id, role="user", content=content
    )
    session.add(user_msg)
    session.commit()

    # 2. Call AI Agent
    ai_response = "I'm sorry, I couldn't process that right now."
    if config.AI_AGENT_CMD:
        try:
            # Check if we should delegate to a host bridge
            host_bridge = os.getenv("AMA_HOST_BRIDGE")
            if host_bridge:
                import requests

                # Bridge expected to be at e.g. http://host.docker.internal:8080/run
                resp = requests.post(
                    f"{host_bridge}/run",
                    json={"command": config.AI_AGENT_CMD, "prompt": content},
                    timeout=100,
                )

                if resp.status_code == 200:
                    ai_response = resp.json().get("output", ai_response)
                else:
                    ai_response = f"Bridge Error: {resp.text}"
            else:
                # Normal in-container execution
                result = subprocess.run(
                    f"{config.AI_AGENT_CMD} {content!r}",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    ai_response = result.stdout.strip()
                else:
                    ai_response = f"AI Error: {result.stderr.strip()}"
        except Exception as e:
            ai_response = f"Failed to call AI agent: {str(e)}"
    else:
        ai_response = (
            f"Echo: You said '{content}'. (No AI agent configured in AI_AGENT_CMD)"
        )

    # 3. Save AI message
    ai_msg = ChatMessage(
        profile_id="local", mission_id=mission_id, role="ai", content=ai_response
    )
    session.add(ai_msg)
    session.commit()

    return {"role": "ai", "content": ai_response, "createdAt": str(ai_msg.created_at)}


@router.get("/profile")
def get_profile(session: Session = Depends(get_session)):
    profile_data = progress_service.get_profile_with_progress(session)
    return {"profile": profile_data}

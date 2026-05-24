import textwrap

import pytest
from sqlmodel import SQLModel, Session, create_engine

from app.mission_loader import MissionLoader
from app.models import Profile, MissionProgress
from app.routes import missions as mission_routes

def test_mission_loader_schema():
    loader = MissionLoader()
    assert True


def reset_loader():
    MissionLoader._instances = {}
    MissionLoader._loaded = False


def write_mission(root, body: str):
    mission_dir = root / "demo"
    mission_dir.mkdir()
    (mission_dir / "mission.yml").write_text(textwrap.dedent(body), encoding="utf-8")
    return mission_dir


def base_mission_yaml(extra: str = "") -> str:
    base = """
    id: demo
    order: 1
    title: Demo Mission
    summary: Demo summary.
    difficulty: beginner
    services:
      - s3
    xp: 50
    estimated_minutes: 5
    prerequisites: []
    story: Demo story.
    learning_objectives:
      - Understand demo infrastructure
    commands:
      - id: create-bucket
        label: Create bucket
        command: aws --endpoint-url http://localhost:4566 s3 mb s3://demo
    hints: []
    checks:
      - id: bucket-exists
        type: s3_bucket_exists
        bucket: demo
    owned_resources: []
    """
    return textwrap.dedent(base) + "\n" + textwrap.dedent(extra)


def test_mission_loader_accepts_authored_steps(tmp_path):
    reset_loader()
    write_mission(
        tmp_path,
        base_mission_yaml(
            """
            steps:
              - id: create-storage
                title: Create durable storage
                goal: Create the demo bucket.
                why: Apps need durable object storage for uploaded files.
                target_state:
                  - label: Bucket
                    value: demo
                action: Create the bucket in the local sandbox.
                command_id: create-bucket
                check_ids:
                  - bucket-exists
                success: The bucket exists in local S3.
            """
        ),
    )

    missions = MissionLoader.load_missions(str(tmp_path))

    step = missions["demo"].steps[0]
    assert step.id == "create-storage"
    assert step.command_id == "create-bucket"
    assert step.check_ids == ["bucket-exists"]
    assert step.target_state[0].label == "Bucket"


def test_mission_loader_rejects_step_with_unknown_command(tmp_path):
    reset_loader()
    write_mission(
        tmp_path,
        base_mission_yaml(
            """
            steps:
              - id: broken-step
                title: Broken step
                goal: Create the demo bucket.
                action: Try a missing command.
                command_id: missing-command
                check_ids:
                  - bucket-exists
            """
        ),
    )

    with pytest.raises(ValueError, match="unknown command_id"):
        MissionLoader.load_missions(str(tmp_path))


def test_mission_loader_rejects_step_with_unknown_check(tmp_path):
    reset_loader()
    write_mission(
        tmp_path,
        base_mission_yaml(
            """
            steps:
              - id: broken-step
                title: Broken step
                goal: Create the demo bucket.
                action: Create the bucket.
                command_id: create-bucket
                check_ids:
                  - missing-check
            """
        ),
    )

    with pytest.raises(ValueError, match="unknown check_id"):
        MissionLoader.load_missions(str(tmp_path))


def test_mission_detail_serializes_authored_steps(tmp_path, monkeypatch):
    reset_loader()
    write_mission(
        tmp_path,
        base_mission_yaml(
            """
            steps:
              - id: create-storage
                title: Create durable storage
                goal: Create the demo bucket.
                why: Apps need durable object storage for uploaded files.
                target_state:
                  - label: Bucket
                    value: demo
                action: Create the bucket in the local sandbox.
                command_id: create-bucket
                check_ids:
                  - bucket-exists
                success: The bucket exists in local S3.
            """
        ),
    )
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    session = make_session()

    response = mission_routes.get_mission("demo", session=session)

    assert response["mission"]["steps"] == [
        {
            "id": "create-storage",
            "title": "Create durable storage",
            "goal": "Create the demo bucket.",
            "why": "Apps need durable object storage for uploaded files.",
            "targetState": [{"label": "Bucket", "value": "demo"}],
            "action": "Create the bucket in the local sandbox.",
            "commandId": "create-bucket",
            "checkIds": ["bucket-exists"],
            "success": "The bucket exists in local S3.",
            "notes": None,
        }
    ]


def test_mission_detail_derives_fallback_steps_for_legacy_missions(tmp_path, monkeypatch):
    reset_loader()
    write_mission(tmp_path, base_mission_yaml())
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    session = make_session()

    response = mission_routes.get_mission("demo", session=session)

    assert response["mission"]["steps"][0]["id"] == "create-bucket"
    assert response["mission"]["steps"][0]["commandId"] == "create-bucket"
    assert response["mission"]["steps"][0]["checkIds"] == []


def test_step_validation_runs_only_step_checks_without_awarding_xp(tmp_path, monkeypatch):
    reset_loader()
    write_mission(
        tmp_path,
        base_mission_yaml(
            """
            checks:
              - id: bucket-exists
                type: s3_bucket_exists
                bucket: demo
              - id: object-exists
                type: s3_object_exists
                bucket: demo
                key: hello.txt
            steps:
              - id: create-storage
                title: Create durable storage
                goal: Create the demo bucket.
                action: Create the bucket in the local sandbox.
                command_id: create-bucket
                check_ids:
                  - bucket-exists
            """
        ),
    )
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    monkeypatch.setattr("app.validators.run_check", lambda check: {
        "id": check["id"],
        "type": check["type"],
        "passed": True,
        "message": f"{check['id']} passed",
    })
    session = make_session()
    session.add(Profile(id="local", display_name="Local Learner", total_xp=0))
    session.add(MissionProgress(profile_id="local", mission_id="demo", status="started"))
    session.commit()

    response = mission_routes.validate_mission(
        "demo",
        body={"stepId": "create-storage"},
        session=session,
    )
    progress = session.get(MissionProgress, ("local", "demo"))
    profile = session.get(Profile, "local")

    assert response["scope"] == "step"
    assert response["stepId"] == "create-storage"
    assert response["xpAwarded"] == 0
    assert [check["id"] for check in response["checks"]] == ["bucket-exists"]
    assert progress.status == "started"
    assert profile.total_xp == 0


def test_step_validation_without_checks_returns_actionable_failure(tmp_path, monkeypatch):
    reset_loader()
    write_mission(
        tmp_path,
        base_mission_yaml(
            """
            steps:
              - id: explain-only
                title: Explain only
                goal: Read the context.
                action: Review the mission context.
                command_id: create-bucket
                check_ids: []
            """
        ),
    )
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    session = make_session()
    session.add(Profile(id="local", display_name="Local Learner", total_xp=0))
    session.add(MissionProgress(profile_id="local", mission_id="demo", status="started"))
    session.commit()

    response = mission_routes.validate_mission(
        "demo",
        body={"stepId": "explain-only"},
        session=session,
    )

    assert response["scope"] == "step"
    assert response["stepId"] == "explain-only"
    assert response["passed"] is False
    assert response["xpAwarded"] == 0
    assert response["checks"] == [
        {
            "id": "explain-only",
            "type": "step_has_checks",
            "passed": False,
            "message": "This step does not have validation checks yet.",
        }
    ]


def test_reset_mission_uses_requested_mode(tmp_path, monkeypatch):
    reset_loader()
    write_mission(tmp_path, base_mission_yaml())
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    monkeypatch.setattr("app.services.reset.reset_owned_resources", lambda owned: ["s3_bucket:demo"])
    session = make_session()
    session.add(Profile(id="local", display_name="Local Learner", total_xp=50))
    session.add(MissionProgress(profile_id="local", mission_id="demo", status="completed", xp_awarded=50))
    session.commit()

    response = mission_routes.reset_mission(
        "demo",
        body={"mode": "restart"},
        session=session,
    )
    progress = session.get(MissionProgress, ("local", "demo"))

    assert response["status"] == "available"
    assert response["resourcesRemoved"] == ["s3_bucket:demo"]
    assert progress.status == "available"


def make_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_all_missions_with_commands_have_authored_steps():
    """Every mission with commands must have authored steps, not fallback steps.

    This ensures no mission relies on the derived fallback step generation,
    which produces empty checkIds and generic actions that don't teach the
    learner anything meaningful.
    """
    import pathlib
    missions_dir = pathlib.Path("missions")
    if not missions_dir.exists():
        pytest.skip("missions directory not found")

    loader = MissionLoader()
    loader._loaded = False
    loader._instances = {}

    loaded = loader.load_missions(str(missions_dir))

    failures = []
    for mission_id, mission in loaded.items():
        if mission.commands and not mission.steps:
            failures.append(f"Mission {mission_id} has {len(mission.commands)} commands but no authored steps")
        elif mission.commands and mission.steps:
            fallback_steps = [
                s for s in mission.steps
                if s.check_ids == [] or s.action == "Run this command in your terminal against the local AWS sandbox."
            ]
            if fallback_steps:
                failures.append(f"Mission {mission_id} has {len(fallback_steps)} steps that look like fallbacks (empty check_ids or generic action)")

    assert failures == [], f"Missions with issues:\n" + "\n".join(failures)

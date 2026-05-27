import textwrap

import pytest
from sqlmodel import SQLModel, Session, create_engine, select

from app import db
from app.mission_loader import MissionLoader
from app.models import (
    CapstoneScore,
    CourseCompletion,
    HintUsage,
    MissionProgress,
    Profile,
    SchemaMigration,
    StepProgress,
    ValidationAttempt,
)
from app.routes import missions as mission_routes
from app.routes import runtime as runtime_routes

def test_mission_loader_schema():
    assert MissionLoader is not None


def reset_loader():
    MissionLoader._instances = {}
    MissionLoader._course = None
    MissionLoader._loaded = False


def get_progress(session, mission_id: str):
    return session.exec(select(MissionProgress).where(MissionProgress.mission_id == mission_id)).first()


def write_mission(root, body: str):
    mission_dir = root / "demo"
    mission_dir.mkdir()
    (mission_dir / "mission.yml").write_text(textwrap.dedent(body), encoding="utf-8")
    return mission_dir


def write_course(root, body: str = ""):
    course = body or """
    id: infra-quest
    title: Infra Quest
    summary: Demo course.
    modules:
      - id: legacy
        order: 1
        title: Legacy
        required: true
        capability: storage
        capability_label: Storage
        summary: Legacy module.
        capstone_mission_id: null
        capstone_required: false
    """
    (root / "course.yml").write_text(textwrap.dedent(course), encoding="utf-8")


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
        command: aws --endpoint-url http://floci:4566 s3 mb s3://demo
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
    progress = get_progress(session, "demo")
    profile = session.get(Profile, "local")

    assert response["scope"] == "step"
    assert response["stepId"] == "create-storage"
    assert response["xpAwarded"] == 0
    assert [check["id"] for check in response["checks"]] == ["bucket-exists"]
    assert progress.status == "started"
    assert profile.total_xp == 0
    attempts = session.exec(select(ValidationAttempt).where(ValidationAttempt.mission_id == "demo")).all()
    step_progress = session.exec(select(StepProgress).where(StepProgress.mission_id == "demo")).first()
    assert attempts[0].scope == "step"
    assert step_progress.status == "passed"
    assert step_progress.attempts == 1


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
    assert response["passed"] is True
    assert response["xpAwarded"] == 0
    assert response["checks"] == []


def test_reset_mission_uses_requested_mode(tmp_path, monkeypatch):
    reset_loader()
    write_mission(tmp_path, base_mission_yaml())
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    monkeypatch.setattr(
        "app.services.reset.reset_owned_resources",
        lambda owned: {
            "deleted": [{"type": "s3_bucket", "id": "demo", "status": "deleted"}],
            "skipped": [],
            "failed": [],
        },
    )
    session = make_session()
    session.add(Profile(id="local", display_name="Local Learner", total_xp=50))
    session.add(MissionProgress(profile_id="local", mission_id="demo", status="completed", xp_awarded=50))
    session.commit()

    response = mission_routes.reset_mission("demo", body={"mode": "resources"}, session=session)
    progress = get_progress(session, "demo")

    assert response["mode"] == "resources"
    assert response["deleted"] == [{"type": "s3_bucket", "id": "demo", "status": "deleted"}]
    assert progress.status == "completed"


def test_reset_mission_progress_mode_preserves_completed_history(tmp_path, monkeypatch):
    reset_loader()
    write_mission(tmp_path, base_mission_yaml())
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    session = make_session()
    session.add(Profile(id="local", display_name="Local Learner", total_xp=50))
    session.add(MissionProgress(profile_id="local", mission_id="demo", status="completed", xp_awarded=50))
    session.add(StepProgress(mission_id="demo", step_id="create-storage", status="passed"))
    session.add(HintUsage(mission_id="demo", hint_id="h1", penalty_xp=10))
    session.add(
        ValidationAttempt(
            mission_id="demo",
            scope="mission",
            passed=True,
            checks_json="[]",
        )
    )
    session.commit()

    response = mission_routes.reset_mission("demo", body={"mode": "progress"}, session=session)
    profile = session.get(Profile, "local")
    progress = get_progress(session, "demo")

    assert response["mode"] == "progress"
    assert progress.status == "completed"
    assert progress.xp_awarded == 50
    assert session.exec(select(StepProgress).where(StepProgress.mission_id == "demo")).first() is None
    assert session.exec(select(HintUsage).where(HintUsage.mission_id == "demo")).first() is None
    assert session.exec(select(ValidationAttempt).where(ValidationAttempt.mission_id == "demo")).first() is not None
    assert profile.total_xp == 50


def test_reset_mission_requires_explicit_mode(tmp_path, monkeypatch):
    reset_loader()
    write_mission(tmp_path, base_mission_yaml())
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    session = make_session()

    with pytest.raises(Exception) as exc:
        mission_routes.reset_mission("demo", body={}, session=session)

    assert exc.value.status_code == 422
    assert exc.value.detail["error"]["code"] == "INVALID_RESET_MODE"


def test_course_endpoint_derives_progress_from_missions(tmp_path, monkeypatch):
    reset_loader()
    write_mission(tmp_path, base_mission_yaml())
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    session = make_session()

    response = mission_routes.get_course(session=session)

    assert response["course"]["progress"]["requiredLessonsTotal"] == 1
    assert response["course"]["progress"]["nextMissionId"] == "demo"
    assert response["course"]["modules"][0]["missions"][0]["status"] == "available"


def test_validate_locked_mission_returns_conflict(tmp_path, monkeypatch):
    reset_loader()
    write_mission(
        tmp_path,
        base_mission_yaml(
            """
            prerequisites:
              - missing-prerequisite
            """
        ),
    )
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    session = make_session()

    with pytest.raises(Exception) as exc:
        mission_routes.validate_mission("demo", body={}, session=session)

    assert exc.value.status_code == 409
    assert exc.value.detail["error"]["code"] == "MISSION_LOCKED"


def test_validation_reports_directly_unlocked_missions(tmp_path, monkeypatch):
    reset_loader()
    write_mission(tmp_path, base_mission_yaml())
    next_dir = tmp_path / "next"
    next_dir.mkdir()
    (next_dir / "mission.yml").write_text(
        textwrap.dedent(
            """
            id: next
            order: 2
            module: legacy
            submodule: next-step
            mission_type: lesson
            required: true
            title: Next Mission
            summary: Next summary.
            difficulty: beginner
            services:
              - s3
            xp: 50
            estimated_minutes: 5
            prerequisites:
              - demo
            story: Next story.
            learning_objectives:
              - Understand mission unlocks
            commands: []
            hints: []
            checks: []
            owned_resources: []
            """
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    monkeypatch.setattr("app.validators.run_check", lambda check: {
        "id": check["id"],
        "type": check["type"],
        "passed": True,
        "message": "passed",
    })
    session = make_session()

    response = mission_routes.validate_mission("demo", body={}, session=session)
    repeat = mission_routes.validate_mission("demo", body={}, session=session)

    assert response["unlockedMissionIds"] == ["next"]
    assert repeat["unlockedMissionIds"] == []


def test_course_endpoint_stores_course_yml_hash(tmp_path, monkeypatch):
    reset_loader()
    write_course(tmp_path)
    write_mission(tmp_path, base_mission_yaml())
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    session = make_session()

    mission_routes.get_course(session=session)

    row = session.exec(select(CourseCompletion).where(CourseCompletion.course_id == "infra-quest")).first()
    assert row.course_yml_hash is not None
    assert len(row.course_yml_hash) == 64


def test_hint_use_is_idempotent_and_reveals_detail(tmp_path, monkeypatch):
    reset_loader()
    write_mission(
        tmp_path,
        base_mission_yaml(
            """
            hints:
              - id: endpoint-required
                title: Check endpoint
                level: nudge
                applies_to_checks:
                  - bucket-exists
                text: Use the local endpoint.
                penalty_xp: 5
            """
        ),
    )
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    session = make_session()

    first = mission_routes.use_hint("demo", "endpoint-required", session=session)
    second = mission_routes.use_hint("demo", "endpoint-required", session=session)
    detail = mission_routes.get_mission("demo", session=session)
    usages = session.exec(select(HintUsage).where(HintUsage.mission_id == "demo")).all()

    assert first["usedAt"] == second["usedAt"]
    assert len(usages) == 1
    assert detail["mission"]["hints"][0]["revealed"] is True
    assert detail["mission"]["hints"][0]["text"] == "Use the local endpoint."


def test_hint_use_rejects_locked_mission(tmp_path, monkeypatch):
    reset_loader()
    write_mission(
        tmp_path,
        base_mission_yaml(
            """
            prerequisites:
              - cloud-explorer
            hints:
              - id: endpoint-required
                title: Check endpoint
                level: nudge
                applies_to_checks:
                  - bucket-exists
                text: Use the local endpoint.
                penalty_xp: 5
            """
        ),
    )
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    session = make_session()

    with pytest.raises(Exception) as exc:
        mission_routes.use_hint("demo", "endpoint-required", session=session)

    assert exc.value.status_code == 409
    assert exc.value.detail["error"]["code"] == "MISSION_LOCKED"
    assert session.exec(select(HintUsage).where(HintUsage.mission_id == "demo")).first() is None


def test_capstone_validation_persists_score_and_returns_payload(tmp_path, monkeypatch):
    reset_loader()
    write_mission(
        tmp_path,
        base_mission_yaml(
            """
            mission_type: module_capstone
            checks:
              - id: floci-available
                type: runtime_floci_available
              - id: bucket-exists
                type: s3_bucket_exists
                bucket: demo
            """
        ),
    )
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    monkeypatch.setattr("app.validators.run_check", lambda check: {
        "id": check["id"],
        "type": check["type"],
        "passed": True,
        "message": "passed",
    })
    session = make_session()

    response = mission_routes.validate_mission("demo", body={}, session=session)
    row = session.exec(select(CapstoneScore).where(CapstoneScore.mission_id == "demo")).first()
    detail = mission_routes.get_mission("demo", session=session)

    assert response["capstoneScore"]["score"] >= 90
    assert response["capstoneScore"]["localSafetyPassed"] is True
    assert response["capstoneScore"]["bestScore"] == response["capstoneScore"]["score"]
    assert row.best_level == response["capstoneScore"]["level"]
    assert row.latest_local_safety_passed is True
    assert detail["mission"]["capstoneScore"]["bestScore"] == row.best_score
    assert detail["mission"]["capstoneScore"]["localSafetyPassed"] is True
    # REVIEW FIX (Sarang): Removed duplicate assertion — capstoneScore was serialized
    # twice (once inside "progress" and once at top-level). The inner copy was a double
    # DB query with no added value. Only the top-level "capstoneScore" field is used
    # by the frontend. The assertion above already covers this.


def test_capstone_local_safety_blocks_completion(tmp_path, monkeypatch):
    reset_loader()
    write_mission(
        tmp_path,
        base_mission_yaml(
            """
            mission_type: module_capstone
            checks:
              - id: floci-available
                type: runtime_floci_available
            """
        ),
    )
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    monkeypatch.setattr("app.validators.run_check", lambda check: {
        "id": check["id"],
        "type": check["type"],
        "passed": False,
        "message": "local runtime unavailable",
    })
    session = make_session()

    response = mission_routes.validate_mission("demo", body={}, session=session)
    progress = get_progress(session, "demo")

    assert response["passed"] is False
    assert response["capstoneScore"]["localSafetyPassed"] is False
    assert progress.status == "started"


def test_capstone_missing_local_safety_check_blocks_completion(tmp_path, monkeypatch):
    reset_loader()
    write_mission(
        tmp_path,
        base_mission_yaml(
            """
            mission_type: module_capstone
            checks:
              - id: bucket-exists
                type: s3_bucket_exists
                bucket: demo
            """
        ),
    )
    monkeypatch.setattr(mission_routes.config, "MISSIONS_DIR", str(tmp_path))
    monkeypatch.setattr("app.validators.run_check", lambda check: {
        "id": check["id"],
        "type": check["type"],
        "passed": True,
        "message": "passed",
    })
    session = make_session()

    response = mission_routes.validate_mission("demo", body={}, session=session)
    progress = get_progress(session, "demo")

    assert response["passed"] is False
    assert response["capstoneScore"]["localSafetyPassed"] is False
    assert progress.status == "started"


def test_runtime_status_reports_diagnostic_issues(monkeypatch):
    class BrokenSession:
        def get(self, *args, **kwargs):
            raise RuntimeError("db unavailable")

    class BrokenClient:
        def list_buckets(self):
            raise RuntimeError("floci unavailable")

    monkeypatch.setattr(runtime_routes, "get_client", lambda service: BrokenClient())

    response = runtime_routes.runtime_status(session=BrokenSession())

    assert response["floci"]["status"] == "offline"
    assert response["database"]["status"] == "offline"
    assert {issue["id"] for issue in response["issues"]} >= {"floci_unreachable", "database_unreachable"}


def test_mission_rename_migration_is_idempotent(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    monkeypatch.setattr(db, "engine", engine)
    with Session(engine) as session:
        session.add(MissionProgress(mission_id="serverless-boss", status="completed", attempts=2, xp_awarded=80))
        session.add(ValidationAttempt(mission_id="serverless-boss", scope="mission", passed=True, checks_json="[]"))
        session.add(StepProgress(id="serverless-boss:deploy", mission_id="serverless-boss", step_id="deploy"))
        session.add(HintUsage(id="serverless-boss:hint", mission_id="serverless-boss", hint_id="hint"))
        session.add(CapstoneScore(mission_id="serverless-boss", best_score=92, best_level="production_minded"))
        session.commit()

    db._run_mission_rename_migration()
    db._run_mission_rename_migration()

    with Session(engine) as session:
        assert get_progress(session, "serverless-boss") is None
        assert get_progress(session, "launchdesk-compose-capstone").status == "completed"
        assert session.exec(select(ValidationAttempt)).first().mission_id == "launchdesk-compose-capstone"
        assert session.exec(select(StepProgress)).first().mission_id == "launchdesk-compose-capstone"
        assert session.exec(select(HintUsage)).first().mission_id == "launchdesk-compose-capstone"
        assert session.exec(select(CapstoneScore)).first().mission_id == "launchdesk-compose-capstone"
        assert session.get(SchemaMigration, "0002_rename_serverless_boss_capstone") is not None


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

    assert failures == [], "Missions with issues:\n" + "\n".join(failures)

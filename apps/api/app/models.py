from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import UTC, datetime
from uuid import uuid4

def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Profile(SQLModel, table=True):
    __tablename__ = "profile"

    id: str = Field(primary_key=True, default="local")
    display_name: str = Field(default="Local Learner")
    total_xp: int = Field(default=0)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class MissionProgress(SQLModel, table=True):
    __tablename__ = "mission_progress"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    profile_id: str = Field(default="local")
    mission_id: str = Field(index=True, unique=True)
    status: str = Field(default="not_started")
    attempts: int = Field(default=0)
    xp_awarded: int = Field(default=0)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ValidationAttempt(SQLModel, table=True):
    __tablename__ = "validation_attempt"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    mission_id: str = Field(nullable=False)
    scope: str = Field(nullable=False)
    step_id: Optional[str] = Field(default=None)
    passed: bool = Field(nullable=False)
    checks_json: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utc_now)


class StepProgress(SQLModel, table=True):
    __tablename__ = "step_progress"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    mission_id: str = Field(index=True)
    step_id: str = Field(index=True)
    status: str = Field(default="not_started")
    attempts: int = Field(default=0)
    latest_checks_json: Optional[str] = Field(default=None)
    last_validated_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class HintUsage(SQLModel, table=True):
    __tablename__ = "hint_usage"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    mission_id: str = Field(index=True)
    hint_id: str = Field(index=True)
    level: str = Field(default="nudge")
    penalty_xp: int = Field(default=0)
    used_at: datetime = Field(default_factory=utc_now)


class LearnMoreUsage(SQLModel, table=True):
    __tablename__ = "learn_more_usage"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    profile_id: str = Field(default="local", index=True)
    mission_id: str = Field(index=True)
    item_id: str = Field(index=True)
    xp: int = Field(default=0)
    used_at: datetime = Field(default_factory=utc_now)


class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_message"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    profile_id: str = Field(default="local", index=True)
    mission_id: str = Field(index=True)
    role: str = Field(nullable=False)  # "user" | "ai"
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=utc_now)


class CapstoneScore(SQLModel, table=True):
    __tablename__ = "capstone_score"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    mission_id: str = Field(index=True, unique=True)
    latest_score: Optional[int] = Field(default=None)
    best_score: Optional[int] = Field(default=None)
    latest_level: Optional[str] = Field(default=None)
    best_level: Optional[str] = Field(default=None)
    dimensions_json: Optional[str] = Field(default=None)
    latest_local_safety_passed: Optional[bool] = Field(default=None)
    best_local_safety_passed: Optional[bool] = Field(default=None)
    updated_at: datetime = Field(default_factory=utc_now)


class CourseCompletion(SQLModel, table=True):
    __tablename__ = "course_completion"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    course_id: str = Field(index=True, unique=True)
    status: str = Field(default="not_started")
    required_lessons_completed: int = Field(default=0)
    required_lessons_total: int = Field(default=0)
    required_capstones_completed: int = Field(default=0)
    required_capstones_total: int = Field(default=0)
    course_yml_hash: Optional[str] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    updated_at: datetime = Field(default_factory=utc_now)


class SchemaMigration(SQLModel, table=True):
    __tablename__ = "schema_migration"

    version: str = Field(primary_key=True)
    applied_at: datetime = Field(default_factory=utc_now)
    description: str = Field(nullable=False)

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Profile(SQLModel, table=True):
    __tablename__ = "profiles"

    id: str = Field(primary_key=True, default="local")
    display_name: str = Field(default="Local Learner")
    total_xp: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MissionProgress(SQLModel, table=True):
    __tablename__ = "mission_progress"

    profile_id: str = Field(primary_key=True)
    mission_id: str = Field(primary_key=True)
    status: str = Field(default="available")
    attempts: int = Field(default=0)
    xp_awarded: int = Field(default=0)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ValidationAttempt(SQLModel, table=True):
    __tablename__ = "validation_attempts"

    id: str = Field(primary_key=True)
    profile_id: str = Field(nullable=False)
    mission_id: str = Field(nullable=False)
    attempt_number: int = Field(nullable=False)
    passed: bool = Field(nullable=False)
    checks_json: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class HintUsage(SQLModel, table=True):
    __tablename__ = "hint_usages"

    profile_id: str = Field(primary_key=True)
    mission_id: str = Field(primary_key=True)
    hint_id: str = Field(primary_key=True)
    penalty_xp: int = Field(nullable=False)
    used_at: datetime = Field(default_factory=datetime.utcnow)

class Badge(SQLModel, table=True):
    __tablename__ = "badges"

    profile_id: str = Field(primary_key=True)
    badge_id: str = Field(primary_key=True)
    title: str = Field(nullable=False)
    awarded_at: datetime = Field(default_factory=datetime.utcnow)
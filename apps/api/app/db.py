from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
from sqlalchemy import inspect
import app.config as config
from app.models import SchemaMigration

engine = create_engine(
    config.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if config.DATABASE_URL.startswith("sqlite") else {},
)

def create_db_and_tables():
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "CREATE TABLE IF NOT EXISTS schema_migration "
            "(version VARCHAR PRIMARY KEY, applied_at DATETIME NOT NULL, description VARCHAR NOT NULL)"
        )
        _prepare_legacy_tables(conn)
    SQLModel.metadata.create_all(engine)
    run_migrations()


def _prepare_legacy_tables(conn):
    inspector = inspect(conn)
    tables = set(inspector.get_table_names())
    if "profiles" in tables and "profile" not in tables:
        conn.exec_driver_sql("ALTER TABLE profiles RENAME TO profiles_legacy")
    if "validation_attempts" in tables and "validation_attempt" not in tables:
        conn.exec_driver_sql("ALTER TABLE validation_attempts RENAME TO validation_attempts_legacy")
    if "hint_usages" in tables and "hint_usage" not in tables:
        conn.exec_driver_sql("ALTER TABLE hint_usages RENAME TO hint_usages_legacy")
    if "mission_progress" in tables:
        columns = {column["name"] for column in inspector.get_columns("mission_progress")}
        if "id" not in columns:
            conn.exec_driver_sql("ALTER TABLE mission_progress RENAME TO mission_progress_legacy")


def run_migrations():
    inspector = inspect(engine)
    existing = set(inspector.get_table_names())
    if "schema_migration" not in existing:
        return
    with engine.begin() as conn:
        _copy_legacy_rows(conn, existing)
    with Session(engine) as session:
        migration = session.get(SchemaMigration, "0001_sqlmodel_foundation")
        if not migration:
            session.add(SchemaMigration(version="0001_sqlmodel_foundation", description="Create SQLModel persistence foundation"))
            session.commit()


def _copy_legacy_rows(conn, existing_tables: set[str]):
    tables = set(inspect(conn).get_table_names()) | existing_tables
    if "profiles_legacy" in tables:
        conn.exec_driver_sql(
            """
            INSERT OR IGNORE INTO profile (id, display_name, total_xp, created_at, updated_at)
            SELECT id, display_name, total_xp, created_at, updated_at FROM profiles_legacy
            """
        )
    if "mission_progress_legacy" in tables:
        conn.exec_driver_sql(
            """
            INSERT OR IGNORE INTO mission_progress
                (id, mission_id, status, attempts, xp_awarded, started_at, completed_at, created_at, updated_at)
            SELECT
                lower(hex(randomblob(16))),
                mission_id,
                CASE WHEN status IN ('started', 'completed') THEN status ELSE 'not_started' END,
                attempts,
                xp_awarded,
                started_at,
                completed_at,
                created_at,
                updated_at
            FROM mission_progress_legacy
            """
        )
    if "validation_attempts_legacy" in tables:
        conn.exec_driver_sql(
            """
            INSERT OR IGNORE INTO validation_attempt
                (id, mission_id, scope, step_id, passed, checks_json, created_at)
            SELECT id, mission_id, 'mission', NULL, passed, checks_json, created_at
            FROM validation_attempts_legacy
            """
        )
    if "hint_usages_legacy" in tables:
        conn.exec_driver_sql(
            """
            INSERT OR IGNORE INTO hint_usage (id, mission_id, hint_id, level, used_at)
            SELECT lower(hex(randomblob(16))), mission_id, hint_id, 'nudge', used_at
            FROM hint_usages_legacy
            """
        )

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

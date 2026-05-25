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
    _run_mission_rename_migration()


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

def _run_mission_rename_migration():
    version = "0002_rename_serverless_boss_capstone"
    with Session(engine) as session:
        if session.get(SchemaMigration, version):
            return

    old_id = "serverless-boss"
    new_id = "launchdesk-compose-capstone"
    with engine.begin() as conn:
        tables = set(inspect(conn).get_table_names())
        if "mission_progress" in tables:
            old_progress = conn.exec_driver_sql(
                "SELECT * FROM mission_progress WHERE mission_id = ?", (old_id,)
            ).mappings().first()
            new_progress = conn.exec_driver_sql(
                "SELECT * FROM mission_progress WHERE mission_id = ?", (new_id,)
            ).mappings().first()
            if old_progress and new_progress:
                status_rank = {"not_started": 0, "started": 1, "completed": 2}
                status = max(
                    [old_progress["status"], new_progress["status"]],
                    key=lambda value: status_rank.get(value, 0),
                )
                conn.exec_driver_sql(
                    """
                    UPDATE mission_progress
                    SET status = ?,
                        attempts = ?,
                        xp_awarded = ?,
                        started_at = COALESCE(started_at, ?),
                        completed_at = COALESCE(completed_at, ?),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE mission_id = ?
                    """,
                    (
                        status,
                        (old_progress["attempts"] or 0) + (new_progress["attempts"] or 0),
                        max(old_progress["xp_awarded"] or 0, new_progress["xp_awarded"] or 0),
                        old_progress["started_at"],
                        old_progress["completed_at"],
                        new_id,
                    ),
                )
                conn.exec_driver_sql("DELETE FROM mission_progress WHERE mission_id = ?", (old_id,))
            elif old_progress:
                conn.exec_driver_sql(
                    "UPDATE mission_progress SET mission_id = ?, updated_at = CURRENT_TIMESTAMP WHERE mission_id = ?",
                    (new_id, old_id),
                )

        if "capstone_score" in tables:
            old_score = conn.exec_driver_sql(
                "SELECT * FROM capstone_score WHERE mission_id = ?", (old_id,)
            ).mappings().first()
            new_score = conn.exec_driver_sql(
                "SELECT * FROM capstone_score WHERE mission_id = ?", (new_id,)
            ).mappings().first()
            if old_score and new_score:
                old_best = old_score["best_score"] if old_score["best_score"] is not None else -1
                new_best = new_score["best_score"] if new_score["best_score"] is not None else -1
                best_source = old_score if old_best > new_best else new_score
                conn.exec_driver_sql(
                    """
                    UPDATE capstone_score
                    SET latest_score = COALESCE(latest_score, ?),
                        latest_level = COALESCE(latest_level, ?),
                        best_score = ?,
                        best_level = ?,
                        dimensions_json = COALESCE(dimensions_json, ?),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE mission_id = ?
                    """,
                    (
                        old_score["latest_score"],
                        old_score["latest_level"],
                        best_source["best_score"],
                        best_source["best_level"],
                        old_score["dimensions_json"],
                        new_id,
                    ),
                )
                conn.exec_driver_sql("DELETE FROM capstone_score WHERE mission_id = ?", (old_id,))
            elif old_score:
                conn.exec_driver_sql(
                    "UPDATE capstone_score SET mission_id = ?, updated_at = CURRENT_TIMESTAMP WHERE mission_id = ?",
                    (new_id, old_id),
                )

        for table in ("validation_attempt", "step_progress", "hint_usage"):
            if table in tables:
                conn.exec_driver_sql(f"UPDATE {table} SET mission_id = ? WHERE mission_id = ?", (new_id, old_id))

    with Session(engine) as session:
        session.add(
            SchemaMigration(
                version=version,
                description="Rename serverless-boss progress records to launchdesk-compose-capstone",
            )
        )
        session.commit()

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

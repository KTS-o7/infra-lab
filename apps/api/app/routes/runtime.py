from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import UTC, datetime
from app.db import get_session
import app.config as config
from app.aws_client import get_client

router = APIRouter()

@router.get("/runtime/status")
def runtime_status(session: Session = Depends(get_session)):
    floci_online = True
    issues = []
    try:
        s3 = get_client("s3")
        s3.list_buckets()
    except Exception as exc:
        floci_online = False
        issues.append(
            {
                "id": "floci_unreachable",
                "severity": "error",
                "component": "floci",
                "message": "Local AWS emulator is not reachable.",
                "detail": str(exc.__class__.__name__),
            }
        )

    db_online = True
    try:
        from app.models import Profile
        session.get(Profile, "local")
    except Exception as exc:
        db_online = False
        issues.append(
            {
                "id": "database_unreachable",
                "severity": "error",
                "component": "database",
                "message": "Local progress database is not reachable.",
                "detail": str(exc.__class__.__name__),
            }
        )

    local_only = config.get_local_only_status()
    if not config.AWS_ENDPOINT_URL:
        issues.append(
            {
                "id": "local_endpoint_missing",
                "severity": "error",
                "component": "localOnly",
                "message": "Local AWS endpoint is not configured.",
                "detail": "AWS_ENDPOINT_URL is empty.",
            }
        )

    return {
        "api": {"status": "online"},
        "floci": {
            "status": "online" if floci_online else "offline",
            "endpoint": config.AWS_ENDPOINT_URL,
            "checkedAt": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        },
        "database": {"status": "online" if db_online else "offline"},
        "localOnly": local_only,
        "issues": issues,
    }

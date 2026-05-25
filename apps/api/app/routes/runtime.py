from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_session
import app.config as config
from app.aws_client import get_client

router = APIRouter()

@router.get("/runtime/status")
def runtime_status(session: Session = Depends(get_session)):
    floci_online = True
    try:
        s3 = get_client("s3")
        s3.list_buckets()
    except Exception:
        floci_online = False

    db_online = True
    try:
        from app.models import Profile
        session.get(Profile, "local")
    except Exception:
        db_online = False

    return {
        "api": {"status": "online"},
        "floci": {
            "status": "online" if floci_online else "offline",
            "endpoint": config.AWS_ENDPOINT_URL,
            "checkedAt": "2026-05-23T00:00:00Z",
        },
        "database": {"status": "online" if db_online else "offline"},
        "localOnly": {"status": "enforced", "endpoint": config.AWS_ENDPOINT_URL},
    }
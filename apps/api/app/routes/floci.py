from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_session

router = APIRouter()

@router.get("/floci/s3/bucket")
def floci_s3_test(session: Session = Depends(get_session)):
    return {"status": "ok"}
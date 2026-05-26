import os
from pathlib import Path

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "test")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/data/lab.db")
MISSIONS_DIR = os.getenv("MISSIONS_DIR", "/app/missions")

_local_only_violation = False
_violation_reason = ""

if not AWS_ENDPOINT_URL:
    _local_only_violation = True
    _violation_reason = "AWS_ENDPOINT_URL is not set"

if _local_only_violation:
    raise RuntimeError(f"LOCAL_ONLY_VIOLATION: {_violation_reason}")

_forbidden_patterns = ["amazonaws.com", "https://aws"]
for pattern in _forbidden_patterns:
    if pattern in AWS_ENDPOINT_URL.lower():
        raise RuntimeError(
            f"LOCAL_ONLY_VIOLATION: endpoint contains forbidden pattern '{pattern}'"
        )

REAL_AWS_KEY_PATTERNS = ["AKIA", "ABIA", "ACCA", "ASIA"]
for key in REAL_AWS_KEY_PATTERNS:
    if AWS_ACCESS_KEY_ID.startswith(key) and AWS_ACCESS_KEY_ID != "test":
        raise RuntimeError(
            f"LOCAL_ONLY_VIOLATION: suspicious real AWS key pattern detected"
        )


def get_local_only_status() -> dict:
    return {
        "status": "enforced",
        "endpoint": AWS_ENDPOINT_URL,
    }


def get_floci_endpoint() -> str:
    return AWS_ENDPOINT_URL

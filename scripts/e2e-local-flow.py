#!/usr/bin/env python3
"""Run a browserless learner flow against the local Compose stack."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from urllib import request
from urllib.error import URLError


API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
FLOCI_URL = os.environ.get("FLOCI_URL", "http://localhost:4566").rstrip("/")


def get_json(path: str) -> dict:
    with request.urlopen(f"{API_URL}{path}", timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(path: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload or {}).encode("utf-8")
    req = request.Request(
        f"{API_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_api() -> None:
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            health = get_json("/health")
            if health.get("status") == "ok":
                return
        except (URLError, TimeoutError, OSError):
            time.sleep(2)
    raise RuntimeError(f"API did not become reachable at {API_URL}")


def aws_cli(*args: str) -> None:
    command = ["aws", "--endpoint-url", FLOCI_URL, *args]
    env = {
        **os.environ,
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
        "AWS_DEFAULT_REGION": "us-east-1",
    }
    subprocess.run(command, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def assert_status(mission_id: str, expected: str) -> None:
    mission = get_json(f"/missions/{mission_id}")["mission"]
    actual = mission["status"]
    if actual != expected:
        raise AssertionError(f"{mission_id} status expected {expected}, got {actual}")


def reset_progress() -> None:
    missions = get_json("/missions")["missions"]
    for mission in reversed(missions):
        post_json(f"/missions/{mission['id']}/reset", {"mode": "resources_and_progress"})


def main() -> int:
    wait_for_api()
    reset_progress()

    runtime = get_json("/runtime/status")
    if runtime["floci"]["status"] != "online" or runtime.get("issues"):
        raise AssertionError(f"Runtime is not clean: {runtime}")

    course = get_json("/course")["course"]
    if course["progress"]["nextMissionId"] != "cloud-explorer":
        raise AssertionError(f"Unexpected first mission: {course['progress']['nextMissionId']}")

    orientation = post_json("/missions/cloud-explorer/validate")
    if not orientation["passed"] or orientation["status"] != "completed":
        raise AssertionError(f"Orientation did not complete: {orientation}")

    assert_status("s3-first-bucket", "available")
    post_json("/missions/s3-first-bucket/start")

    aws_cli("s3", "mb", "s3://starter-bucket")
    step_one = post_json("/missions/s3-first-bucket/validate", {"stepId": "create-storage-boundary"})
    if not step_one["passed"]:
        raise AssertionError(f"S3 bucket step failed: {step_one}")

    with open("/tmp/infra-quest-hello.txt", "w", encoding="utf-8") as f:
        f.write("Hello from local AWS")
    aws_cli("s3", "cp", "/tmp/infra-quest-hello.txt", "s3://starter-bucket/hello.txt")

    step_two = post_json("/missions/s3-first-bucket/validate", {"stepId": "store-welcome-object"})
    if not step_two["passed"]:
        raise AssertionError(f"S3 object step failed: {step_two}")

    completed = post_json("/missions/s3-first-bucket/validate")
    if not completed["passed"] or completed["status"] != "completed" or completed["xpAwarded"] <= 0:
        raise AssertionError(f"S3 mission did not complete: {completed}")

    profile = get_json("/profile")["profile"]
    if profile["totalXp"] < 150:
        raise AssertionError(f"Profile XP did not persist expected awards: {profile}")

    course_after = get_json("/course")["course"]
    if course_after["progress"]["requiredLessonsCompleted"] < 2:
        raise AssertionError(f"Course progress did not update: {course_after['progress']}")

    print("PASS: local learner e2e flow completed orientation and storage")
    return 0


if __name__ == "__main__":
    sys.exit(main())

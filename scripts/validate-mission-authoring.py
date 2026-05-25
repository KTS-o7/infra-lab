#!/usr/bin/env python3
"""Release-strict mission authoring validator."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
MISSIONS_DIR = ROOT / "missions"

BASE_FIELDS = {
    "id",
    "order",
    "module",
    "submodule",
    "mission_type",
    "required",
    "title",
    "summary",
    "difficulty",
    "services",
    "xp",
    "estimated_minutes",
    "prerequisites",
    "story",
}
CURRICULUM_FIELDS = {"capability", "motivation", "theory", "thought_process", "debrief"}
STEP_FIELDS = {"id", "title", "goal", "target_state", "action", "check_ids", "success"}
LOCAL_ENDPOINTS = ("http://localhost:4566", "http://floci:4566")
REMOTE_AWS_RE = re.compile(r"https?://[^\s\"']*amazonaws\.com|amazonaws\.com")
CREATE_PATTERNS = {
    "s3_bucket": (re.compile(r"\bs3\s+mb\s+s3://([^\s/]+)"), "bucket"),
    "s3_object": (re.compile(r"\bs3\s+cp\s+\S+\s+s3://([^\s/]+)/([^\s]+)"), "bucket_key"),
    "sqs_queue": (re.compile(r"\bsqs\s+create-queue\b.*?--queue-name\s+([^\s]+)"), "queue_name"),
    "sns_topic": (re.compile(r"\bsns\s+create-topic\b.*?--name\s+([^\s]+)"), "topic_name"),
    "dynamodb_table": (re.compile(r"\bdynamodb\s+create-table\b.*?--table-name\s+([^\s]+)"), "table_name"),
    "lambda_function": (re.compile(r"\blambda\s+create-function\b.*?--function-name\s+([^\s]+)"), "function_name"),
    "apigateway_api": (re.compile(r"\bapigatewayv2\s+create-api\b.*?--name\s+([^\s]+)"), "api_name"),
}
CHECK_RESOURCE_FIELDS = ("bucket", "key", "queue_name", "topic_name", "table_name", "function_name", "api_name", "route", "body", "value")
ACTION_VERBS = {
    "add",
    "call",
    "check",
    "confirm",
    "create",
    "deploy",
    "get",
    "inspect",
    "integrate",
    "invoke",
    "list",
    "locate",
    "package",
    "publish",
    "put",
    "receive",
    "send",
    "store",
    "subscribe",
    "test",
    "upload",
    "verify",
    "wire",
}


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_blank(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def text(value: Any) -> str:
    return str(value or "").strip()


def add(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def owned_resource_keys(resources: list[dict[str, Any]]) -> set[tuple[Any, ...]]:
    keys: set[tuple[Any, ...]] = set()
    for resource in resources:
        rtype = resource.get("type")
        if rtype == "none":
            keys.add(("none",))
        elif rtype == "s3_bucket":
            keys.add((rtype, resource.get("bucket")))
        elif rtype == "s3_object":
            keys.add((rtype, resource.get("bucket"), resource.get("key")))
        elif rtype == "sqs_queue":
            keys.add((rtype, resource.get("queue_name")))
        elif rtype == "sns_topic":
            keys.add((rtype, resource.get("topic_name")))
        elif rtype == "dynamodb_table":
            keys.add((rtype, resource.get("table_name")))
        elif rtype == "lambda_function":
            keys.add((rtype, resource.get("function_name")))
        elif rtype == "apigateway_api":
            keys.add((rtype, resource.get("api_name")))
    return keys


def created_resource_keys(commands: list[dict[str, Any]]) -> set[tuple[Any, ...]]:
    keys: set[tuple[Any, ...]] = set()
    for command in commands:
        body = text(command.get("command"))
        for rtype, (pattern, shape) in CREATE_PATTERNS.items():
            match = pattern.search(body)
            if not match:
                continue
            if shape == "bucket_key":
                keys.add((rtype, match.group(1), match.group(2)))
            else:
                keys.add((rtype, match.group(1)))
    return keys


def check_local_command(path: Path, command: dict[str, Any], errors: list[str]) -> None:
    command_id = command.get("id", "<missing id>")
    body = text(command.get("command"))
    if REMOTE_AWS_RE.search(body):
        add(errors, path, f"command {command_id} references a real AWS endpoint")
    if re.search(r"\baws\b", body) and "--endpoint-url" not in body:
        add(errors, path, f"command {command_id} uses aws without --endpoint-url")
    if "--endpoint-url" in body and not any(endpoint in body for endpoint in LOCAL_ENDPOINTS):
        add(errors, path, f"command {command_id} uses a non-local endpoint")
    first_word = text(command.get("label")).split(" ", 1)[0].lower()
    if first_word not in ACTION_VERBS:
        add(errors, path, f"command {command_id} label should start with an action verb")


def validate_mission(path: Path) -> list[str]:
    errors: list[str] = []
    mission = load_yaml(path)
    if not isinstance(mission, dict):
        return [f"{path.relative_to(ROOT)}: mission.yml must contain a mapping"]

    mission_id = mission.get("id", path.parent.name)
    for field in sorted(BASE_FIELDS | CURRICULUM_FIELDS):
        if field == "prerequisites":
            missing = mission.get(field) is None
        else:
            missing = is_blank(mission.get(field))
        if missing:
            add(errors, path, f"{mission_id} missing release-strict field: {field}")

    commands = mission.get("commands") or []
    checks = mission.get("checks") or []
    steps = mission.get("steps") or []
    hints = mission.get("hints") or []
    owned = mission.get("owned_resources") or []

    command_ids = {command.get("id") for command in commands}
    check_ids = {check.get("id") for check in checks}
    step_check_ids: set[str] = set()

    for command in commands:
        if is_blank(command.get("id")) or is_blank(command.get("label")) or is_blank(command.get("command")):
            add(errors, path, f"{mission_id} has a command missing id, label, or command")
            continue
        check_local_command(path, command, errors)

    if commands and not steps:
        add(errors, path, f"{mission_id} has commands but no authored steps")

    for step in steps:
        step_id = step.get("id", "<missing id>")
        for field in sorted(STEP_FIELDS):
            if is_blank(step.get(field)):
                add(errors, path, f"step {step_id} missing authoring field: {field}")
        if step.get("command_id") and step.get("command_id") not in command_ids:
            add(errors, path, f"step {step_id} references unknown command_id {step.get('command_id')}")
        for check_id in step.get("check_ids") or []:
            if check_id not in check_ids:
                add(errors, path, f"step {step_id} references unknown check_id {check_id}")
            step_check_ids.add(check_id)

        target_blob = " ".join(text(item.get("value")) for item in step.get("target_state") or [] if isinstance(item, dict))
        proof_blob = " ".join(
            text(check.get(field))
            for check in checks
            if check.get("id") in set(step.get("check_ids") or [])
            for field in CHECK_RESOURCE_FIELDS
            if check.get(field) is not None
        )
        if target_blob and proof_blob:
            proof_tokens = [token for token in re.split(r"[^A-Za-z0-9#/_:.-]+", proof_blob) if len(token) >= 3]
            if proof_tokens and not any(token in target_blob for token in proof_tokens):
                add(errors, path, f"step {step_id} target_state does not appear to map to its proof checks")

    unused_checks = check_ids - step_check_ids
    if unused_checks:
        add(errors, path, f"{mission_id} has checks not referenced by any step: {', '.join(sorted(unused_checks))}")

    for hint in hints:
        hint_id = hint.get("id", "<missing id>")
        if hint.get("level") not in {"nudge", "diagnosis", "repair"}:
            add(errors, path, f"hint {hint_id} must use level nudge, diagnosis, or repair")
        for check_id in hint.get("applies_to_checks") or []:
            if check_id not in check_ids:
                add(errors, path, f"hint {hint_id} references unknown check_id {check_id}")
    if check_ids:
        levels = {hint.get("level") for hint in hints}
        missing_levels = {"nudge", "diagnosis", "repair"} - levels
        if missing_levels:
            add(errors, path, f"{mission_id} missing staged hint levels: {', '.join(sorted(missing_levels))}")

    if created_resource_keys(commands) and ("none",) in owned_resource_keys(owned):
        add(errors, path, f"{mission_id} creates resources but declares owned_resources type none")
    missing_owned = created_resource_keys(commands) - owned_resource_keys(owned)
    if missing_owned:
        readable = ", ".join("/".join(str(part) for part in key if part) for key in sorted(missing_owned))
        add(errors, path, f"{mission_id} missing owned_resources for created resources: {readable}")

    if mission.get("mission_type") in {"module_capstone", "final_capstone"}:
        if len(commands) >= len(steps):
            add(errors, path, f"{mission_id} capstone should provide reduced command guidance: fewer commands than steps")
        if not any(is_blank(step.get("command_id")) for step in steps):
            add(errors, path, f"{mission_id} capstone should leave at least one step without a command_id")

    if len(text(mission.get("theory")).split()) >= len(text(mission.get("story")).split()) + len(text(mission.get("thought_process")).split()):
        add(errors, path, f"{mission_id} theory should stay shorter than the surrounding build context")
    thought = text(mission.get("thought_process")).lower()
    if not any(marker in thought for marker in ("instead", "rather than", "tradeoff", "avoid", "not ")):
        add(errors, path, f"{mission_id} thought_process should include a tradeoff or rejected alternative")

    return errors


def main() -> int:
    paths = sorted(MISSIONS_DIR.glob("*/mission.yml"))
    errors: list[str] = []
    for path in paths:
        errors.extend(validate_mission(path))

    if errors:
        print("FAIL: mission authoring validation found issues")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"PASS: mission authoring validation passed for {len(paths)} missions")
    return 0


if __name__ == "__main__":
    sys.exit(main())

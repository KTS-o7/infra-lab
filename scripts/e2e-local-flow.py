#!/usr/bin/env python3
"""Run a browserless learner flow against the local Compose stack."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from urllib import request
from urllib.error import URLError


API_URL = os.environ.get("API_URL", "http://localhost:8000").rstrip("/")
FLOCI_URL = os.environ.get("FLOCI_URL", "http://localhost:4566").rstrip("/")
ROOT = Path(__file__).resolve().parents[1]


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


def aws_cli_output(*args: str) -> str:
    command = ["aws", "--endpoint-url", FLOCI_URL, *args]
    env = {
        **os.environ,
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
        "AWS_DEFAULT_REGION": "us-east-1",
    }
    result = subprocess.run(command, env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()


def create_lambda_zip(source: Path) -> Path:
    tmp_dir = Path(tempfile.mkdtemp(prefix="infra-quest-lambda-"))
    archive = tmp_dir / "function.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(source, arcname=source.name)
    return archive


def create_lambda(
    function_name: str,
    source: Path,
    *,
    runtime: str = "nodejs22.x",
    environment: dict[str, str] | None = None,
) -> None:
    archive = create_lambda_zip(source)
    command = [
        "lambda",
        "create-function",
        "--function-name",
        function_name,
        "--runtime",
        runtime,
        "--handler",
        "index.handler",
        "--zip-file",
        f"fileb://{archive}",
        "--role",
        "arn:aws:iam::000000000000:role/local-lambda-role",
    ]
    if environment:
        variables = ",".join(f"{key}={value}" for key, value in environment.items())
        command.extend(["--environment", f"Variables={{{variables}}}"])
    try:
        aws_cli(*command)
    finally:
        shutil.rmtree(archive.parent, ignore_errors=True)


def mission_validate(mission_id: str) -> dict:
    result = post_json(f"/missions/{mission_id}/validate")
    if not result["passed"] or result["status"] != "completed":
        raise AssertionError(f"{mission_id} did not complete: {result}")
    return result


def step_validate(mission_id: str, step_id: str) -> dict:
    result = post_json(f"/missions/{mission_id}/validate", {"stepId": step_id})
    if not result["passed"]:
        raise AssertionError(f"{mission_id}/{step_id} failed: {result}")
    return result


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

    assert_status("lambda-tiny-function", "available")
    post_json("/missions/lambda-tiny-function/start")
    create_lambda("starter-function", ROOT / "missions/lambda-tiny-function/function/index.mjs")
    step_validate("lambda-tiny-function", "deploy-function")
    aws_cli("lambda", "invoke", "--function-name", "starter-function", "--payload", '{"name":"Local Learner"}', "/tmp/infra-quest-lambda-response.json")
    step_validate("lambda-tiny-function", "invoke-and-verify")
    mission_validate("lambda-tiny-function")

    assert_status("apigateway-http-trigger", "available")
    post_json("/missions/apigateway-http-trigger/start")
    create_lambda("starter-api-function", ROOT / "missions/apigateway-http-trigger/function/index.mjs")
    step_validate("apigateway-http-trigger", "deploy-api-function")
    aws_cli("apigatewayv2", "create-api", "--name", "starter-api", "--protocol-type", "HTTP")
    api_id = aws_cli_output("apigatewayv2", "get-apis", "--query", "Items[?Name==`starter-api`].ApiId", "--output", "text")
    step_validate("apigateway-http-trigger", "create-http-api")
    aws_cli("apigatewayv2", "create-route", "--api-id", api_id, "--route-key", "GET /hello")
    step_validate("apigateway-http-trigger", "add-hello-route")
    integration_id = aws_cli_output(
        "apigatewayv2",
        "create-integration",
        "--api-id",
        api_id,
        "--integration-type",
        "LAMBDA_PROXY",
        "--integration-uri",
        "arn:aws:lambda:us-east-1:000000000000:function:starter-api-function",
        "--payload-format",
        "1.0",
        "--query",
        "IntegrationId",
        "--output",
        "text",
    )
    route_id = aws_cli_output("apigatewayv2", "get-routes", "--api-id", api_id, "--query", "Items[?RouteKey==`GET /hello`].RouteId", "--output", "text")
    aws_cli("apigatewayv2", "update-route", "--api-id", api_id, "--route-id", route_id, "--target", f"integrations/{integration_id}")
    step_validate("apigateway-http-trigger", "wire-lambda-integration")
    mission_validate("apigateway-http-trigger")

    assert_status("dynamodb-first-table", "available")
    post_json("/missions/dynamodb-first-table/start")
    aws_cli(
        "dynamodb",
        "create-table",
        "--table-name",
        "starter-table",
        "--attribute-definitions",
        "AttributeName=pk,AttributeType=S",
        "--key-schema",
        "AttributeName=pk,KeyType=HASH",
        "--billing-mode",
        "PAY_PER_REQUEST",
    )
    step_validate("dynamodb-first-table", "create-table")
    aws_cli("dynamodb", "put-item", "--table-name", "starter-table", "--item", '{"pk":{"S":"learner#1"},"name":{"S":"Local Learner"},"level":{"N":"1"}}')
    step_validate("dynamodb-first-table", "store-record")
    mission_validate("dynamodb-first-table")

    assert_status("sqs-first-message", "available")
    post_json("/missions/sqs-first-message/start")
    aws_cli("sqs", "create-queue", "--queue-name", "starter-queue", "--attributes", "VisibilityTimeout=0")
    step_validate("sqs-first-message", "create-work-queue")
    queue_url = aws_cli_output("sqs", "get-queue-url", "--queue-name", "starter-queue", "--query", "QueueUrl", "--output", "text")
    aws_cli("sqs", "send-message", "--queue-url", queue_url, "--message-body", "first local queue message")
    step_validate("sqs-first-message", "enqueue-background-work")
    mission_validate("sqs-first-message")

    assert_status("sns-fanout", "available")
    post_json("/missions/sns-fanout/start")
    aws_cli("sns", "create-topic", "--name", "starter-topic")
    aws_cli("sqs", "create-queue", "--queue-name", "starter-fanout-queue", "--attributes", "VisibilityTimeout=0")
    topic_arn = aws_cli_output("sns", "list-topics", "--query", "Topics[?contains(TopicArn,`starter-topic`)].TopicArn", "--output", "text")
    queue_url = aws_cli_output("sqs", "get-queue-url", "--queue-name", "starter-fanout-queue", "--query", "QueueUrl", "--output", "text")
    queue_arn = aws_cli_output(
        "sqs",
        "get-queue-attributes",
        "--queue-url",
        queue_url,
        "--attribute-names",
        "QueueArn",
        "--query",
        "Attributes.QueueArn",
        "--output",
        "text",
    )
    aws_cli("sns", "subscribe", "--topic-arn", topic_arn, "--protocol", "sqs", "--notification-endpoint", queue_arn)
    aws_cli("sns", "publish", "--topic-arn", topic_arn, "--message", "local fanout works")
    step_validate("sns-fanout", "create-notification-channel")
    step_validate("sns-fanout", "create-subscriber-endpoint")
    step_validate("sns-fanout", "wire-the-subscription")
    mission_validate("sns-fanout")

    assert_status("operate-and-recover", "available")
    post_json("/missions/operate-and-recover/start")
    step_validate("operate-and-recover", "confirm-runtime-health")
    step_validate("operate-and-recover", "repair-targeted-state")
    mission_validate("operate-and-recover")

    assert_status("launchdesk-compose-capstone", "available")
    post_json("/missions/launchdesk-compose-capstone/start")
    aws_cli(
        "dynamodb",
        "create-table",
        "--table-name",
        "orders-table",
        "--attribute-definitions",
        "AttributeName=pk,AttributeType=S",
        "--key-schema",
        "AttributeName=pk,KeyType=HASH",
        "--billing-mode",
        "PAY_PER_REQUEST",
    )
    step_validate("launchdesk-compose-capstone", "create-orders-table")
    aws_cli("sqs", "create-queue", "--queue-name", "orders-queue", "--attributes", "VisibilityTimeout=0")
    step_validate("launchdesk-compose-capstone", "create-orders-queue")
    create_lambda(
        "orders-function",
        ROOT / "missions/launchdesk-compose-capstone/function/index.py",
        runtime="python3.12",
        environment={
            "AWS_ENDPOINT_URL": "http://floci:4566",
            "AWS_ACCESS_KEY_ID": "test",
            "AWS_SECRET_ACCESS_KEY": "test",
            "AWS_DEFAULT_REGION": "us-east-1",
        },
    )
    step_validate("launchdesk-compose-capstone", "deploy-orders-function")
    aws_cli("apigatewayv2", "create-api", "--name", "orders-api", "--protocol-type", "HTTP")
    orders_api_id = aws_cli_output("apigatewayv2", "get-apis", "--query", "Items[?Name==`orders-api`].ApiId", "--output", "text")
    step_validate("launchdesk-compose-capstone", "create-orders-api")
    aws_cli("apigatewayv2", "create-route", "--api-id", orders_api_id, "--route-key", "POST /orders")
    step_validate("launchdesk-compose-capstone", "add-orders-route")
    orders_integration_id = aws_cli_output(
        "apigatewayv2",
        "create-integration",
        "--api-id",
        orders_api_id,
        "--integration-type",
        "LAMBDA_PROXY",
        "--integration-uri",
        "arn:aws:lambda:us-east-1:000000000000:function:orders-function",
        "--payload-format",
        "1.0",
        "--query",
        "IntegrationId",
        "--output",
        "text",
    )
    orders_route_id = aws_cli_output("apigatewayv2", "get-routes", "--api-id", orders_api_id, "--query", "Items[?RouteKey==`POST /orders`].RouteId", "--output", "text")
    aws_cli("apigatewayv2", "update-route", "--api-id", orders_api_id, "--route-id", orders_route_id, "--target", f"integrations/{orders_integration_id}")
    step_validate("launchdesk-compose-capstone", "wire-orders-integration")
    capstone = mission_validate("launchdesk-compose-capstone")
    if not capstone.get("capstoneScore") or not capstone["capstoneScore"].get("localSafetyPassed"):
        raise AssertionError(f"Capstone score did not include a passing local safety gate: {capstone}")

    profile = get_json("/profile")["profile"]
    if profile["totalXp"] < 1050:
        raise AssertionError(f"Profile XP did not persist expected awards: {profile}")

    course_after = get_json("/course")["course"]
    if course_after["progress"]["requiredLessonsCompleted"] != course_after["progress"]["requiredLessonsTotal"]:
        raise AssertionError(f"Course progress did not update: {course_after['progress']}")
    if course_after["progress"]["status"] != "completed":
        raise AssertionError(f"Course did not complete required lessons: {course_after['progress']}")

    print("PASS: local learner e2e flow completed all required lessons")
    return 0


if __name__ == "__main__":
    sys.exit(main())

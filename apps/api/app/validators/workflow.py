import requests

from app.aws_client import get_dynamodb_client, get_sqs_client
from app.validators.apigateway import api_url_by_name


def _post_workflow(api_name: str, route: str, request_json: dict):
    method, path = route.split(" ", 1)
    if method != "POST":
        raise ValueError("Workflow validators only support POST routes.")
    url = api_url_by_name(api_name, path)
    if not url:
        raise ValueError(f"API {api_name} was not found.")
    return requests.post(url, json=request_json, timeout=10)


def workflow_http_writes_dynamodb(api_name: str, route: str, request_json: dict, table_name: str, key: dict) -> dict:
    try:
        response = _post_workflow(api_name, route, request_json)
        if response.status_code < 200 or response.status_code >= 300:
            return {"id": "http-writes-item", "type": "workflow_http_writes_dynamodb", "passed": False, "message": f"Workflow HTTP response status {response.status_code} did not indicate success: {response.text[:200]}"}

        item = get_dynamodb_client().get_item(TableName=table_name, Key=key).get("Item")
        if item:
            return {"id": "http-writes-item", "type": "workflow_http_writes_dynamodb", "passed": True, "message": f"Workflow wrote the expected item to {table_name}."}
        return {"id": "http-writes-item", "type": "workflow_http_writes_dynamodb", "passed": False, "message": f"Workflow did not write the expected item to {table_name}."}
    except Exception:
        return {"id": "http-writes-item", "type": "workflow_http_writes_dynamodb", "passed": False, "message": "Workflow did not write the expected DynamoDB item."}


def workflow_http_sends_sqs(api_name: str, route: str, request_json: dict, queue_name: str, expected_body_contains: str) -> dict:
    try:
        response = _post_workflow(api_name, route, request_json)
        if response.status_code < 200 or response.status_code >= 300:
            return {"id": "http-sends-message", "type": "workflow_http_sends_sqs", "passed": False, "message": f"Workflow HTTP response status {response.status_code} did not indicate success: {response.text[:200]}"}

        sqs = get_sqs_client()
        queue_url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
        messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=2, VisibilityTimeout=0).get("Messages", [])
        for message in messages:
            if expected_body_contains in message.get("Body", ""):
                return {"id": "http-sends-message", "type": "workflow_http_sends_sqs", "passed": True, "message": f"Workflow sent the expected message to {queue_name}."}
        return {"id": "http-sends-message", "type": "workflow_http_sends_sqs", "passed": False, "message": f"Workflow did not send the expected message to {queue_name}."}
    except Exception:
        return {"id": "http-sends-message", "type": "workflow_http_sends_sqs", "passed": False, "message": "Workflow did not send the expected SQS message."}

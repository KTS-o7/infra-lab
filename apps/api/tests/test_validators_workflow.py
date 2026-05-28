from app.validators.workflow import workflow_http_sends_sqs, workflow_http_writes_dynamodb


def test_workflow_http_writes_dynamodb_pass(monkeypatch):
    class FakeResponse:
        status_code = 200

    class FakeDynamo:
        def get_item(self, TableName, Key):
            return {"Item": {"pk": {"S": "order#order-001"}}}

    monkeypatch.setattr("app.validators.workflow.api_url_by_name", lambda api_name, path: "http://floci/restapis/api/default/_user_request_/orders")
    monkeypatch.setattr("app.validators.workflow.requests.post", lambda url, json, timeout: FakeResponse())
    monkeypatch.setattr("app.validators.workflow.get_dynamodb_client", lambda: FakeDynamo())

    result = workflow_http_writes_dynamodb(
        "orders-api",
        "POST /orders",
        {"orderId": "order-001"},
        "orders-table",
        {"pk": {"S": "order#order-001"}},
    )

    assert result["passed"]


def test_workflow_http_writes_dynamodb_fails_when_item_missing(monkeypatch):
    class FakeResponse:
        status_code = 200

    class FakeDynamo:
        def get_item(self, TableName, Key):
            return {}

    monkeypatch.setattr("app.validators.workflow.api_url_by_name", lambda api_name, path: "http://floci/restapis/api/default/_user_request_/orders")
    monkeypatch.setattr("app.validators.workflow.requests.post", lambda url, json, timeout: FakeResponse())
    monkeypatch.setattr("app.validators.workflow.get_dynamodb_client", lambda: FakeDynamo())

    result = workflow_http_writes_dynamodb(
        "orders-api",
        "POST /orders",
        {"orderId": "order-001"},
        "orders-table",
        {"pk": {"S": "order#order-001"}},
    )

    assert not result["passed"]


def test_workflow_http_sends_sqs_pass(monkeypatch):
    class FakeResponse:
        status_code = 200

    class FakeSqs:
        def get_queue_url(self, QueueName):
            return {"QueueUrl": "http://queue"}

        def receive_message(self, QueueUrl, MaxNumberOfMessages, WaitTimeSeconds, VisibilityTimeout):
            return {"Messages": [{"Body": '{"orderId":"order-001"}'}]}

    monkeypatch.setattr("app.validators.workflow.api_url_by_name", lambda api_name, path: "http://floci/restapis/api/default/_user_request_/orders")
    monkeypatch.setattr("app.validators.workflow.requests.post", lambda url, json, timeout: FakeResponse())
    monkeypatch.setattr("app.validators.workflow.get_sqs_client", lambda: FakeSqs())

    result = workflow_http_sends_sqs("orders-api", "POST /orders", {"orderId": "order-001"}, "orders-queue", "order-001")

    assert result["passed"]


def test_workflow_http_sends_sqs_fails_when_message_missing(monkeypatch):
    class FakeResponse:
        status_code = 200

    class FakeSqs:
        def get_queue_url(self, QueueName):
            return {"QueueUrl": "http://queue"}

        def receive_message(self, QueueUrl, MaxNumberOfMessages, WaitTimeSeconds, VisibilityTimeout):
            return {"Messages": [{"Body": "other"}]}

    monkeypatch.setattr("app.validators.workflow.api_url_by_name", lambda api_name, path: "http://floci/restapis/api/default/_user_request_/orders")
    monkeypatch.setattr("app.validators.workflow.requests.post", lambda url, json, timeout: FakeResponse())
    monkeypatch.setattr("app.validators.workflow.get_sqs_client", lambda: FakeSqs())

    result = workflow_http_sends_sqs("orders-api", "POST /orders", {"orderId": "order-001"}, "orders-queue", "order-001")

    assert not result["passed"]

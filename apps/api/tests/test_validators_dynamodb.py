from app.validators.dynamodb import dynamodb_item_exists


def test_dynamodb_item_exists_pass(monkeypatch):
    class FakeClient:
        def get_item(self, TableName, Key):
            return {"Item": {"pk": {"S": "learner#1"}}}

    monkeypatch.setattr("app.validators.dynamodb.get_dynamodb_client", lambda: FakeClient())

    result = dynamodb_item_exists("starter-table", {"pk": {"S": "learner#1"}})

    assert result["passed"]


def test_dynamodb_item_exists_fails_when_item_missing(monkeypatch):
    class FakeClient:
        def get_item(self, TableName, Key):
            return {}

    monkeypatch.setattr("app.validators.dynamodb.get_dynamodb_client", lambda: FakeClient())

    result = dynamodb_item_exists("starter-table", {"pk": {"S": "missing"}})

    assert not result["passed"]

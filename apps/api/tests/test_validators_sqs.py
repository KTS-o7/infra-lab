from app.validators.sqs import sqs_queue_exists

def test_sqs_queue_exists_pass(monkeypatch):
    class FakeClient:
        def get_queue_url(self, QueueName):
            return {"QueueUrl": "http://localhost:4566/000000000000/test-queue"}
    monkeypatch.setattr("app.validators.sqs.get_sqs_client", lambda: FakeClient())
    result = sqs_queue_exists("test-queue")
    assert result["passed"]

def test_sqs_queue_exists_fail(monkeypatch):
    class FakeClient:
        def get_queue_url(self, QueueName):
            raise Exception("Queue not found")
    monkeypatch.setattr("app.validators.sqs.get_sqs_client", lambda: FakeClient())
    result = sqs_queue_exists("nonexistent-queue")
    assert not result["passed"]

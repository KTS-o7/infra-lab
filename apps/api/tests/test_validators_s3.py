import pytest
from app.validators.s3 import s3_bucket_exists, s3_object_exists, s3_object_body_equals

def test_s3_bucket_exists_pass(monkeypatch):
    class FakeClient:
        def head_bucket(self, Bucket):
            return {}
    monkeypatch.setattr("app.validators.s3.get_s3_client", lambda: FakeClient())
    result = s3_bucket_exists("test-bucket")
    assert result["passed"] == True

def test_s3_bucket_exists_fail(monkeypatch):
    class FakeClient:
        def head_bucket(self, Bucket):
            raise Exception("Not found")
    monkeypatch.setattr("app.validators.s3.get_s3_client", lambda: FakeClient())
    result = s3_bucket_exists("nonexistent-bucket")
    assert result["passed"] == False
import pytest
from app.validators.runtime import runtime_floci_available

def test_runtime_floci_available_pass(monkeypatch):
    class FakeClient:
        def list_buckets(self):
            return {"Buckets": []}
    monkeypatch.setattr("app.validators.runtime.get_client", lambda svc: FakeClient())
    result = runtime_floci_available()
    assert result["passed"] == True

def test_runtime_floci_available_fail(monkeypatch):
    class FakeClient:
        def list_buckets(self):
            raise Exception("Floci unavailable")
    monkeypatch.setattr("app.validators.runtime.get_client", lambda svc: FakeClient())
    result = runtime_floci_available()
    assert result["passed"] == False
from app.config import (
    AWS_ACCESS_KEY_ID,
    get_local_only_status,
    get_floci_endpoint,
)

def test_fake_credentials():
    assert AWS_ACCESS_KEY_ID == "test"

def test_floci_endpoint():
    endpoint = get_floci_endpoint()
    assert endpoint.startswith("http"), f"Expected http(s) endpoint, got: {endpoint}"
    assert "amazonaws.com" not in endpoint, "Endpoint must not point at real AWS"

def test_local_only_status():
    status = get_local_only_status()
    assert status["status"] == "enforced"